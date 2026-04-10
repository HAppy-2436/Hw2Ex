<template>
  <div class="review-checkpoints">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>{{ planTitle }}</h1>
          <el-button type="primary" @click="goToSuggestions">复习建议</el-button>
        </div>
      </el-header>
      <el-main>
        <!-- 进度概览 -->
        <el-card style="margin-bottom: 20px;">
          <div class="progress-overview">
            <div class="progress-stats">
              <div class="stat-item">
                <span class="stat-label">总体进度</span>
                <el-progress 
                  type="circle" 
                  :percentage="overallProgress" 
                  :width="80"
                  :status="getProgressStatus()"
                />
              </div>
              <div class="stat-item">
                <span class="stat-label">未开始</span>
                <span class="stat-value">{{ statusCounts.not_started || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">学习中</span>
                <span class="stat-value learning">{{ statusCounts.learning || 0 }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">已掌握</span>
                <span class="stat-value mastered">{{ statusCounts.mastered || 0 }}</span>
              </div>
            </div>
            <div class="exam-info" v-if="examDate">
              <el-icon><Calendar /></el-icon>
              <span>考试日期：{{ examDate }}</span>
              <span class="days-left">还剩 {{ daysLeft }} 天</span>
            </div>
          </div>
        </el-card>

        <!-- 知识点列表 -->
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>知识点清单</span>
              <el-select v-model="filterStatus" placeholder="筛选状态" clearable style="width: 150px;">
                <el-option label="全部" value="" />
                <el-option label="未开始" value="not_started" />
                <el-option label="学习中" value="learning" />
                <el-option label="已掌握" value="mastered" />
              </el-select>
            </div>
          </template>
          
          <div class="checkpoint-list">
            <div 
              v-for="checkpoint in filteredCheckpoints" 
              :key="checkpoint.id" 
              class="checkpoint-item"
              :class="{ mastered: checkpoint.status === 'mastered' }"
            >
              <div class="checkpoint-header">
                <div class="checkpoint-info">
                  <el-checkbox 
                    :model-value="checkpoint.status === 'mastered'" 
                    @change="(val) => updateCheckpointStatus(checkpoint, val)"
                  />
                  <span class="checkpoint-name">{{ checkpoint.node_name }}</span>
                  <el-tag size="small" :type="getStatusType(checkpoint.status)">
                    {{ getStatusText(checkpoint.status) }}
                  </el-tag>
                </div>
                <div class="checkpoint-actions">
                  <el-button link type="primary" @click="goToChat(checkpoint)">
                    <el-icon><ChatDotRound /></el-icon>
                    AI问答
                  </el-button>
                </div>
              </div>
              
              <div class="checkpoint-body">
                <!-- 掌握程度 -->
                <div class="mastery-section">
                  <span class="section-label">掌握程度：</span>
                  <el-rate
                    v-model="checkpoint.mastery_level"
                    :max="5"
                    show-text
                    :texts="['陌生', '模糊', '一般', '良好', '熟练', '精通']"
                    @change="(val) => updateMasteryLevel(checkpoint, val)"
                  />
                </div>
                
                <!-- 复习笔记 -->
                <div class="note-section">
                  <span class="section-label">复习笔记：</span>
                  <el-input
                    v-model="checkpoint.notes"
                    type="textarea"
                    :rows="2"
                    placeholder="记录学习心得..."
                    @blur="updateNotes(checkpoint)"
                  />
                </div>
                
                <!-- 上次复习 -->
                <div class="last-review" v-if="checkpoint.last_reviewed_at">
                  <el-icon><Clock /></el-icon>
                  <span>上次复习：{{ formatDate(checkpoint.last_reviewed_at) }}</span>
                </div>
              </div>
            </div>
            
            <el-empty v-if="filteredCheckpoints.length === 0" description="暂无知识点" />
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewApi } from '@/api'
import { ArrowLeft, Calendar, Clock, ChatDotRound } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id)

const loading = ref(false)
const planTitle = ref('')
const examDate = ref('')
const checkpoints = ref([])
const filterStatus = ref('')
const saveTimers = ref({})

const filteredCheckpoints = computed(() => {
  if (!filterStatus.value) return checkpoints.value
  return checkpoints.value.filter(cp => cp.status === filterStatus.value)
})

const statusCounts = computed(() => {
  const counts = {
    not_started: 0,
    learning: 0,
    mastered: 0
  }
  checkpoints.value.forEach(cp => {
    if (counts[cp.status] !== undefined) {
      counts[cp.status]++
    }
  })
  return counts
})

const overallProgress = computed(() => {
  if (checkpoints.value.length === 0) return 0
  const masteredCount = checkpoints.value.filter(cp => cp.status === 'mastered').length
  return Math.round((masteredCount / checkpoints.value.length) * 100)
})

const daysLeft = computed(() => {
  if (!examDate.value) return 0
  const exam = new Date(examDate.value)
  const today = new Date()
  const diff = exam - today
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

onMounted(async () => {
  await fetchPlanDetail()
  await fetchCheckpoints()
})

const fetchPlanDetail = async () => {
  try {
    const plan = await reviewApi.getPlanDetail(planId.value)
    planTitle.value = plan.title
    examDate.value = plan.exam_date || ''
  } catch (error) {
    console.error('获取计划详情失败:', error)
  }
}

const fetchCheckpoints = async () => {
  loading.value = true
  try {
    checkpoints.value = await reviewApi.getCheckpoints(planId.value)
  } catch (error) {
    console.error('获取知识点清单失败:', error)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  const types = {
    not_started: 'info',
    learning: 'warning',
    mastered: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    not_started: '未开始',
    learning: '学习中',
    mastered: '已掌握'
  }
  return texts[status] || status
}

const getProgressStatus = () => {
  const progress = overallProgress.value
  if (progress === 100) return 'success'
  if (progress >= 50) return 'warning'
  return ''
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const updateCheckpointStatus = async (checkpoint, isMastered) => {
  const newStatus = isMastered ? 'mastered' : 'learning'
  checkpoint.status = newStatus
  
  try {
    await reviewApi.updateCheckpoint(checkpoint.id, { 
      status: newStatus,
      last_reviewed_at: new Date().toISOString()
    })
  } catch (error) {
    console.error('更新状态失败:', error)
    checkpoint.status = isMastered ? 'learning' : 'mastered'
  }
}

const updateMasteryLevel = async (checkpoint, level) => {
  try {
    await reviewApi.updateCheckpoint(checkpoint.id, { mastery_level: level })
  } catch (error) {
    console.error('更新掌握程度失败:', error)
  }
}

const updateNotes = async (checkpoint) => {
  // Debounce notes saving
  if (saveTimers.value[checkpoint.id]) {
    clearTimeout(saveTimers.value[checkpoint.id])
  }
  
  saveTimers.value[checkpoint.id] = setTimeout(async () => {
    try {
      await reviewApi.updateCheckpoint(checkpoint.id, { notes: checkpoint.notes })
    } catch (error) {
      console.error('保存笔记失败:', error)
    }
  }, 500)
}

const goToSuggestions = () => {
  router.push(`/review/${planId.value}/suggestions`)
}

const goToChat = (checkpoint) => {
  router.push(`/review/${planId.value}/chat?checkpoint_id=${checkpoint.id}`)
}
</script>

<style scoped>
.review-checkpoints {
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

.progress-overview {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.progress-stats {
  display: flex;
  gap: 40px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-label {
  color: #909399;
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}

.stat-value.learning {
  color: #e6a23c;
}

.stat-value.mastered {
  color: #67c23a;
}

.exam-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #606266;
}

.days-left {
  background: #fef0f0;
  color: #f56c6c;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkpoint-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.checkpoint-item {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  background: #fff;
  transition: all 0.3s;
}

.checkpoint-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.checkpoint-item.mastered {
  background: #f0f9eb;
  border-color: #e1f3d8;
}

.checkpoint-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.checkpoint-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.checkpoint-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.checkpoint-actions {
  display: flex;
  gap: 8px;
}

.checkpoint-body {
  padding-left: 32px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-label {
  color: #909399;
  font-size: 14px;
  margin-bottom: 4px;
  display: block;
}

.mastery-section {
  display: flex;
  flex-direction: column;
}

.note-section {
  display: flex;
  flex-direction: column;
}

.last-review {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #c0c4cc;
  font-size: 12px;
}
</style>
