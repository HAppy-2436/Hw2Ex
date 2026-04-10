<template>
  <div class="review-report">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="header-left">
            <el-button :icon="Back" @click="$router.back()">返回</el-button>
            <h1>复习报告</h1>
          </div>
          <div class="header-actions">
            <el-select 
              v-model="selectedPlanId" 
              placeholder="选择复习计划"
              @change="fetchReportData"
              style="width: 200px;"
            >
              <el-option
                v-for="plan in reviewPlans"
                :key="plan.id"
                :label="plan.name"
                :value="plan.id"
              />
            </el-select>
            <el-button :icon="Refresh" @click="fetchReportData">刷新</el-button>
          </div>
        </div>
      </el-header>
      <el-main v-loading="loading">
        <div v-if="reportData" class="report-content">
          <!-- 概览卡片 -->
          <el-row :gutter="20" class="overview-row">
            <el-col :xs="24" :sm="12" :md="6">
              <StatCard
                title="复习计划"
                :value="reportData.plan_name || '暂无'"
                icon="Collection"
                icon-color="#409eff"
              />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <StatCard
                title="总知识点"
                :value="reportData.total_nodes || 0"
                icon="Document"
                icon-color="#67c23a"
              />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <StatCard
                title="已复习"
                :value="reportData.reviewed_nodes || 0"
                icon="Success"
                icon-color="#e6a23c"
              />
            </el-col>
            <el-col :xs="24" :sm="12" :md="6">
              <StatCard
                title="预计完成"
                :value="reportData.estimated_completion || '未知'"
                icon="Calendar"
                icon-color="#909399"
              />
            </el-col>
          </el-row>

          <!-- 主内容区 -->
          <el-row :gutter="20" class="main-row">
            <!-- 左侧：掌握度进度环 -->
            <el-col :xs="24" :lg="8">
              <el-card class="mastery-card">
                <template #header>
                  <div class="card-header">
                    <span>整体掌握度</span>
                  </div>
                </template>
                <div class="mastery-ring-container">
                  <div class="mastery-ring">
                    <svg viewBox="0 0 120 120">
                      <!-- 背景圆环 -->
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="transparent"
                        stroke="#ebeef5"
                        stroke-width="12"
                      />
                      <!-- 进度圆环 -->
                      <circle
                        cx="60"
                        cy="60"
                        r="50"
                        fill="transparent"
                        :stroke="masteryColor"
                        stroke-width="12"
                        :stroke-dasharray="circumference"
                        :stroke-dashoffset="progressOffset"
                        stroke-linecap="round"
                        :style="{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%', transition: 'stroke-dashoffset 0.5s ease' }"
                      />
                    </svg>
                    <div class="mastery-center">
                      <span class="mastery-value">{{ masteryPercentage }}</span>
                      <span class="mastery-label">%</span>
                    </div>
                  </div>
                  <div class="mastery-stats">
                    <div class="mastery-stat">
                      <span class="stat-name">高效记忆</span>
                      <span class="stat-num" :style="{ color: '#67c23a' }">
                        {{ reportData.efficient_count || 0 }}次
                      </span>
                    </div>
                    <div class="mastery-stat">
                      <span class="stat-name">需要强化</span>
                      <span class="stat-num" :style="{ color: '#e6a23c' }">
                        {{ reportData.needs_reinforcement || 0 }}次
                      </span>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>

            <!-- 右侧：薄弱点高亮 -->
            <el-col :xs="24" :lg="16">
              <el-card class="weakness-card">
                <template #header>
                  <div class="card-header">
                    <span>薄弱点分析</span>
                    <el-tag type="warning" size="small">需加强</el-tag>
                  </div>
                </template>
                <div class="weakness-list" v-if="weakPoints.length > 0">
                  <div 
                    v-for="(item, index) in weakPoints" 
                    :key="index"
                    class="weakness-item"
                  >
                    <div class="weakness-rank">{{ index + 1 }}</div>
                    <div class="weakness-info">
                      <span class="weakness-title">{{ item.node_title }}</span>
                      <span class="weakness-desc">
                        正确率: {{ ((item.accuracy || 0) * 100).toFixed(0) }}% |
                        距上次复习: {{ item.days_since_review || 0 }}天
                      </span>
                    </div>
                    <el-progress
                      :percentage="Math.round((item.accuracy || 0) * 100)"
                      :stroke-width="8"
                      :color="getProgressColor(item.accuracy)"
                      style="width: 120px;"
                    />
                  </div>
                </div>
                <el-empty v-else description="暂无薄弱点数据" />
              </el-card>
            </el-col>
          </el-row>

          <!-- 复习建议卡片 -->
          <el-row :gutter="20" class="suggestions-row">
            <el-col :span="24">
              <el-card class="suggestions-card">
                <template #header>
                  <div class="card-header">
                    <span>复习建议</span>
                  </div>
                </template>
                <div class="suggestions-grid" v-if="suggestions.length > 0">
                  <div 
                    v-for="(suggestion, index) in suggestions" 
                    :key="index"
                    class="suggestion-item"
                    :class="suggestion.type"
                  >
                    <div class="suggestion-icon">
                      <el-icon :size="24">
                        <component :is="getSuggestionIcon(suggestion.type)" />
                      </el-icon>
                    </div>
                    <div class="suggestion-content">
                      <span class="suggestion-title">{{ suggestion.title }}</span>
                      <span class="suggestion-desc">{{ suggestion.description }}</span>
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无建议" />
              </el-card>
            </el-col>
          </el-row>

          <!-- 复习时间线 -->
          <el-row :gutter="20" class="timeline-row">
            <el-col :span="24">
              <el-card class="timeline-card">
                <template #header>
                  <div class="card-header">
                    <span>复习进度时间线</span>
                  </div>
                </template>
                <div class="timeline-container">
                  <div class="timeline-track">
                    <div 
                      v-for="(item, index) in reviewTimeline" 
                      :key="index"
                      class="timeline-item"
                      :class="{ completed: item.completed, current: item.current }"
                    >
                      <div class="timeline-dot"></div>
                      <div class="timeline-info">
                        <span class="timeline-date">{{ item.date }}</span>
                        <span class="timeline-title">{{ item.title }}</span>
                        <span class="timeline-count" v-if="item.count">
                          {{ item.completed ? '已完成' : `待复习 ${item.count} 个` }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
        <el-empty v-else description="请选择复习计划查看报告" />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { reportsApi, reviewApi } from '@/api'
import { Refresh, Back, Clock, TrendCharts, Star, Warning, Info, Success } from '@element-plus/icons-vue'
import StatCard from '@/components/StatCard.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()

// 状态
const loading = ref(false)
const selectedPlanId = ref(null)
const reviewPlans = ref([])
const reportData = ref(null)

// 计算属性
const circumference = computed(() => 2 * Math.PI * 50)

const progressOffset = computed(() => {
  if (!reportData.value) return circumference.value
  const mastery = reportData.value.mastery_percentage || 0
  return circumference.value * (1 - mastery / 100)
})

const masteryPercentage = computed(() => {
  if (!reportData.value) return 0
  return Math.round(reportData.value.mastery_percentage || 0)
})

const masteryColor = computed(() => {
  const mastery = masteryPercentage.value
  if (mastery >= 80) return '#67c23a'
  if (mastery >= 60) return '#409eff'
  if (mastery >= 40) return '#e6a23c'
  return '#f56c6c'
})

const weakPoints = computed(() => {
  if (!reportData.value || !reportData.value.weak_points) return []
  return reportData.value.weak_points
})

const suggestions = computed(() => {
  if (!reportData.value || !reportData.value.suggestions) return []
  return reportData.value.suggestions
})

const reviewTimeline = computed(() => {
  if (!reportData.value || !reportData.value.timeline) return []
  return reportData.value.timeline
})

// 方法
const getProgressColor = (accuracy) => {
  if (accuracy >= 0.8) return '#67c23a'
  if (accuracy >= 0.6) return '#409eff'
  if (accuracy >= 0.4) return '#e6a23c'
  return '#f56c6c'
}

const getSuggestionIcon = (type) => {
  const iconMap = {
    priority: 'Warning',
    strategy: 'TrendCharts',
    tip: 'Info',
    encouragement: 'Success'
  }
  return iconMap[type] || 'Info'
}

const fetchReviewPlans = async () => {
  try {
    const plans = await reviewApi.getPlans({})
    reviewPlans.value = plans || []
    
    // 如果有plan_id参数，优先使用
    const planIdFromQuery = route.query.planId
    if (planIdFromQuery) {
      selectedPlanId.value = Number(planIdFromQuery)
    } else if (reviewPlans.value.length > 0) {
      selectedPlanId.value = reviewPlans.value[0].id
    }
  } catch (error) {
    console.error('获取复习计划列表失败:', error)
    // 使用模拟数据
    reviewPlans.value = [
      { id: 1, name: '数学第一章复习计划' },
      { id: 2, name: '物理力学复习计划' }
    ]
    if (reviewPlans.value.length > 0) {
      selectedPlanId.value = reviewPlans.value[0].id
    }
  }
}

const fetchReportData = async () => {
  if (!selectedPlanId.value) return
  
  loading.value = true
  try {
    reportData.value = await reportsApi.getReviewReport(selectedPlanId.value)
  } catch (error) {
    console.error('获取复习报告失败:', error)
    // 使用模拟数据
    reportData.value = {
      plan_name: reviewPlans.value.find(p => p.id === selectedPlanId.value)?.name || '复习计划',
      total_nodes: 25,
      reviewed_nodes: 15,
      mastery_percentage: 68,
      efficient_count: 12,
      needs_reinforcement: 5,
      estimated_completion: '3天后',
      weak_points: [
        { node_title: '二次函数图像变换', accuracy: 0.35, days_since_review: 5 },
        { node_title: '三角函数诱导公式', accuracy: 0.42, days_since_review: 7 },
        { node_title: '平面向量基本定理', accuracy: 0.48, days_since_review: 3 },
        { node_title: '立体几何证明', accuracy: 0.55, days_since_review: 4 }
      ],
      suggestions: [
        { type: 'priority', title: '优先复习', description: '二次函数相关知识点掌握较弱，建议优先安排复习' },
        { type: 'strategy', title: '复习策略', description: '采用间隔重复法，每天复习2-3个薄弱点' },
        { type: 'tip', title: '记忆技巧', description: '结合图形记忆和公式推导，加深理解' },
        { type: 'encouragement', title: '鼓励', description: '已掌握68%的内容，继续保持！' }
      ],
      timeline: [
        { date: '周一', title: '函数基础', count: 5, completed: true, current: false },
        { date: '周二', title: '函数图像', count: 4, completed: true, current: false },
        { date: '今天', title: '函数应用', count: 3, completed: false, current: true },
        { date: '周四', title: '综合练习', count: 6, completed: false, current: false },
        { date: '周五', title: '错题回顾', count: 4, completed: false, current: false }
      ]
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchReviewPlans().then(() => {
    if (selectedPlanId.value) {
      fetchReportData()
    }
  })
})
</script>

<style scoped>
.review-report {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  font-size: 24px;
  color: #303133;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.el-main {
  padding: 20px;
}

.overview-row {
  margin-bottom: 20px;
}

.main-row {
  margin-bottom: 20px;
}

/* 掌握度进度环 */
.mastery-card {
  height: 100%;
}

.mastery-ring-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
}

.mastery-ring {
  position: relative;
  width: 160px;
  height: 160px;
}

.mastery-ring svg {
  width: 100%;
  height: 100%;
}

.mastery-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.mastery-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}

.mastery-label {
  font-size: 18px;
  color: #909399;
}

.mastery-stats {
  display: flex;
  gap: 32px;
  margin-top: 24px;
}

.mastery-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-name {
  font-size: 12px;
  color: #909399;
}

.stat-num {
  font-size: 16px;
  font-weight: 500;
}

/* 薄弱点 */
.weakness-card {
  height: 100%;
}

.weakness-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weakness-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
}

.weakness-rank {
  width: 24px;
  height: 24px;
  background: #f56c6c;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  flex-shrink: 0;
}

.weakness-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.weakness-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.weakness-desc {
  font-size: 12px;
  color: #909399;
}

/* 建议卡片 */
.suggestions-card {
  margin-bottom: 20px;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border-left: 4px solid;
}

.suggestion-item.priority {
  background: #fef0f0;
  border-color: #f56c6c;
}

.suggestion-item.strategy {
  background: #ecf5ff;
  border-color: #409eff;
}

.suggestion-item.tip {
  background: #fdf6ec;
  border-color: #e6a23c;
}

.suggestion-item.encouragement {
  background: #f0f9eb;
  border-color: #67c23a;
}

.suggestion-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.suggestion-item.priority .suggestion-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.suggestion-item.strategy .suggestion-icon {
  background: #ecf5ff;
  color: #409eff;
}

.suggestion-item.tip .suggestion-icon {
  background: #fdf6ec;
  color: #e6a23c;
}

.suggestion-item.encouragement .suggestion-icon {
  background: #f0f9eb;
  color: #67c23a;
}

.suggestion-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.suggestion-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.suggestion-desc {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}

/* 时间线 */
.timeline-card {
  margin-bottom: 20px;
}

.timeline-container {
  padding: 20px 0;
  overflow-x: auto;
}

.timeline-track {
  display: flex;
  justify-content: space-between;
  position: relative;
  min-width: 600px;
  padding: 0 20px;
}

.timeline-track::before {
  content: '';
  position: absolute;
  top: 12px;
  left: 40px;
  right: 40px;
  height: 2px;
  background: #dcdfe6;
}

.timeline-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.timeline-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #dcdfe6;
  border: 3px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.timeline-item.completed .timeline-dot {
  background: #67c23a;
}

.timeline-item.current .timeline-dot {
  background: #409eff;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(64, 158, 255, 0.4); }
  50% { box-shadow: 0 0 0 8px rgba(64, 158, 255, 0); }
}

.timeline-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.timeline-date {
  font-size: 12px;
  color: #909399;
}

.timeline-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.timeline-count {
  font-size: 12px;
  color: #606266;
}

.timeline-item.completed .timeline-count {
  color: #67c23a;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 12px;
    padding: 12px 0;
  }
  
  .header-left {
    width: 100%;
    justify-content: space-between;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}
</style>
