<template>
  <div class="subject-list">
    <el-container>
      <el-header>
        <h1>StudyMate - 学习复习作业管理助手</h1>
        <p class="subtitle">让作业成为学习的入口，而非学习的终点</p>
      </el-header>
      <el-main>
        <div class="action-bar">
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            创建新学科
          </el-button>
        </div>

        <el-row :gutter="20">
          <el-col
            v-for="subject in subjects"
            :key="subject.id"
            :xs="24" :sm="12" :md="8" :lg="6"
          >
            <el-card class="subject-card" shadow="hover" @click="goToBooks(subject.id)">
              <template #header>
                <div class="card-header">
                  <span>{{ subject.name }}</span>
                  <el-dropdown @command="(cmd) => handleCommand(cmd, subject)" trigger="click">
                    <el-button link :icon="MoreFilled" @click.stop />
                    <template #dropdown>
                      <el-dropdown-menu>
                        <el-dropdown-item command="edit">编辑</el-dropdown-item>
                        <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                      </el-dropdown-menu>
                    </template>
                  </el-dropdown>
                </div>
              </template>
              <div class="card-content">
                <p>{{ subject.description || '暂无描述' }}</p>
                <div class="card-stats">
                  <span><el-icon><Reading /></el-icon> {{ subject.book_count || 0 }} 教材</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="!loading && subjects.length === 0" description="暂无学科数据，点击上方按钮创建">
          <el-button type="primary" @click="showCreateDialog = true">创建第一个学科</el-button>
        </el-empty>
      </el-main>
    </el-container>

    <!-- 创建/编辑学科对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingSubject ? '编辑学科' : '创建新学科'"
      width="500px"
      @close="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="学科名称" prop="name">
          <el-input v-model="form.name" placeholder="例如：高等数学" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="学科描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="简要描述这个学科的主要内容..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          {{ editingSubject ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSubjectStore } from '@/stores/subjects'
import { subjectApi } from '@/api'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, MoreFilled, Reading } from '@element-plus/icons-vue'

const router = useRouter()
const subjectStore = useSubjectStore()
const { subjects, loading } = storeToRefs(subjectStore)

const showCreateDialog = ref(false)
const submitting = ref(false)
const editingSubject = ref(null)
const formRef = ref(null)

const form = reactive({
  name: '',
  description: ''
})

const rules = {
  name: [
    { required: true, message: '请输入学科名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 200, message: '描述不能超过 200 个字符', trigger: 'blur' }
  ]
}

onMounted(() => {
  subjectStore.fetchSubjects()
})

const goToBooks = (subjectId) => {
  router.push(`/books/${subjectId}`)
}

const handleCommand = (command, subject) => {
  if (command === 'edit') {
    editingSubject.value = subject
    form.name = subject.name
    form.description = subject.description || ''
    showCreateDialog.value = true
  } else if (command === 'delete') {
    handleDelete(subject)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    submitting.value = true
    try {
      if (editingSubject.value) {
        await subjectApi.update(editingSubject.value.id, form)
        ElMessage.success('学科更新成功')
      } else {
        await subjectApi.create(form)
        ElMessage.success('学科创建成功')
      }
      showCreateDialog.value = false
      resetForm()
      await subjectStore.fetchSubjects()
    } catch (error) {
      // Error handled by interceptor
    } finally {
      submitting.value = false
    }
  })
}

const handleDelete = async (subject) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除学科 "${subject.name}" 吗？删除后无法恢复。`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await subjectApi.delete(subject.id)
    ElMessage.success('删除成功')
    await subjectStore.fetchSubjects()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetForm = () => {
  form.name = ''
  form.description = ''
  editingSubject.value = null
  formRef.value?.resetFields()
}
</script>

<style scoped>
.subject-list {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.el-header {
  background: rgba(255, 255, 255, 0.95);
  padding: 30px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.el-header h1 {
  color: #333;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.el-main {
  padding: 40px 20px;
}

.action-bar {
  margin-bottom: 20px;
  text-align: right;
}

.subject-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: transform 0.3s;
}

.subject-card:hover {
  transform: translateY(-5px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.card-content {
  color: #666;
}

.card-stats {
  margin-top: 15px;
  display: flex;
  gap: 15px;
  color: #999;
  font-size: 14px;
}

.card-stats span {
  display: flex;
  align-items: center;
  gap: 5px;
}
</style>