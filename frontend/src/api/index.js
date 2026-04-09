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
  getAnswer: (homeworkId) => api.get(`/ai/answer/${homeworkId}`)
}

// ============ 学习记录 API ============
export const learnApi = {
  // 记录学习进度
  recordProgress: (data) => api.post('/learn/progress', data),
  // 获取学习记录
  getRecords: (params) => api.get('/learn/records', { params })
}

// ============ 复习 API ============
export const reviewApi = {
  // 获取复习计划
  getPlan: () => api.get('/review/plan'),
  // 记录复习
  record: (data) => api.post('/review/record', data),
  // 获取复习统计
  getStats: () => api.get('/review/stats')
}

export default api