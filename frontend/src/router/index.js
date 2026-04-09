import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/subjects'
  },
  {
    path: '/dashboard',
    name: 'LearningDashboard',
    component: () => import('@/views/LearningDashboard.vue'),
    meta: { title: '学习仪表盘' }
  },
  {
    path: '/token-usage',
    name: 'TokenUsage',
    component: () => import('@/views/TokenUsage.vue'),
    meta: { title: 'Token使用统计' }
  },
  {
    path: '/subjects',
    name: 'SubjectList',
    component: () => import('@/views/SubjectList.vue'),
    meta: { title: '学科列表' }
  },
  {
    path: '/books/:id',
    name: 'BookDetail',
    component: () => import('@/views/BookDetail.vue'),
    meta: { title: '教材详情' }
  },
  {
    path: '/nodes/:id',
    name: 'KnowledgeTree',
    component: () => import('@/views/KnowledgeTree.vue'),
    meta: { title: '知识树' }
  },
  {
    path: '/homeworks',
    name: 'HomeworkList',
    component: () => import('@/views/HomeworkList.vue'),
    meta: { title: '作业列表' }
  },
  {
    path: '/homeworks/:id',
    name: 'HomeworkDetail',
    component: () => import('@/views/HomeworkDetail.vue'),
    meta: { title: '作业详情' }
  },
  // ============ 复习模式路由 ============
  {
    path: '/review/plans',
    name: 'ReviewPlan',
    component: () => import('@/views/ReviewPlan.vue'),
    meta: { title: '复习计划' }
  },
  {
    path: '/review/:id/checkpoints',
    name: 'ReviewCheckpoints',
    component: () => import('@/views/ReviewCheckpoints.vue'),
    meta: { title: '知识点清单' }
  },
  {
    path: '/review/:id/suggestions',
    name: 'ReviewSuggestions',
    component: () => import('@/views/ReviewSuggestions.vue'),
    meta: { title: '复习建议' }
  },
  {
    path: '/review/:id/chat',
    name: 'AIChat',
    component: () => import('@/views/AIChat.vue'),
    meta: { title: 'AI问答' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - StudyMate` : 'StudyMate'
  next()
})

export default router
