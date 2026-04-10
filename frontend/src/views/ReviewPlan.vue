<template>
  <div class="review-plan">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>复习计划</h1>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建计划
          </el-button>
        </div>
      </el-header>
      <el-main>
        <!-- 状态筛选 -->
        <el-card style="margin-bottom: 20px;">
          <el-tabs v-model="activeTab" @tab-change="handleTabChange">
            <el-tab-pane label="全部" name="all" />
            <el-tab-pane label="计划中" name="planning" />
            <el-tab-pane label="进行中" name="in_progress" />
            <el-tab-pane label="已完成" name="completed" />
          </el-tabs>
        </el-card>

        <!-- 计划列表 -->
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>复习计划列表</span>
              <span class="plan-count">共 {{ plans.length }} 个计划</span>
            </div>
          </template>
          
          <el-table :data="plans" stripe v-if="plans.length > 0">
            <el-table-column prop="title" label="计划名称" min-width="150">
              <template #default="{ row }">
                <el-link type="primary" @click="goToPlanDetail(row)">{{ row.title }}</el-link>
              </template>
            </el-table-column>
            <el-table-column prop="subject_name" label="学科" width="120" />
            <el-table-column prop="exam_date" label="考试日期" width="120">
              <template #default="{ row }">
                <span v-if="row.exam_date">{{ row.exam_date }}</span>
                <span v-else class="no-data">未设置</span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" width="180">
              <template #default="{ row }">
                <el-progress 
                  :percentage="row.progress || 0" 
                  :status="getProgressStatus(row.status)"
                />
              </template>
            </el-table-column>
            <el-table-column prop="checkpoint_count" label="知识点数" width="100">
              <template #default="{ row }">
                {{ row.checkpoint_count || 0 }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="goToPlanDetail(row)">查看详情</el-button>
                <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, row)">
                  <el-button link :icon="MoreFilled" @click.stop />
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="edit">编辑</el-dropdown-item>
                      <el-dropdown-item command="start" v-if="row.status === 'planning'">开始复习</el-dropdown-item>
                      <el-dropdown-item command="complete" v-if="row.status === 'in_progress'">标记完成</el-dropdown-item>
                      <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>
          
          <el-empty v-else description="暂无复习计划" />
        </el-card>
      </el-main>
    </el-container>

    <!-- 创建/编辑计划对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="isEditing ? '编辑复习计划' : '创建复习计划'" 
      width="600px" 
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="计划名称" prop="title">
          <el-input v-model="form.title" placeholder="输入计划名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="学科" prop="subject_id">
          <el-select v-model="form.subject_id" placeholder="选择学科" @change="handleSubjectChange">
            <el-option
              v-for="subject in subjects"
              :key="subject.id"
              :label="subject.name"
              :value="subject.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="考试日期" prop="exam_date">
          <el-date-picker
            v-model="form.exam_date"
            type="date"
            placeholder="选择考试日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            :disabled-date="disabledDate"
          />
        </el-form-item>
        <el-form-item label="考试范围" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="描述需要复习的范围..."
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ isEditing ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reviewApi } from '@/api'
import { subjectApi } from '@/api'
import { storeToRefs } from 'pinia'
import { useSubjectStore } from '@/stores/subjects'
import { ArrowLeft, Plus, MoreFilled } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const subjectStore = useSubjectStore()
const { subjects } = storeToRefs(subjectStore)

const loading = ref(false)
const activeTab = ref('all')
const plans = ref([])
const showCreateDialog = ref(false)
const isEditing = ref(false)
const submitting = ref(false)
const editingId = ref(null)
const formRef = ref(null)

const form = reactive({
  title: '',
  subject_id: null,
  exam_date: '',
  description: ''
})

const rules = {
  title: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  subject_id: [
    { required: true, message: '请选择学科', trigger: 'change' }
  ]
}

onMounted(async () => {
  await subjectStore.fetchSubjects()
  fetchPlans()
})

const fetchPlans = async () => {
  loading.value = true
  try {
    const params = activeTab.value !== 'all' ? { status: activeTab.value } : {}
    plans.value = await reviewApi.getPlans(params)
  } catch (error) {
    console.error('获取复习计划失败:', error)
  } finally {
    loading.value = false
  }
}

const handleTabChange = () => {
  fetchPlans()
}

const handleSubjectChange = () => {
  // Reset other fields if needed
}

const disabledDate = (date) => {
  return date < new Date(new Date().setHours(0, 0, 0, 0))
}

const getStatusType = (status) => {
  const types = {
    planning: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    planning: '计划中',
    in_progress: '进行中',
    completed: '已完成'
  }
  return texts[status] || status
}

const getProgressStatus = (status) => {
  if (status === 'completed') return 'success'
  return ''
}

const goToPlanDetail = (plan) => {
  router.push(`/review/${plan.id}/checkpoints`)
}

const handleCommand = async (command, plan) => {
  switch (command) {
    case 'edit':
      openEditDialog(plan)
      break
    case 'start':
      await startPlan(plan)
      break
    case 'complete':
      await completePlan(plan)
      break
    case 'delete':
      await deletePlan(plan)
      break
  }
}

const openEditDialog = (plan) => {
  isEditing.value = true
  editingId.value = plan.id
  form.title = plan.title
  form.subject_id = plan.subject_id
  form.exam_date = plan.exam_date || ''
  form.description = plan.description || ''
  showCreateDialog.value = true
}

const startPlan = async (plan) => {
  try {
    await reviewApi.updatePlan(plan.id, { status: 'in_progress' })
    ElMessage.success('复习计划已启动')
    fetchPlans()
  } catch (error) {
    console.error('启动计划失败:', error)
  }
}

const completePlan = async (plan) => {
  try {
    await reviewApi.updatePlan(plan.id, { status: 'completed' })
    ElMessage.success('复习计划已标记完成')
    fetchPlans()
  } catch (error) {
    console.error('完成计划失败:', error)
  }
}

const deletePlan = async (plan) => {
  try {
    await ElMessageBox.confirm('确定要删除这个复习计划吗？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await reviewApi.deletePlan(plan.id)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除计划失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (isEditing.value) {
        await reviewApi.updatePlan(editingId.value, { ...form })
        ElMessage.success('计划更新成功')
      } else {
        await reviewApi.createPlan({
          ...form,
          status: 'planning'
        })
        ElMessage.success('计划创建成功')
      }
      showCreateDialog.value = false
      resetForm()
      fetchPlans()
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
  form.exam_date = ''
  form.description = ''
  isEditing.value = false
  editingId.value = null
  formRef.value?.resetFields()
}
</script>

<style scoped>
.review-plan {
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

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.plan-count {
  color: #909399;
  font-size: 14px;
}

.no-data {
  color: #999;
  font-style: italic;
}
</style>
