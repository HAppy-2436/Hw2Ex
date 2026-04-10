<template>
  <el-card class="stat-card" :class="{ 'stat-card-clickable': clickable }">
    <div class="stat-content">
      <div class="stat-info">
        <span class="stat-label">{{ title }}</span>
        <div class="stat-value-row">
          <span class="stat-value" :style="{ color: valueColor }">{{ displayValue }}</span>
          <span v-if="suffix" class="stat-suffix">{{ suffix }}</span>
        </div>
        <span v-if="trend !== undefined" class="stat-trend" :class="trendClass">
          <el-icon v-if="trend !== 0">
            <Top v-if="trend > 0" />
            <Bottom v-else />
          </el-icon>
          {{ formatTrend }}
        </span>
        <span v-if="subtitle" class="stat-subtitle">{{ subtitle }}</span>
      </div>
      <div class="stat-icon-wrapper" :style="iconStyle">
        <el-icon class="stat-icon" :size="28">
          <component :is="iconComponent" />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Top, Bottom } from '@element-plus/icons-vue'

const props = defineProps({
  // 标题
  title: {
    type: String,
    required: true
  },
  // 数值
  value: {
    type: [Number, String],
    default: 0
  },
  // 数值后缀
  suffix: {
    type: String,
    default: ''
  },
  // 副标题
  subtitle: {
    type: String,
    default: ''
  },
  // 趋势值（正数上升，负数下降）
  trend: {
    type: Number,
    default: undefined
  },
  // 图标
  icon: {
    type: String,
    default: 'DataAnalysis'
  },
  // 图标颜色（渐变起始色）
  iconColor: {
    type: String,
    default: '#409eff'
  },
  // 数值颜色
  valueColor: {
    type: String,
    default: '#303133'
  },
  // 是否可点击
  clickable: {
    type: Boolean,
    default: false
  },
  // 数值格式化类型
  formatType: {
    type: String,
    default: 'number', // 'number' | 'percent' | 'time' | 'currency'
  }
})

// 图标组件映射
const iconMap = {
  'Clock': 'Clock',
  'Document': 'Document',
  'Star': 'Star',
  'Bell': 'Bell',
  'DataAnalysis': 'DataAnalysis',
  'TrendCharts': 'TrendCharts',
  'Histogram': 'Histogram',
  'Collection': 'Collection',
  'Reading': 'Reading',
  'Success': 'Success',
  'Warning': 'Warning',
  'Info': 'Info'
}

const iconComponent = computed(() => {
  return iconMap[props.icon] || 'DataAnalysis'
})

// 渐变背景样式
const iconStyle = computed(() => {
  const color = props.iconColor
  return {
    background: `linear-gradient(135deg, ${color}, ${adjustColor(color, 20)})`
  }
})

// 调整颜色亮度
const adjustColor = (color, percent) => {
  const num = parseInt(color.replace('#', ''), 16)
  const amt = Math.round(2.55 * percent)
  const R = (num >> 16) + amt
  const G = (num >> 8 & 0x00FF) + amt
  const B = (num & 0x0000FF) + amt
  return '#' + (
    0x1000000 +
    (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
    (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
    (B < 255 ? (B < 1 ? 0 : B) : 255)
  ).toString(16).slice(1)
}

// 格式化趋势值
const formatTrend = computed(() => {
  if (props.trend === undefined || props.trend === 0) return '持平'
  const absValue = Math.abs(props.trend)
  return `${props.trend > 0 ? '+' : '-'}${absValue}%`
})

// 趋势样式
const trendClass = computed(() => {
  if (props.trend === undefined || props.trend === 0) return 'trend-flat'
  return props.trend > 0 ? 'trend-up' : 'trend-down'
})

// 显示值格式化
const displayValue = computed(() => {
  const val = props.value
  if (val === undefined || val === null) return '0'
  
  switch (props.formatType) {
    case 'percent':
      return `${Number(val).toFixed(1)}%`
    case 'time':
      if (val >= 60) {
        const hours = Math.floor(val / 60)
        const mins = val % 60
        return mins > 0 ? `${hours}h ${mins}m` : `${hours}h`
      }
      return `${val}m`
    case 'currency':
      return `¥${Number(val).toFixed(2)}`
    default:
      return Number(val).toLocaleString()
  }
})
</script>

<style scoped>
.stat-card {
  height: 100%;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card-clickable {
  cursor: pointer;
}

.stat-card-clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value-row {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-suffix {
  font-size: 14px;
  color: #c0c4cc;
  margin-left: 2px;
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 2px;
  font-size: 12px;
  margin-top: 4px;
}

.trend-up {
  color: #67c23a;
}

.trend-down {
  color: #f56c6c;
}

.trend-flat {
  color: #909399;
}

.stat-subtitle {
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 4px;
}

.stat-icon-wrapper {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.stat-icon {
  color: #fff;
}

/* 响应式 */
@media (max-width: 768px) {
  .stat-value {
    font-size: 24px;
  }
  
  .stat-icon-wrapper {
    width: 48px;
    height: 48px;
  }
  
  .stat-icon {
    font-size: 24px;
  }
}
</style>
