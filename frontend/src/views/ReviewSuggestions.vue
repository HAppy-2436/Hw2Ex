<template>
  <div class="review-suggestions">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>复习建议</h1>
        </div>
      </el-header>
      <el-main>
        <!-- 遗忘曲线说明 -->
        <el-card style="margin-bottom: 20px;">
          <div class="forgetting-curve-info">
            <div class="info-icon">
              <el-icon :size="40" color="#409eff"><Warning /></el-icon>
            </div>
            <div class="info-content">
              <h3>基于遗忘曲线的智能推荐</h3>
              <p>根据艾宾浩斯遗忘曲线，知识点在学习后会逐渐遗忘。建议在学习后的以下时间点进行复习：</p>
              <div class="curve-points">
                <span class="point">20分钟</span>
                <span class="point">1小时</span>
                <span class="point">1天</span>
                <span class="point">2天</span>
                <span class="point">6天</span>
                <span class="point">31天</span>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 复习优先级列表 -->
        <el-card v-loading="loading">
          <template #header>
            <div class="card-header">
              <span>推荐复习知识点</span>
              <span class="suggestion-count">共 {{ suggestions.length }} 个</span>
            </div>
          </template>
          
          <div class="suggestion-list" v-if="suggestions.length > 0">
            <div 
              v-for="(item, index) in suggestions" 
              :key="item.checkpoint_id" 
              class="suggestion-item"
              :class="{ urgent: item.priority === 'high', medium: item.priority === 'medium' }"
            >
              <div class="priority-badge">
                <span class="priority-number">{{ index + 1 }}</span>
                <el-tag 
                  size="small" 
                  :type="getPriorityType(item.priority)"
                >
                  {{ getPriorityText(item.priority) }}
                </el-tag>
              </div>
              
              <div class="suggestion-content">
                <div class="suggestion-header">
                  <span class="node-name">{{ item.node_name }}</span>
                  <el-tag size="small" :type="getStatusType(item.status)">
                    {{ getStatusText(item.status) }}
                  </el-tag>
                </div>
                
                <div class="suggestion-meta">
                  <span class="meta-item">
                    <el-icon><Clock /></el-icon>
                    距上次复习：{{ item.days_since_review }} 天
                  </span>
                  <span class="meta-item" v-if="item.next_review_date">
                    <el-icon><Calendar /></el-icon>
                    下次复习：{{ item.next_review_date }}
                  </span>
                  <span class="meta-item">
                    <el-icon><Star /></el-icon>
                    掌握程度：{{ item.mastery_level }}/5
                  </span>
                </div>
                
                <div class="suggestion-reason">
                  <el-icon><InfoFilled /></el-icon>
                  {{ item.reason }}
                </div>
              </div>
              
              <div class="suggestion-action">
                <el-button type="primary" @click="startReview(item)">
                  开始复习
                </el-button>
                <el-button @click="viewDetails(item)">
                  查看详情
                </el-button>
              </div>
            </div>
          </div>
          
          <el-empty v-else description="暂无需要复习的知识点">
            <el-button type="primary" @click="goToCheckpoints">去学习新知识</el-button>
          </el-empty>
        </el-card>

        <!-- 复习完成提示 -->
        <el-card v-if="completedReview" style="margin-top: 20px;" class="completed-card">
          <div class="completed-message">
            <el-icon color="#67c23a" :size="30"><CircleCheckFilled /></el-icon>
            <span>太棒了！今天的复习任务已完成，记得明天再来哦！</span>
          </div>
        </el-card>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewApi } from '@/api'
import { 
  ArrowLeft, 
  Warning, 
  Clock, 
  Calendar, 
  Star, 
  InfoFilled,
  CircleCheckFilled 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id)

const loading = ref(false)
const suggestions = ref([])
const completedReview = ref(false)

const getPriorityType = (priority) => {
  const types = {
    high: 'danger',
    medium: 'warning',
    low: 'info'
  }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = {
    high: '紧急',
    medium: '重要',
    low: '一般'
  }
  return texts[priority] || priority
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

onMounted(async () => {
  await fetchSuggestions()
})

const fetchSuggestions = async () => {
  loading.value = true
  try {
    const data = await reviewApi.getSuggestions(planId.value)
    suggestions.value = data.suggestions || []
    completedReview.value = data.completed || false
  } catch (error) {
    console.error('获取复习建议失败:', error)
  } finally {
    loading.value = false
  }
}

const startReview = (item) => {
  router.push(`/review/${planId.value}/chat?checkpoint_id=${item.checkpoint_id}`)
}

const viewDetails = (item) => {
  router.push(`/review/${planId.value}/chat?checkpoint_id=${item.checkpoint_id}`)
}

const goToCheckpoints = () => {
  router.push(`/review/${planId.value}/checkpoints`)
}
</script>

<style scoped>
.review-suggestions {
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

.forgetting-curve-info {
  display: flex;
  gap: 20px;
  align-items: center;
}

.info-icon {
  flex-shrink: 0;
}

.info-content h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.info-content p {
  margin: 0 0 12px 0;
  color: #606266;
  font-size: 14px;
}

.curve-points {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.point {
  background: #ecf5ff;
  color: #409eff;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-count {
  color: #909399;
  font-size: 14px;
}

.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  background: #fff;
  transition: all 0.3s;
}

.suggestion-item:hover {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.suggestion-item.urgent {
  border-left: 4px solid #f56c6c;
  background: #fef0f0;
}

.suggestion-item.medium {
  border-left: 4px solid #e6a23c;
  background: #fdf6ec;
}

.priority-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.priority-number {
  width: 32px;
  height: 32px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.suggestion-content {
  flex: 1;
}

.suggestion-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.node-name {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.suggestion-meta {
  display: flex;
  gap: 20px;
  margin-bottom: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #909399;
  font-size: 13px;
}

.suggestion-reason {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  color: #606266;
  font-size: 13px;
  background: #f5f7fa;
  padding: 8px 12px;
  border-radius: 4px;
}

.suggestion-action {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.completed-card {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
}

.completed-message {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #67c23a;
  font-size: 16px;
}
</style>
