<template>
  <div class="token-usage">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>Token 使用统计</h1>
          <el-date-picker
            v-model="selectedDate"
            type="month"
            placeholder="选择月份"
            value-format="YYYY-MM"
            @change="handleDateChange"
          />
        </div>
      </el-header>
      <el-main>
        <!-- 时间切换Tab -->
        <el-tabs v-model="activeTab" @tab-change="handleTabChange">
          <el-tab-pane label="今日" name="today" />
          <el-tab-pane label="本周" name="week" />
          <el-tab-pane label="本月" name="month" />
        </el-tabs>

        <!-- 统计卡片 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :xs="24" :sm="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon token-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-label">{{ currentPeriodLabel }} Token 消耗</span>
                  <span class="stat-value">{{ formattedTokenUsage }}</span>
                  <span class="stat-unit">tokens</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon api-icon">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-label">{{ currentPeriodLabel }} API 调用</span>
                  <span class="stat-value">{{ apiCalls }}</span>
                  <span class="stat-unit">次</span>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :xs="24" :sm="8">
            <el-card class="stat-card">
              <div class="stat-content">
                <div class="stat-icon cost-icon">
                  <el-icon><Money /></el-icon>
                </div>
                <div class="stat-info">
                  <span class="stat-label">{{ currentPeriodLabel }} 预估成本</span>
                  <span class="stat-value">¥{{ estimatedCost }}</span>
                  <span class="stat-unit">≈ {{ realCost }}</span>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- Token消耗趋势图 -->
        <el-row :gutter="20" class="chart-row">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>Token 消耗趋势</span>
                  <el-select v-model="trendType" size="small" style="width: 100px;">
                    <el-option label="按小时" value="hourly" v-if="activeTab === 'today'" />
                    <el-option label="按天" value="daily" />
                    <el-option label="按周" value="weekly" />
                  </el-select>
                </div>
              </template>
              <div class="chart-container">
                <div class="area-chart">
                  <svg :viewBox="`0 0 ${trendData.length * 60} 180`" preserveAspectRatio="xMidYMid meet">
                    <!-- 网格线 -->
                    <line 
                      v-for="i in 4" 
                      :key="'grid-'+i"
                      :x1="0" 
                      :y1="(i * 40)"
                      :x2="trendData.length * 60" 
                      :y2="(i * 40)"
                      stroke="#ebeef5"
                      stroke-width="1"
                    />
                    <!-- 面积 -->
                    <polygon
                      :points="areaPoints"
                      fill="url(#areaGradient)"
                      opacity="0.6"
                    />
                    <!-- 折线 -->
                    <polyline
                      :points="linePoints"
                      fill="none"
                      stroke="#409eff"
                      stroke-width="2"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <!-- 数据点 -->
                    <circle
                      v-for="(point, index) in chartPoints"
                      :key="'point-'+index"
                      :cx="point.x"
                      :cy="point.y"
                      r="3"
                      fill="#409eff"
                      @mouseenter="showTooltip(point, $event)"
                      @mouseleave="hideTooltip"
                    />
                    <!-- 渐变定义 -->
                    <defs>
                      <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#409eff" stop-opacity="0.8" />
                        <stop offset="100%" stop-color="#409eff" stop-opacity="0.1" />
                      </linearGradient>
                    </defs>
                  </svg>
                  <!-- 工具提示 -->
                  <div 
                    v-if="tooltipVisible"
                    class="chart-tooltip"
                    :style="{ left: tooltipX + 'px', top: tooltipY + 'px' }"
                  >
                    <div class="tooltip-content">
                      <span class="tooltip-label">{{ tooltipData.label }}</span>
                      <span class="tooltip-value">{{ tooltipData.value }} tokens</span>
                    </div>
                  </div>
                  <div class="chart-labels">
                    <span 
                      v-for="(item, index) in trendData" 
                      :key="'label-'+index"
                      class="chart-label"
                    >
                      {{ item.label }}
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 详细数据表格 -->
        <el-row :gutter="20" class="table-row">
          <el-col :span="24">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>使用明细</span>
                  <el-button type="primary" link :icon="Download" @click="exportData">
                    导出数据
                  </el-button>
                </div>
              </template>
              <el-table :data="usageDetails" stripe v-loading="loading">
                <el-table-column prop="date" label="时间" width="180">
                  <template #default="{ row }">
                    {{ formatDateTime(row.date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="type" label="调用类型" width="120">
                  <template #default="{ row }">
                    <el-tag size="small" :type="getTypeTagType(row.type)">
                      {{ getTypeName(row.type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="input_tokens" label="输入 Token" width="120" align="right">
                  <template #default="{ row }">
                    {{ row.input_tokens.toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="output_tokens" label="输出 Token" width="120" align="right">
                  <template #default="{ row }">
                    {{ row.output_tokens.toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="total_tokens" label="合计" width="120" align="right">
                  <template #default="{ row }">
                    <span class="total-tokens">{{ row.total_tokens.toLocaleString() }}</span>
                  </template>
                </el-table-column>
                <el-table-column prop="cost" label="预估成本" width="100" align="right">
                  <template #default="{ row }">
                    ¥{{ row.cost.toFixed(4) }}
                  </template>
                </el-table-column>
              </el-table>
              <div class="table-footer" v-if="totalPages > 1">
                <el-pagination
                  v-model:current-page="currentPage"
                  :page-size="pageSize"
                  :total="totalRecords"
                  layout="prev, pager, next"
                  @current-change="handlePageChange"
                />
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 费用说明 -->
        <el-row :gutter="20" class="info-row">
          <el-col :span="24">
            <el-card>
              <template #header>
                <span>费用说明</span>
              </template>
              <div class="cost-info">
                <el-descriptions :column="2" border>
                  <el-descriptions-item label="输入 Token 单价">
                    $0.001 / 1K tokens (约 ¥0.007 / 1K)
                  </el-descriptions-item>
                  <el-descriptions-item label="输出 Token 单价">
                    $0.002 / 1K tokens (约 ¥0.014 / 1K)
                  </el-descriptions-item>
                  <el-descriptions-item label="计费模型">
                    GPT-3.5-Turbo
                  </el-descriptions-item>
                  <el-descriptions-item label="免费额度">
                    每月 100K tokens
                  </el-descriptions-item>
                </el-descriptions>
              </div>
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
import { ArrowLeft, Cpu, Connection, Money, Download } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()

// 状态
const activeTab = ref('today')
const selectedDate = ref('')
const trendType = ref('daily')
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const totalRecords = ref(0)

// 数据
const tokenUsage = ref(0)
const apiCalls = ref(0)
const estimatedCost = ref(0)
const realCost = ref('')
const trendData = ref([])
const usageDetails = ref([])

// 计算属性
const currentPeriodLabel = computed(() => {
  const labels = { today: '今日', week: '本周', month: '本月' }
  return labels[activeTab.value] || '今日'
})

const formattedTokenUsage = computed(() => {
  return tokenUsage.value.toLocaleString()
})

const totalPages = computed(() => {
  return Math.ceil(totalRecords.value / pageSize.value)
})

const chartPoints = computed(() => {
  if (!trendData.value.length) return []
  
  const maxValue = Math.max(...trendData.value.map(d => d.value), 1)
  const width = trendData.value.length * 60
  const height = 140
  
  return trendData.value.map((item, index) => ({
    x: index * 60 + 30,
    y: height - (item.value / maxValue) * height + 20,
    value: item.value,
    label: item.label
  }))
})

const linePoints = computed(() => {
  return chartPoints.value.map(p => `${p.x},${p.y}`).join(' ')
})

const areaPoints = computed(() => {
  if (!chartPoints.value.length) return ''
  const points = chartPoints.value.map(p => `${p.x},${p.y}`)
  const lastX = chartPoints.value[chartPoints.value.length - 1]?.x || 0
  const firstX = chartPoints.value[0]?.x || 0
  return `${firstX},160 ${points.join(' ')} ${lastX},160`
})

// 工具提示
const tooltipVisible = ref(false)
const tooltipX = ref(0)
const tooltipY = ref(0)
const tooltipData = ref({})

// 方法
const handleTabChange = () => {
  currentPage.value = 1
  loadTokenUsageData()
  loadUsageDetails()
}

const handleDateChange = () => {
  loadTokenUsageData()
  loadUsageDetails()
}

const handlePageChange = () => {
  loadUsageDetails()
}

const showTooltip = (point, event) => {
  tooltipVisible.value = true
  tooltipX.value = event.offsetX + 10
  tooltipY.value = event.offsetY - 30
  tooltipData.value = { label: point.label, value: point.value.toLocaleString() }
}

const hideTooltip = () => {
  tooltipVisible.value = false
}

const getTypeTagType = (type) => {
  const types = {
    chat: 'primary',
    analyze: 'success',
    answer: 'warning',
    suggestion: 'info'
  }
  return types[type] || 'info'
}

const getTypeName = (type) => {
  const names = {
    chat: 'AI聊天',
    analyze: '解题分析',
    answer: '答案获取',
    suggestion: '复习建议'
  }
  return names[type] || type
}

const formatDateTime = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const exportData = () => {
  ElMessage.success('数据导出功能开发中')
}

const loadTokenUsageData = async () => {
  // 模拟数据
  let tokens = 0
  let calls = 0
  let cost = 0
  
  switch (activeTab.value) {
    case 'today':
      tokens = 12580
      calls = 24
      cost = 0.025
      trendData.value = generateHourlyData()
      break
    case 'week':
      tokens = 89500
      calls = 156
      cost = 0.179
      trendData.value = generateDailyData()
      break
    case 'month':
      tokens = 358000
      calls = 624
      cost = 0.716
      trendData.value = generateMonthlyData()
      break
  }
  
  tokenUsage.value = tokens
  apiCalls.value = calls
  estimatedCost.value = cost.toFixed(3)
  realCost.value = `≈ ¥${(cost * 7).toFixed(2)}`
}

const loadUsageDetails = () => {
  loading.value = true
  
  setTimeout(() => {
    usageDetails.value = Array.from({ length: 10 }, (_, i) => ({
      date: new Date(Date.now() - i * 3600000).toISOString(),
      type: ['chat', 'analyze', 'answer', 'suggestion'][i % 4],
      input_tokens: Math.floor(Math.random() * 2000) + 500,
      output_tokens: Math.floor(Math.random() * 3000) + 200,
      total_tokens: 0,
      cost: 0
    })).map(item => ({
      ...item,
      total_tokens: item.input_tokens + item.output_tokens,
      cost: (item.input_tokens * 0.001 + item.output_tokens * 0.002) / 1000
    }))
    
    totalRecords.value = 45
    loading.value = false
  }, 300)
}

const generateHourlyData = () => {
  const hours = []
  for (let i = 0; i < 24; i++) {
    hours.push({
      label: `${i}:00`,
      value: Math.floor(Math.random() * 1500) + 200
    })
  }
  return hours
}

const generateDailyData = () => {
  const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return days.map(label => ({
    label,
    value: Math.floor(Math.random() * 15000) + 5000
  }))
}

const generateMonthlyData = () => {
  const weeks = ['第1周', '第2周', '第3周', '第4周']
  return weeks.map(label => ({
    label,
    value: Math.floor(Math.random() * 100000) + 50000
  }))
}

onMounted(() => {
  loadTokenUsageData()
  loadUsageDetails()
})
</script>

<style scoped>
.token-usage {
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
  color: #303133;
  flex: 1;
  margin: 0;
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
  align-items: center;
  gap: 16px;
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

.token-icon {
  background: linear-gradient(135deg, #f56c6c, #f78989);
}

.api-icon {
  background: linear-gradient(135deg, #409eff, #66b1ff);
}

.cost-icon {
  background: linear-gradient(135deg, #67c23a, #85ce61);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-unit {
  font-size: 12px;
  color: #c0c4cc;
}

.chart-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  padding: 20px 0;
  position: relative;
}

.area-chart {
  width: 100%;
  height: 200px;
  overflow-x: auto;
}

.area-chart svg {
  width: 100%;
  min-width: 600px;
  height: 100%;
}

.chart-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 10;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tooltip-label {
  color: #c0c4cc;
}

.tooltip-value {
  font-weight: 500;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  padding: 0 30px;
  margin-top: 8px;
}

.chart-label {
  font-size: 11px;
  color: #909399;
}

.table-row {
  margin-bottom: 20px;
}

.table-footer {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.total-tokens {
  font-weight: 500;
  color: #409eff;
}

.info-row {
  margin-bottom: 20px;
}

.cost-info {
  padding: 10px 0;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
  }
  
  .header-content h1 {
    font-size: 20px;
    order: 1;
    width: 100%;
    text-align: center;
    margin-bottom: 12px;
  }
  
  .header-content .el-button {
    order: 2;
  }
  
  .header-content .el-date-picker {
    order: 3;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
  }
  
  .area-chart {
    overflow-x: scroll;
  }
  
  .area-chart svg {
    min-width: 800px;
  }
}
</style>
