<template>
  <div class="homework-list">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>作业列表</h1>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建作业
          </el-button>
        </div>
      </el-header>
      <el-main>
        <el-card>
          <template #header>
            <div class="filter-bar">
              <div class="filters">
                <el-select v-model="filters.subject_id" placeholder="选择学科" clearable @change="handleSubjectChange">
                  <el-option
                    v-for="subject in subjects"
                    :key="subject.id"
                    :label="subject.name"
                    :value="subject.id"
                  />
                </el-select>
                <el-select v-model="filters.status" placeholder="作业状态" clearable @change="fetchData">
                  <el-option label="全部" value="" />
                  <el-option label="未完成" value="pending" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已批改" value="graded" />
                </el-select>
              </div>
              <el-button link @click="resetFilters">重置筛选</el-button>
            </div>
          </template>
          
          <el-table :data="homeworks" v-loading="loading" stripe>
            <el-table-column prop="title" label="作业标题" min-width="150" />
            <el-table-column prop="subject_name" label="学科" width="120" />
            <el-table-column prop="node_name" label="知识点" width="150">
              <template #default="{ row }">
                <span v-if="row.node_name">{{ row.node_name }}</span>
                <span v-else class="no-data">未指定</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="due_date" label="截止日期" width="120">
              <template #default="{ row }">
                <span v-if="row.due_date">{{ row.due_date }}</span>
                <span v-else class="no-data">无</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="goToDetail(row.id)">查看详情</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-if="total > 0"
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="total"
            layout="total, prev, pager, next"
            @current-change="fetchData"
            style="margin-top: 20px; justify-content: center;"
          />
        </el-card>
      </el-main>
    </el-container>

    <!-- 创建作业对话框 -->
    <el-dialog v-model="showCreateDialog" title="创建作业" width="600px" @close="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="作业标题" prop="title">
          <el-input v-model="form.title" placeholder="输入作业标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="学科" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="选择学科" @change="handleFormSubjectChange">
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="知识点" prop="node_id">
          <el-select v-model="form.node_id" placeholder="选择知识点" clearable :disabled="!form.subject_id">
            <el-option
              v-for="node in availableNodes"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="form.due_date"
            type="date"
            placeholder="选择截止日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="作业描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="作业的具体要求..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHomeworkStore } from '@/stores/homework'
import { useSubjectStore } from '@/stores/subjects'
import { useNodeStore } from '@/stores/nodes'
import { homeworkApi, nodeApi } from '@/api'
import { storeToRefs } from 'pinia'
import { ArrowLeft, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const homeworkStore = useHomeworkStore()
const subjectStore = useSubjectStore()
const nodeStore = useNodeStore()

const { homeworks, loading } = storeToRefs(homeworkStore)
const { subjects } = storeToRefs(subjectStore)

const filters = reactive({
  status: '',
  subject_id: route.query.subject_id || null,
  node_id: route.query.node_id || null
})

const pagination = reactive({
  page: 1,
  pageSize: 20
})

const total = ref(0)

// 创建作业相关
const showCreateDialog = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const allNodes = ref([])

const form = reactive({
  title: '',
  subject_id: null,
  node_id: null,
  due_date: '',
  description: ''
})

const rules = {
  title: [
    { required: true, message: '请输入作业标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  subject_id: [
    { required: true, message: '请选择学科', trigger: 'change' }
  ]
}

// 根据选中的学科筛选知识点
const availableNodes = computed(() => {
  if (!form.subject_id) return []
  return allNodes.value.filter(node => node.subject_id === form.subject_id)
})

onMounted(async () => {
  await subjectStore.fetchSubjects()
  
  // 加载所有知识点用于筛选
  await loadAllNodes()
  
  // 如果有预设的学科/知识点筛选条件，先加载对应的树
  if (filters.subject_id) {
    await loadNodesForSubject(filters.subject_id)
  }
  
  fetchData()
})

const loadAllNodes = async () => {
  try {
    // 从各学科的教材中加载知识点
    for (const subject of subjects.value) {
      await loadNodesForSubject(subject.id)
    }
  } catch (error) {
    console.error('加载知识点失败:', error)
  }
}

const loadNodesForSubject = async (subjectId) => {
  try {
    const books = await import('@/api').then(m => m.bookApi.list(subjectId))
    if (books && books.length > 0) {
      const tree = await nodeApi.tree(books[0].id)
      const flattenNodes = (nodes, result = []) => {
        nodes.forEach(node => {
          result.push({ id: node.id, name: node.name, subject_id: subjectId })
          if (node.children?.length) {
            flattenNodes(node.children, result)
          }
        })
        return result
      }
      const existingIds = new Set(allNodes.value.map(n => n.id))
      flattenNodes(tree).forEach(node => {
        if (!existingIds.has(node.id)) {
          allNodes.value.push(node)
          existingIds.add(node.id)
        }
      })
    }
  } catch (error) {
    console.error(`加载学科 ${subjectId} 的知识点失败:`, error)
  }
}

const fetchData = async () => {
  const params = {
    ...filters,
    page: pagination.page,
    page_size: pagination.pageSize
  }
  // 移除空值
  Object.keys(params).forEach(key => {
    if (params[key] === '' || params[key] === null) {
      delete params[key]
    }
  })
  
  const result = await homeworkStore.fetchHomeworks(params)
  if (result) {
    total.value = result.total || 0
  }
}

const handleSubjectChange = async (subjectId) => {
  filters.node_id = null
  if (subjectId) {
    await loadNodesForSubject(subjectId)
  }
  pagination.page = 1
  fetchData()
}

const resetFilters = () => {
  filters.status = ''
  filters.subject_id = null
  filters.node_id = null
  pagination.page = 1
  fetchData()
}

const goToDetail = (id) => {
  router.push(`/homeworks/${id}`)
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    completed: 'success',
    graded: 'info'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    pending: '未完成',
    completed: '已完成',
    graded: '已批改'
  }
  return texts[status] || status
}

const handleFormSubjectChange = () => {
  form.node_id = null
}

const disabledDate = (date) => {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      await homeworkApi.create({
        ...form,
        status: 'pending'
      })
      ElMessage.success('作业创建成功')
      showCreateDialog.value = false
      resetForm()
      fetchData()
    } catch (error) {
      // Error handled by interceptor
    } finally {
      submitting.value = false
    }
  })
}

const resetForm = () => {
  form.title = ''
  form.subject_id = null
  form.node_id = null
  form.due_date = ''
  form.description = ''
  formRef.value?.resetFields()
}
</script>

<style scoped>
.homework-list {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-content h1 {
  font-size: 24px;
  color: #333;
  flex: 1;
}

.el-main {
  padding: 20px;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 10px;
}

.no-data {
  color: #999;
  font-style: italic;
}
</style>