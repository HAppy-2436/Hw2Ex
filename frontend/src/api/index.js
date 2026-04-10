import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.message || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// ============ 学科 API ============
export const subjectApi = {
  list: () => api.get('/subjects'),
  detail: (id) => api.get(`/subjects/${id}`),
  create: (data) => api.post('/subjects', data),
  update: (id, data) => api.put(`/subjects/${id}`, data),
  delete: (id) => api.delete(`/subjects/${id}`)
}

// ============ 教材 API ============
export const bookApi = {
  list: (subjectId) => api.get(`/books`, { params: { subject_id: subjectId } }),
  detail: (id) => api.get(`/books/${id}`),
  create: (data) => api.post('/books', data),
  update: (id, data) => api.put(`/books/${id}`, data),
  delete: (id) => api.delete(`/books/${id}`)
}

// ============ 知识节点 API ============
export const nodeApi = {
  tree: (bookId) => api.get(`/nodes/tree`, { params: { book_id: bookId } }),
  detail: (id) => api.get(`/nodes/${id}`),
  create: (data) => api.post('/nodes', data),
  update: (id, data) => api.put(`/nodes/${id}`, data),
  delete: (id) => api.delete(`/nodes/${id}`)
}

// ============ 作业 API ============
export const homeworkApi = {
  list: (params) => api.get('/homeworks', { params }),
  detail: (id) => api.get(`/homeworks/${id}`),
  create: (data) => api.post('/homeworks', data),
  update: (id, data) => api.put(`/homeworks/${id}`, data),
  delete: (id) => api.delete(`/homeworks/${id}`),
  submit: (id, data) => api.post(`/homeworks/${id}/submit`, data),
  feedback: (id) => api.get(`/homeworks/${id}/feedback`)
}

// ============ AI API ============
export const aiApi = {
  // 提交解题思路，获取AI分析
  analyzeSolution: (homeworkId, data) => api.post(`/ai/analyze`, {
    homework_id: homeworkId,
    user_solution: data.user_solution
  }),
  // 获取AI答案
  getAnswer: (homeworkId) => api.get(`/ai/answer/${homeworkId}`),
  // AI聊天（带上下文）
  chat: (context, data) => api.post('/ai/chat', {
    context,
    message: data.message
  }),
  // 获取Token使用统计
  getTokenUsage: (params) => api.get('/ai/token-usage', { params })
}

// ============ 学习记录 API ============
export const learnApi = {
  // 获取学习记录
  getRecords: (params) => api.get('/learning/records', { params }),
  // 创建学习记录
  createRecord: (data) => api.post('/learning/records', data),
  // 获取学习记录详情
  getRecordDetail: (id) => api.get(`/learning/records/${id}`),
  // 更新学习记录
  updateRecord: (id, data) => api.put(`/learning/records/${id}`, data),
  // 删除学习记录
  deleteRecord: (id) => api.delete(`/learning/records/${id}`),
  
  // 获取知识点学习状态
  getNodeStatus: (nodeId) => api.get(`/learning/nodes/${nodeId}/status`),
  
  // 获取学习统计
  getStats: () => api.get('/learning/stats'),
  
  // 获取复习计划
  getReviewPlan: (days) => api.get('/learning/review-plan', { params: { days } })
}

// ============ 学习时长统计 API ============
export const learningStatsApi = {
  // 获取本周学习时长（按天统计）
  getWeeklyStats: () => api.get('/learning/weekly-stats'),
  // 获取知识点掌握度分布
  getMasteryDistribution: () => api.get('/learning/mastery-distribution'),
  // 获取学习进度趋势
  getProgressTrend: (days) => api.get('/learning/progress-trend', { params: { days } })
}

// ============ 复习计划 API ============
export const reviewApi = {
  // 获取复习计划列表
  getPlans: (params) => api.get('/review/plans', { params }),
  // 获取复习计划详情
  getPlanDetail: (id) => api.get(`/review/plans/${id}`),
  // 创建复习计划
  createPlan: (data) => api.post('/review/plans', data),
  // 更新复习计划
  updatePlan: (id, data) => api.put(`/review/plans/${id}`, data),
  // 删除复习计划
  deletePlan: (id) => api.delete(`/review/plans/${id}`),
  
  // ============ 复习知识点清单 API ============
  // 获取复习计划包含的知识点清单
  getCheckpoints: (planId) => api.get(`/review/plans/${planId}/checkpoints`),
  // 创建复习知识点
  createCheckpoint: (planId, data) => api.post(`/review/plans/${planId}/checkpoints`, data),
  // 更新复习知识点
  updateCheckpoint: (checkpointId, data) => api.put(`/review/checkpoints/${checkpointId}`, data),
  // 删除复习知识点
  deleteCheckpoint: (checkpointId) => api.delete(`/review/checkpoints/${checkpointId}`),
  
  // ============ 复习建议 API ============
  // 获取基于遗忘曲线的复习建议
  getSuggestions: (planId) => api.get(`/review/plans/${planId}/suggestions`),
  
  // ============ 遗留的旧API（兼容） ============
  // 获取复习计划
  getPlan: () => api.get('/review/plan'),
  // 记录复习
  record: (data) => api.post('/review/record', data),
  // 获取复习统计
  getStats: () => api.get('/review/stats')
}

// ============ 分析统计 API ============
export const analyticsApi = {
  // 获取学习效率趋势
  getEfficiencyTrend: (params) => api.get('/analytics/efficiency-trend', { params }),
  // 获取知识点掌握度
  getMasteryRadar: () => api.get('/analytics/mastery-radar'),
  // 获取复习进度
  getReviewGantt: () => api.get('/analytics/review-gantt')
}

// ============ 报告 API ============
export const reportsApi = {
  // 获取复习报告
  getReviewReport: (planId) => api.get(`/reports/review/${planId}`),
  // 获取学习报告
  getLearningReport: (params) => api.get('/reports/learning', { params })
}

export default api
