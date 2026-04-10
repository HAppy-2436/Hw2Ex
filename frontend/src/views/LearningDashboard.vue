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
                  <span class="stat-label">已学习知识点</span>
                  <span class="stat-value">{{ learnedNodes }}</span>
                  <span class="stat-unit">个</span>
                </div>
                <div class="stat-icon nodes">
                  <el-icon><Document /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">平均自评分数</span>
                  <span class="stat-value">{{ averageRating }}</span>
                  <span class="stat-unit">分</span>
                </div>
                <div class="stat-icon rating">
                  <el-icon><Star /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="12" :md="6">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-info">
                  <span class="stat-label">待复习提醒</span>
                  <span class="stat-value">{{ pendingReviewCount }}</span>
                  <span class="stat-unit">个</span>
                </div>
                <div class="stat-icon review">
                  <el-icon><Bell /></el-icon>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 图表区域 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 本周学习时长柱状图 -->
          <el-col :xs="24" :lg="12">
            <el-card v-loading="loadingWeekly">
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
                        :class="{ 'bar-today': day.isToday }"
                        :style="{ height: day.percentage + '%' }"
                      >
                        <span class="bar-value" v-if="day.hours > 0">{{ day.hours }}h</span>
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
            <el-card v-loading="loadingMastery">
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
            <el-card v-loading="loadingTrend">
              <template #header>
                <div class="card-header">
                  <span>学习进度趋势</span>
                  <el-select v-model="trendPeriod" size="small" style="width: 120px;" @change="fetchProgressTrend">
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

          <!-- 待复习提醒 -->
          <el-col :xs="24" :lg="8">
            <el-card v-loading="loadingReminders">
              <template #header>
                <div class="card-header">
                  <span>待复习提醒</span>
                  <el-badge :value="pendingReviewCount" type="warning" />
                </div>
              </template>
              <div class="reminder-list" v-if="reviewReminders.length > 0">
                <div 
                  v-for="item in reviewReminders" 
                  :key="item.node_id"
                  class="reminder-item"
                >
                  <div class="reminder-info">
                    <el-icon class="reminder-icon" :color="getReminderColor(item.days_since_review)">
                      <Clock />
                    </el-icon>
                    <div class="reminder-content">
                      <span class="reminder-title">{{ item.node_title }}</span>
                      <span class="reminder-desc">正确率: {{ ((item.accuracy || 0) * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                  <div class="reminder-meta">
                    <el-tag size="small" :type="getReminderType(item.days_since_review)">
                      {{ item.days_since_review }}天未复习
                    </el-tag>
                    <el-button type="primary" size="small" link @click="goToStudy(item.node_id)">
                      立即复习
                    </el-button>
                  </div>
                </div>
              </div>
              <el-empty v-else description="暂无待复习提醒" />
            </el-card>
          </el-col>
        </el-row>

        <!-- 第三行图表：雷达图 + 学习效率 + 复习进度甘特图 -->
        <el-row :gutter="20" class="charts-row">
          <!-- 知识掌握度雷达图 -->
          <el-col :xs="24" :lg="8">
            <el-card v-loading="loadingRadar">
              <template #header>
                <div class="card-header">
                  <span>知识掌握度</span>
                  <el-tag size="small">能力分析</el-tag>
                </div>
              </template>
              <div class="chart-container radar-chart-container">
                <div class="radar-chart">
                  <svg viewBox="0 0 200 200">
                    <!-- 背景网格 -->
                    <g class="radar-grid">
                      <polygon 
                        v-for="(level, i) in radarLevels" 
                        :key="'level-'+i"
                        :points="getRadarPoints(level)"
                        fill="none"
                        stroke="#e4e7ed"
                        stroke-width="1"
                      />
                    </g>
                    <!-- 轴线 -->
                    <g class="radar-axes">
                      <line 
                        v-for="(axis, i) in radarAxes" 
                        :key="'axis-'+i"
                        :x1="100"
                        :y1="100"
                        :x2="getRadarPoint(axis.label, 1).x"
                        :y2="getRadarPoint(axis.label, 1).y"
                        stroke="#e4e7ed"
                        stroke-width="1"
                      />
                    </g>
                    <!-- 数据区域 -->
                    <polygon
                      :points="radarDataPoints"
                      fill="rgba(64, 158, 255, 0.2)"
                      stroke="#409eff"
                      stroke-width="2"
                    />
                    <!-- 数据点 -->
                    <circle
                      v-for="(point, i) in radarDataPointsArray"
                      :key="'data-point-'+i"
                      :cx="point.x"
                      :cy="point.y"
                      r="4"
                      fill="#409eff"
                    />
                    <!-- 轴标签 -->
                    <text
                      v-for="(axis, i) in radarAxes"
                      :key="'label-'+i"
                      :x="getLabelPosition(axis.label).x"
                      :y="getLabelPosition(axis.label).y"
                      text-anchor="middle"
                      dominant-baseline="middle"
                      font-size="11"
                      fill="#606266"
                    >
                      {{ axis.name }}
                    </text>
                  </svg>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 学习效率趋势 -->
          <el-col :xs="24" :lg="8">
            <el-card v-loading="loadingEfficiency">
              <template #header>
                <div class="card-header">
                  <span>学习效率</span>
                  <el-select v-model="efficiencyPeriod" size="small" style="width: 100px;" @change="fetchEfficiencyTrend">
                    <el-option label="7天" value="7" />
                    <el-option label="30天" value="30" />
                  </el-select>
                </div>
              </template>
              <div class="chart-container efficiency-chart-container">
                <div class="efficiency-info">
                  <div class="efficiency-current">
                    <span class="efficiency-value">{{ currentEfficiency }}</span>
                    <span class="efficiency-unit">%</span>
                  </div>
                  <span class="efficiency-label">当前效率</span>
                </div>
                <div class="efficiency-trend">
                  <div 
                    v-for="(item, index) in efficiencyTrendData" 
                    :key="index"
                    class="efficiency-bar-item"
                  >
                    <div class="efficiency-bar-wrapper">
                      <div 
                        class="efficiency-bar" 
                        :style="{ height: (item.efficiency || 0) + '%' }"
                      ></div>
                    </div>
                    <span class="efficiency-bar-label">{{ item.label }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>

          <!-- 复习进度甘特图 -->
          <el-col :xs="24" :lg="8">
            <el-card v-loading="loadingGantt">
              <template #header>
                <div class="card-header">
                  <span>复习进度</span>
                  <el-button type="primary" link @click="$router.push('/review-report')">
                    查看报告
                  </el-button>
                </div>
              </template>
              <div class="chart-container gantt-chart-container">
                <div class="gantt-chart">
                  <div 
                    v-for="(item, index) in reviewGanttData" 
                    :key="index"
                    class="gantt-row"
                  >
                    <span class="gantt-label">{{ item.subject }}</span>
                    <div class="gantt-track">
                      <div 
                        class="gantt-bar"
                        :class="{ completed: item.completed >= item.total }"
                        :style="{ 
                          width: (item.total > 0 ? (item.completed / item.total) * 100 : 0) + '%',
                          background: getGanttColor(item.completed / item.total)
                        }"
                      >
                        <span class="gantt-progress" v-if="item.total > 0">
                          {{ item.completed }}/{{ item.total }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
                <div class="gantt-legend">
                  <span class="legend-dot" style="background: #67c23a;"></span>
                  <span class="legend-text">已完成</span>
                  <span class="legend-dot" style="background: #409eff;"></span>
                  <span class="legend-text">进行中</span>
                  <span class="legend-dot" style="background: #e6a23c;"></span>
                  <span class="legend-text">待开始</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 最近学习记录 -->
        <el-row :gutter="20" class="history-row">
          <el-col :span="24">
            <el-card v-loading="loadingHistory">
              <template #header>
                <div class="card-header">
                  <span>最近学习记录</span>
                  <el-button type="primary" link @click="$router.push('/study')">
                    查看更多
                  </el-button>
                </div>
              </template>
              <el-table :data="recentRecords" stripe v-if="recentRecords.length > 0">
                <el-table-column prop="node_title" label="知识点" min-width="150">
                  <template #default="{ row }">
                    <el-link type="primary" @click="goToStudy(row.node_id)">
                      {{ row.node_title || '未知知识点' }}
                    </el-link>
                  </template>
                </el-table-column>
                <el-table-column prop="duration" label="学习时长" width="120">
                  <template #default="{ row }">
                    {{ row.duration || 0 }}分钟
                  </template>
                </el-table-column>
                <el-table-column prop="self_rating" label="自评分数" width="120">
                  <template #default="{ row }">
                    <el-rate v-model="row.self_rating" disabled :max="5" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="notes" label="学习笔记" min-width="200">
                  <template #default="{ row }">
                    <span class="notes-text">{{ row.notes || '无' }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="created_at" label="学习时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
              <el-empty v-else description="暂无学习记录" />
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
import { learnApi, nodeApi, analyticsApi } from '@/api'
import { Clock, Bell, Refresh, Star, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 日期范围
const dateRange = ref([])
const trendPeriod = ref('7days')

// 加载状态
const loadingWeekly = ref(false)
const loadingMastery = ref(false)
const loadingTrend = ref(false)
const loadingReminders = ref(false)
const loadingHistory = ref(false)

// 统计数据
const totalStudyTime = ref(0)
const learnedNodes = ref(0)
const averageRating = ref(0)
const pendingReviewCount = ref(0)
const learningStats = ref(null)

// 本周学习数据
const weeklyStudyData = ref([
  { label: '周一', hours: 0, percentage: 0, isToday: false },
  { label: '周二', hours: 0, percentage: 0, isToday: false },
  { label: '周三', hours: 0, percentage: 0, isToday: false },
  { label: '周四', hours: 0, percentage: 0, isToday: false },
  { label: '周五', hours: 0, percentage: 0, isToday: false },
  { label: '周六', hours: 0, percentage: 0, isToday: false },
  { label: '周日', hours: 0, percentage: 0, isToday: false }
])

// 知识点掌握度分布
const masteryDistribution = ref([
  { name: '未开始', count: 0, color: '#909399', percent: 0 },
  { name: '学习中', count: 0, color: '#e6a23c', percent: 0 },
  { name: '复习中', count: 0, color: '#409eff', percent: 0 },
  { name: '已掌握', count: 0, color: '#67c23a', percent: 0 }
])

// 学习进度趋势
const trendData = ref([])

// 待复习提醒
const reviewReminders = ref([])

// 最近学习记录
const recentRecords = ref([])

// 雷达图数据
const radarAxes = ref([
  { label: 'memory', name: '记忆' },
  { label: 'understanding', name: '理解' },
  { label: 'application', name: '应用' },
  { label: 'analysis', name: '分析' },
  { label: 'evaluation', name: '评价' }
])
const radarLevels = [0.2, 0.4, 0.6, 0.8, 1]
const radarData = ref({})
const loadingRadar = ref(false)

// 学习效率数据
const efficiencyPeriod = ref('7')
const efficiencyTrendData = ref([])
const currentEfficiency = ref(0)
const loadingEfficiency = ref(false)

// 复习甘特图数据
const reviewGanttData = ref([])
const loadingGantt = ref(false)

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

const refreshData = async () => {
  await Promise.all([
    fetchWeeklyStats(),
    fetchMasteryDistribution(),
    fetchProgressTrend(),
    fetchReviewReminders(),
    fetchRecentRecords(),
    fetchStats(),
    fetchRadarData(),
    fetchEfficiencyTrend(),
    fetchReviewGantt()
  ])
}

const getReminderColor = (days) => {
  if (days >= 7) return '#f56c6c'
  if (days >= 4) return '#e6a23c'
  return '#909399'
}

const getReminderType = (days) => {
  if (days >= 7) return 'danger'
  if (days >= 4) return 'warning'
  return 'info'
}

const goToStudy = (nodeId) => {
  router.push({ path: '/study', query: { nodeId } })
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchWeeklyStats = async () => {
  loadingWeekly.value = true
  try {
    // 获取本周7天的数据
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    const today = new Date()
    const todayDayIndex = today.getDay() === 0 ? 6 : today.getDay() - 1
    
    // 初始化数据
    weeklyStudyData.value = days.map((label, index) => ({
      label,
      hours: 0,
      percentage: 0,
      isToday: index === todayDayIndex
    }))
    
    // 尝试从API获取数据
    try {
      const records = await learnApi.getRecords({})
      
      // 按天分组计算学习时长
      records.forEach(record => {
        if (record.created_at) {
          const recordDate = new Date(record.created_at)
          const dayIndex = recordDate.getDay() === 0 ? 6 : recordDate.getDay() - 1
          
          // 只统计本周的数据
          const startOfWeek = new Date(today)
          startOfWeek.setDate(today.getDate() - todayDayIndex)
          startOfWeek.setHours(0, 0, 0, 0)
          
          if (recordDate >= startOfWeek) {
            weeklyStudyData.value[dayIndex].hours += (record.duration || 0) / 60
          }
        }
      })
    } catch (e) {
      console.log('使用模拟周数据')
    }
    
    // 计算百分比
    const maxHours = Math.max(...weeklyStudyData.value.map(d => d.hours), 1)
    weeklyStudyData.value = weeklyStudyData.value.map(day => ({
      ...day,
      hours: Math.round(day.hours * 10) / 10,
      percentage: day.isToday ? 100 : Math.max((day.hours / maxHours) * 100, day.isToday ? 5 : 0)
    }))
    
    totalStudyTime.value = weeklyStudyData.value.reduce((sum, d) => sum + d.hours, 0).toFixed(1)
  } catch (error) {
    console.error('获取本周数据失败:', error)
  } finally {
    loadingWeekly.value = false
  }
}

const fetchMasteryDistribution = async () => {
  loadingMastery.value = true
  try {
    // 重置分布
    masteryDistribution.value = [
      { name: '未开始', count: 0, color: '#909399', percent: 0 },
      { name: '学习中', count: 0, color: '#e6a23c', percent: 0 },
      { name: '复习中', count: 0, color: '#409eff', percent: 0 },
      { name: '已掌握', count: 0, color: '#67c23a', percent: 0 }
    ]
    
    try {
      // 从stats API获取
      const stats = await learnApi.getStats()
      if (stats && stats.status_breakdown) {
        const statusMap = {
          'not_started': '未开始',
          'learning': '学习中',
          'reviewing': '复习中',
          'mastered': '已掌握'
        }
        
        Object.entries(stats.status_breakdown).forEach(([status, count]) => {
          const item = masteryDistribution.value.find(d => d.name === statusMap[status])
          if (item) {
            item.count = count
          }
        })
      }
      
      if (stats) {
        learnedNodes.value = stats.learned_nodes || 0
      }
    } catch (e) {
      // 使用模拟数据
      masteryDistribution.value = [
        { name: '未开始', count: 10, color: '#909399', percent: 20 },
        { name: '学习中', count: 15, color: '#e6a23c', percent: 30 },
        { name: '复习中', count: 15, color: '#409eff', percent: 30 },
        { name: '已掌握', count: 10, color: '#67c23a', percent: 20 }
      ]
      learnedNodes.value = 50
    }
    
    // 计算百分比
    const total = masteryDistribution.value.reduce((sum, d) => sum + d.count, 0)
    masteryDistribution.value = masteryDistribution.value.map(d => ({
      ...d,
      percent: total > 0 ? Math.round((d.count / total) * 100) : 0
    }))
  } catch (error) {
    console.error('获取掌握度分布失败:', error)
  } finally {
    loadingMastery.value = false
  }
}

const fetchProgressTrend = async () => {
  loadingTrend.value = true
  try {
    const days = trendPeriod.value === '7days' ? 7 : 30
    const labels = days === 7 
      ? ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      : ['第1周', '第2周', '第3周', '第4周']
    
    // 初始化趋势数据
    trendData.value = labels.map(label => ({
      label,
      value: 0
    }))
    
    try {
      // 尝试从records构建趋势
      const records = await learnApi.getRecords({})
      
      if (records && records.length > 0) {
        // 按日期分组
        const dateGroups = {}
        records.forEach(record => {
          if (record.created_at) {
            const date = record.created_at.split('T')[0]
            if (!dateGroups[date]) {
              dateGroups[date] = { count: 0, duration: 0 }
            }
            dateGroups[date].count++
            dateGroups[date].duration += record.duration || 0
          }
        })
        
        // 填充到趋势数据
        // 对于7天，我们直接用记录
        if (days === 7) {
          const today = new Date()
          for (let i = 6; i >= 0; i--) {
            const date = new Date(today)
            date.setDate(date.getDate() - i)
            const dateStr = date.toISOString().split('T')[0]
            const dayIndex = date.getDay() === 0 ? 6 : date.getDay() - 1
            
            if (dateGroups[dateStr]) {
              trendData.value[dayIndex].value = dateGroups[dateStr].duration
            }
          }
        }
      }
    } catch (e) {
      // 使用模拟数据
      trendData.value = labels.map((label, index) => ({
        label,
        value: Math.floor(Math.random() * 60) + 20
      }))
    }
  } catch (error) {
    console.error('获取进度趋势失败:', error)
  } finally {
    loadingTrend.value = false
  }
}

const fetchReviewReminders = async () => {
  loadingReminders.value = true
  try {
    try {
      reviewReminders.value = await learnApi.getReviewPlan(7)
    } catch (e) {
      // 使用模拟数据
      reviewReminders.value = [
        {
          node_id: 1,
          node_title: '二次函数的基本性质',
          status: 'reviewing',
          days_since_review: 5,
          accuracy: 0.65
        },
        {
          node_id: 2,
          node_title: '三角函数变换',
          status: 'learning',
          days_since_review: 7,
          accuracy: 0.4
        },
        {
          node_id: 3,
          node_title: '几何证明方法',
          status: 'learning',
          days_since_review: 3,
          accuracy: 0.55
        }
      ]
    }
    pendingReviewCount.value = reviewReminders.value.length
  } catch (error) {
    console.error('获取复习提醒失败:', error)
    reviewReminders.value = []
    pendingReviewCount.value = 0
  } finally {
    loadingReminders.value = false
  }
}

const fetchRecentRecords = async () => {
  loadingHistory.value = true
  try {
    try {
      let records = await learnApi.getRecords({})
      
      // 如果有node信息，补充node_title
      if (records && records.length > 0) {
        const nodeIds = [...new Set(records.map(r => r.node_id).filter(Boolean))]
        
        // 获取各节点信息
        const nodePromises = nodeIds.slice(0, 10).map(async (nodeId) => {
          try {
            const node = await nodeApi.detail(nodeId)
            return { id: nodeId, title: node.title }
          } catch (e) {
            return { id: nodeId, title: null }
          }
        })
        
        const nodeMap = {}
        const nodeDetails = await Promise.all(nodePromises)
        nodeDetails.forEach(n => {
          nodeMap[n.id] = n.title
        })
        
        records = records.map(r => ({
          ...r,
          node_title: nodeMap[r.node_id] || r.node_title || '未知知识点'
        }))
      }
      
      recentRecords.value = records.slice(0, 10)
    } catch (e) {
      // 使用模拟数据
      recentRecords.value = [
        {
          id: 1,
          node_id: 1,
          node_title: '一元二次方程',
          duration: 30,
          self_rating: 4,
          notes: '理解了求根公式',
          created_at: new Date().toISOString()
        },
        {
          id: 2,
          node_id: 2,
          node_title: '因式分解技巧',
          duration: 45,
          self_rating: 5,
          notes: '掌握了十字相乘法',
          created_at: new Date(Date.now() - 86400000).toISOString()
        },
        {
          id: 3,
          node_id: 3,
          node_title: '几何证明',
          duration: 25,
          self_rating: 3,
          notes: '需要更多练习',
          created_at: new Date(Date.now() - 172800000).toISOString()
        }
      ]
    }
    
    // 计算平均评分
    const ratedRecords = recentRecords.value.filter(r => r.self_rating > 0)
    if (ratedRecords.length > 0) {
      averageRating.value = (ratedRecords.reduce((sum, r) => sum + r.self_rating, 0) / ratedRecords.length).toFixed(1)
    }
  } catch (error) {
    console.error('获取学习记录失败:', error)
    recentRecords.value = []
  } finally {
    loadingHistory.value = false
  }
}

const fetchStats = async () => {
  try {
    try {
      learningStats.value = await learnApi.getStats()
      if (learningStats.value) {
        learnedNodes.value = learningStats.value.learned_nodes || 0
      }
    } catch (e) {
      // 模拟数据已在其他方法中处理
    }
  } catch (error) {
    console.error('获取学习统计失败:', error)
  }
}

// 雷达图方法
const getRadarPoint = (label, value) => {
  const index = radarAxes.value.findIndex(a => a.label === label)
  if (index === -1) return { x: 100, y: 100 }
  
  const angle = (index * 72 - 90) * Math.PI / 180
  const radius = 70 * value
  return {
    x: 100 + radius * Math.cos(angle),
    y: 100 + radius * Math.sin(angle)
  }
}

const getRadarPoints = (level) => {
  return radarAxes.value.map((axis, i) => {
    const point = getRadarPoint(axis.label, level)
    return `${point.x},${point.y}`
  }).join(' ')
}

const radarDataPoints = computed(() => {
  return radarDataPointsArray.value.map(p => `${p.x},${p.y}`).join(' ')
})

const radarDataPointsArray = computed(() => {
  return radarAxes.value.map(axis => {
    const value = radarData.value[axis.label] || 0
    return getRadarPoint(axis.label, value / 100)
  })
})

const getLabelPosition = (label) => {
  const point = getRadarPoint(label, 1.15)
  return point
}

const fetchRadarData = async () => {
  loadingRadar.value = true
  try {
    try {
      const data = await analyticsApi.getMasteryRadar()
      radarData.value = data || {}
    } catch (e) {
      // 使用模拟数据
      radarData.value = {
        memory: 75,
        understanding: 82,
        application: 68,
        analysis: 55,
        evaluation: 45
      }
    }
  } catch (error) {
    console.error('获取雷达图数据失败:', error)
  } finally {
    loadingRadar.value = false
  }
}

// 学习效率趋势方法
const fetchEfficiencyTrend = async () => {
  loadingEfficiency.value = true
  try {
    try {
      const data = await analyticsApi.getEfficiencyTrend({ days: efficiencyPeriod.value })
      if (data && data.trend) {
        efficiencyTrendData.value = data.trend
        currentEfficiency.value = data.current || 0
      }
    } catch (e) {
      // 使用模拟数据
      const days = parseInt(efficiencyPeriod.value)
      const labels = days === 7 
        ? ['一', '二', '三', '四', '五', '六', '日']
        : ['第1周', '第2周', '第3周', '第4周']
      
      efficiencyTrendData.value = labels.map((label, i) => ({
        label,
        efficiency: Math.floor(Math.random() * 30) + 60
      }))
      currentEfficiency.value = Math.floor(Math.random() * 20) + 70
    }
  } catch (error) {
    console.error('获取学习效率趋势失败:', error)
  } finally {
    loadingEfficiency.value = false
  }
}

// 复习进度甘特图方法
const getGanttColor = (ratio) => {
  if (ratio >= 1) return '#67c23a'
  if (ratio >= 0.5) return '#409eff'
  return '#e6a23c'
}

const fetchReviewGantt = async () => {
  loadingGantt.value = true
  try {
    try {
      const data = await analyticsApi.getReviewGantt()
      reviewGanttData.value = data || []
    } catch (e) {
      // 使用模拟数据
      reviewGanttData.value = [
        { subject: '数学', completed: 8, total: 12 },
        { subject: '物理', completed: 5, total: 10 },
        { subject: '化学', completed: 3, total: 8 },
        { subject: '英语', completed: 10, total: 15 }
      ]
    }
  } catch (error) {
    console.error('获取复习进度甘特图失败:', error)
  } finally {
    loadingGantt.value = false
  }
}

onMounted(() => {
  refreshData()
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

.stat-icon.nodes {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-icon.rating {
  background: linear-gradient(135deg, #e6a23c, #ebb563);
}

.stat-icon.review {
  background: linear-gradient(135deg, #f56c6c, #f78989);
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
  min-height: 4px;
  position: relative;
  transition: height 0.3s ease;
}

.bar-today {
  background: linear-gradient(180deg, #67c23a, #85ce61);
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
  width: 50px;
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

/* 提醒列表样式 */
.reminder-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
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

/* 学习记录 */
.history-row {
  margin-top: 20px;
}

.notes-text {
  color: #606266;
  font-size: 14px;
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

/* 雷达图样式 */
.radar-chart-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.radar-chart {
  width: 220px;
  height: 220px;
}

.radar-chart svg {
  width: 100%;
  height: 100%;
}

/* 学习效率样式 */
.efficiency-chart-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.efficiency-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 0;
}

.efficiency-current {
  display: flex;
  align-items: baseline;
}

.efficiency-value {
  font-size: 42px;
  font-weight: bold;
  color: #409eff;
}

.efficiency-unit {
  font-size: 20px;
  color: #409eff;
  margin-left: 2px;
}

.efficiency-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.efficiency-trend {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 80px;
  padding: 0 10px;
}

.efficiency-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.efficiency-bar-wrapper {
  width: 24px;
  height: 60px;
  background: #f5f7fa;
  border-radius: 4px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
}

.efficiency-bar {
  width: 100%;
  background: linear-gradient(180deg, #409eff, #66b1ff);
  border-radius: 4px;
  min-height: 4px;
  transition: height 0.3s ease;
}

.efficiency-bar-label {
  font-size: 10px;
  color: #909399;
}

/* 复习进度甘特图样式 */
.gantt-chart-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gantt-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gantt-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.gantt-label {
  width: 40px;
  font-size: 12px;
  color: #606266;
  text-align: right;
  flex-shrink: 0;
}

.gantt-track {
  flex: 1;
  height: 20px;
  background: #f5f7fa;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.gantt-bar {
  height: 100%;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 6px;
  transition: width 0.3s ease;
  min-width: 30px;
}

.gantt-bar.completed {
  background: #67c23a;
}

.gantt-bar:not(.completed) {
  background: linear-gradient(90deg, #409eff, #66b1ff);
}

.gantt-progress {
  font-size: 10px;
  color: #fff;
  font-weight: 500;
  white-space: nowrap;
}

.gantt-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding-top: 8px;
  border-top: 1px solid #ebeef5;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.legend-text {
  font-size: 11px;
  color: #909399;
  margin-right: 8px;
}

/* 响应式 - 新图表 */
@media (max-width: 768px) {
  .radar-chart {
    width: 180px;
    height: 180px;
  }
  
  .efficiency-trend {
    height: 60px;
  }
  
  .efficiency-bar-wrapper {
    width: 20px;
    height: 50px;
  }
  
  .gantt-label {
    width: 32px;
    font-size: 11px;
  }
}
</style>
