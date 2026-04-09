<template>
  <div class="learning-dashboard">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>学习仪表盘</h1>
          <div class="header-actions">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
              @change="handleDateRangeChange"
            />
            <el-button :icon="Refresh" @click="refreshData">刷新</el-button>
          </div>
        </div>
      </el-header>
      <el-main>
        <!-- 统计卡片区域 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">本周学习时长</span>
                  <span class="stat-value">{{ totalStudyTime }}</span>
                  <span class="stat-unit">小时</span>
                </div>
                <div class="stat-icon study">
                  <el-icon><Clock /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">待复习知识点</span>
                  <span class="stat-value">{{ pendingReviewCount }}</span>
                  <span class="stat-unit">个</span>
                </div>
                <div class="stat-icon review">
                  <el-icon><Bell /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">AI Token消耗</span>
                  <span class="stat-value">{{ tokenUsage }}</span>
                  <span class="stat-unit">K</span>
                </div>
                <div class="stat-icon token">
                  <el-icon><Cpu /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">本周掌握度</span>
                  <span class="stat-value">{{ masteryRate }}</span>
                  <span class="stat-unit">%</span>
                </div>
                <div class="stat-icon mastery">
                  <el-icon><Trophy /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 图表区域 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 本周学习时长柱状图 -->
          <el-col :xs="24" :lg="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>本周学习时长</span>
                  <el-tag size="small">7天</el-tag>
                </div>
              </template>
              <div class="chart-container">
                <div class="bar-chart">
                  <div 
                    v-for="(day, index) in weeklyStudyData" 
                    :key="index"
                    class="bar-item"
                  >
                    <div class="bar-wrapper">
                      <div 
                        class="bar" 
                        :style="{ height: day.percentage + '%' }"
                      >
                        <span class="bar-value">{{ day.hours }}h</span>
                      </div>
                    </div>
                    <span class="bar-label">{{ day.label }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 知识点掌握度分布饼图 -->
          <el-col :xs="24" :lg="12">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>知识点掌握度分布</span>
                </div>
              </template>
              <div class="chart-container pie-chart-container">
                <div class="pie-chart">
                  <svg viewBox="0 0 100 100">
                    <circle 
                      v-for="(segment, index) in pieChartData" 
                      :key="index"
                      cx="50" 
                      cy="50" 
                      r="40"
                      fill="transparent"
                      :stroke="segment.color"
                      stroke-width="20"
                      :stroke-dasharray="segment.dashArray"
                      :stroke-dashoffset="segment.dashOffset"
                      :style="{ transform: 'rotate(-90deg)', transformOrigin: '50% 50%' }"
                    />
                  </svg>
                  <div class="pie-center">
                    <span class="pie-total">{{ totalNodes }}</span>
                    <span class="pie-label">知识点</span>
                  </div>
                </div>
                <div class="pie-legend">
                  <div 
                    v-for="item in masteryDistribution" 
                    :key="item.name"
                    class="legend-item"
                  >
                    <span class="legend-color" :style="{ background: item.color }"></span>
                    <span class="legend-name">{{ item.name }}</span>
                    <span class="legend-value">{{ item.count }}</span>
                    <span class="legend-percent">({{ item.percent }}%)</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 第二行图表 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 学习进度趋势折线图 -->
          <el-col :xs="24" :lg="16">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>学习进度趋势</span>
                  <el-select v-model="trendPeriod" size="small" style="width: 120px;">
                    <el-option label="最近7天" value="7days" />
                    <el-option label="最近30天" value="30days" />
                  </el-select>
                </div>
              </template>
              <div class="chart-container">
                <div class="line-chart">
                  <svg :viewBox="`0 0 ${trendData.length * 80} 150`" preserveAspectRatio="xMidYMid meet">
                    <!-- 网格线 -->
                    <line 
                      v-for="i in 4" 
                      :key="'grid-'+i"
                      :x1="0" 
                      :y1="(i * 30)"
                      :x2="trendData.length * 80" 
                      :y2="(i * 30)"
                      stroke="#ebeef5"
                      stroke-width="1"
                    />
                    <!-- 折线 -->
                    <polyline
                      :points="trendPoints"
                      fill="none"
                      stroke="#409eff"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <!-- 数据点 -->
                    <circle
                      v-for="(point, index) in trendPointsArray"
                      :key="'point-'+index"
                      :cx="point.x"
                      :cy="point.y"
                      r="4"
                      fill="#409eff"
                    />
                  </svg>
                  <div class="line-labels">
                    <span 
                      v-for="(item, index) in trendData" 
                      :key="'label-'+index"
                      class="line-label"
                    >
                      {{ item.label }}
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- AI使用统计 -->
          <el-col :xs="24" :lg="8">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>AI 使用统计</span>
                </div>
              </template>
              <div class="ai-stats">
                <div class="ai-stat-item">
                  <span class="ai-stat-label">今日API调用</span>
                  <span class="ai-stat-value">{{ todayApiCalls }}</span>
                </div>
                <div class="ai-stat-item">
                  <span class="ai-stat-label">今日Token消耗</span>
                  <span class="ai-stat-value">{{ todayTokens }}</span>
                </div>
                <div class="ai-stat-item">
                  <span class="ai-stat-label">预估成本</span>
                  <span class="ai-stat-value">¥{{ estimatedCost }}</span>
                </div>
                <el-button type="primary" link @click="goToTokenUsage">
                  查看详情
                  <el-icon><ArrowRight /></el-icon>
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 待复习提醒列表 -->
        <el-row :gutter="20" class="reminder-row">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>待复习提醒</span>
                  <el-badge :value="pendingReviewCount" type="warning">
                    <el-button link>查看全部</el-button>
                  </el-badge>
                </div>
              </template>
              <div class="reminder-list" v-if="reviewReminders.length > 0">
                <div 
                  v-for="item in reviewReminders" 
                  :key="item.id"
                  class="reminder-item"
                >
                  <div class="reminder-info">
                    <el-icon class="reminder-icon" :color="getPriorityColor(item.priority)">
                      <Clock />
                    </el-icon>
                    <div class="reminder-content">
                      <span class="reminder-title">{{ item.title }}</span>
                      <span class="reminder-desc">{{ item.nodeName }}</span>
                    </div>
                  </div>
                  <div class="reminder-meta">
                    <el-tag size="small" :type="getPriorityType(item.priority)">
                      {{ getPriorityText(item.priority) }}
                    </el-tag>
                    <span class="reminder-time">{{ item.dueText }}</span>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无待复习内容" />
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Clock, Bell, Cpu, Trophy, Refresh, ArrowRight } from '@element-plus/icons-vue'

const router = useRouter()

// 日期范围
const dateRange = ref([])
const trendPeriod = ref('7days')

// 统计数据
const totalStudyTime = ref(0)
const pendingReviewCount = ref(0)
const tokenUsage = ref(0)
const masteryRate = ref(0)

// 本周学习数据
const weeklyStudyData = ref([
  { label: '周一', hours: 0, percentage: 0 },
  { label: '周二', hours: 0, percentage: 0 },
  { label: '周三', hours: 0, percentage: 0 },
  { label: '周四', hours: 0, percentage: 0 },
  { label: '周五', hours: 0, percentage: 0 },
  { label: '周六', hours: 0, percentage: 0 },
  { label: '周日', hours: 0, percentage: 0 }
])

// 知识点掌握度分布
const masteryDistribution = ref([
  { name: '陌生', count: 0, color: '#f56c6c', percent: 0 },
  { name: '模糊', count: 0, color: '#e6a23c', percent: 0 },
  { name: '熟悉', count: 0, color: '#409eff', percent: 0 },
  { name: '掌握', count: 0, color: '#67c23a', percent: 0 }
])

// 学习进度趋势
const trendData = ref([])

// AI使用统计
const todayApiCalls = ref(0)
const todayTokens = ref(0)
const estimatedCost = ref(0)

// 待复习提醒
const reviewReminders = ref([])

// 计算属性
const totalNodes = computed(() => {
  return masteryDistribution.value.reduce((sum, item) => sum + item.count, 0)
})

const pieChartData = computed(() => {
  const total = totalNodes.value
  if (total === 0) return []
  
  let currentOffset = 0
  const circumference = 2 * Math.PI * 40
  
  return masteryDistribution.value.map(item => {
    const percent = item.count / total
    const dashLength = circumference * percent
    const dashArray = `${dashLength} ${circumference - dashLength}`
    const dashOffset = -currentOffset
    currentOffset += dashLength
    
    return {
      color: item.color,
      dashArray,
      dashOffset
    }
  })
})

const trendPoints = computed(() => {
  return trendPointsArray.value.map(p => `${p.x},${p.y}`).join(' ')
})

const trendPointsArray = computed(() => {
  if (!trendData.value.length) return []
  
  const maxValue = Math.max(...trendData.value.map(d => d.value), 1)
  const width = trendData.value.length * 80
  const height = 120
  
  return trendData.value.map((item, index) => ({
    x: index * 80 + 40,
    y: height - (item.value / maxValue) * height + 15,
    value: item.value
  }))
})

// 方法
const handleDateRangeChange = () => {
  refreshData()
}

const refreshData = () => {
  loadDashboardData()
}

const getPriorityColor = (priority) => {
  const colors = { high: '#f56c6c', medium: '#e6a23c', low: '#909399' }
  return colors[priority] || colors.medium
}

const getPriorityType = (priority) => {
  const types = { high: 'danger', medium: 'warning', low: 'info' }
  return types[priority] || 'info'
}

const getPriorityText = (priority) => {
  const texts = { high: '紧急', medium: '一般', low: '可选' }
  return texts[priority] || '一般'
}

const goToTokenUsage = () => {
  router.push('/token-usage')
}

const loadDashboardData = async () => {
  // 模拟数据加载
  // 实际项目中应该从API获取
  
  // 本周学习数据
  const weekHours = [2.5, 1.5, 3.0, 2.0, 4.5, 3.5, 2.0]
  const maxHours = Math.max(...weekHours)
  weeklyStudyData.value = weeklyStudyData.value.map((day, index) => ({
    ...day,
    hours: weekHours[index],
    percentage: (weekHours[index] / maxHours) * 100
  }))
  totalStudyTime.value = weekHours.reduce((a, b) => a + b, 0).toFixed(1)
  
  // 知识点掌握度
  const distribution = [
    { name: '陌生', count: 5, color: '#f56c6c' },
    { name: '模糊', count: 12, color: '#e6a23c' },
    { name: '熟悉', count: 25, color: '#409eff' },
    { name: '掌握', count: 18, color: '#67c23a' }
  ]
  const total = distribution.reduce((sum, d) => sum + d.count, 0)
  masteryDistribution.value = distribution.map(d => ({
    ...d,
    percent: Math.round((d.count / total) * 100)
  }))
  masteryRate.value = Math.round((18 / total) * 100)
  
  // 学习进度趋势
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  trendData.value = days.map((label, index) => ({
    label,
    value: Math.floor(Math.random() * 50) + 10
  }))
  
  // AI使用统计
  todayApiCalls.value = 24
  todayTokens.value = 12580
  estimatedCost.value = (12580 * 0.002).toFixed(2)
  
  // 待复习提醒
  reviewReminders.value = [
    { id: 1, title: '复习计划A', nodeName: '二次函数', priority: 'high', dueText: '已逾期' },
    { id: 2, title: '复习计划B', nodeName: '三角函数', priority: 'high', dueText: '今天到期' },
    { id: 3, title: '复习计划C', nodeName: '几何证明', priority: 'medium', dueText: '明天到期' },
    { id: 4, title: '复习计划D', nodeName: '概率统计', priority: 'low', dueText: '3天后到期' }
  ]
  pendingReviewCount.value = reviewReminders.value.length
  
  // Token使用
  tokenUsage.value = Math.round(todayTokens.value / 1000)
}

onMounted(() => {
  loadDashboardData()
})
</script>

<style scoped>
.learning-dashboard {
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

.header-content h1 {
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

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 16px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-unit {
  font-size: 14px;
  color: #c0c4cc;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.stat-icon.study {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.stat-icon.review {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stat-icon.token {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.stat-icon.mastery {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.charts-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  padding: 20px 0;
}

/* 柱状图样式 */
.bar-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 200px;
  padding: 0 20px;
}

.bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.bar-wrapper {
  height: 160px;
  width: 40px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  background: #f5f7fa;
  border-radius: 4px 4px 0 0;
}

.bar {
  width: 100%;
  background: linear-gradient(180deg, #409eff, #66b1ff);
  border-radius: 4px 4px 0 0;
  min-height: 20px;
  position: relative;
  transition: height 0.3s ease;
}

.bar-value {
  position: absolute;
  top: -24px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 12px;
  color: #409eff;
  font-weight: 500;
}

.bar-label {
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}

/* 饼图样式 */
.pie-chart-container {
  display: flex;
  align-items: center;
  justify-content: space-around;
}

.pie-chart {
  position: relative;
  width: 180px;
  height: 180px;
}

.pie-chart svg {
  width: 100%;
  height: 100%;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.pie-total {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.pie-label {
  font-size: 12px;
  color: #909399;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-name {
  font-size: 14px;
  color: #606266;
  width: 40px;
}

.legend-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.legend-percent {
  font-size: 12px;
  color: #c0c4cc;
}

/* 折线图样式 */
.line-chart {
  width: 100%;
  height: 180px;
}

.line-chart svg {
  width: 100%;
  height: 100%;
}

.line-labels {
  display: flex;
  justify-content: space-around;
  padding: 0 20px;
  margin-top: 8px;
}

.line-label {
  font-size: 12px;
  color: #909399;
  flex: 1;
  text-align: center;
}

/* AI统计样式 */
.ai-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ai-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.ai-stat-item:last-of-type {
  border-bottom: none;
}

.ai-stat-label {
  font-size: 14px;
  color: #909399;
}

.ai-stat-value {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

/* 提醒列表样式 */
.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: background 0.3s;
}

.reminder-item:hover {
  background: #ebeef5;
}

.reminder-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reminder-icon {
  font-size: 20px;
}

.reminder-content {
  display: flex;
  flex-direction: column;
}

.reminder-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.reminder-desc {
  font-size: 12px;
  color: #909399;
}

.reminder-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.reminder-time {
  font-size: 12px;
  color: #909399;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 12px;
    padding: 12px 0;
  }
  
  .header-content h1 {
    font-size: 20px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .bar-chart {
    height: 150px;
    padding: 0 10px;
  }
  
  .bar-wrapper {
    width: 30px;
    height: 120px;
  }
  
  .pie-chart-container {
    flex-direction: column;
  }
  
  .pie-legend {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .reminder-item {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .reminder-meta {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
