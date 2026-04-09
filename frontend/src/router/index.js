import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/subjects'
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
