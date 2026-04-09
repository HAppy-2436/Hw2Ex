import { defineStore } from 'pinia'
import { ref } from 'vue'
import { homeworkApi } from '@/api'

export const useHomeworkStore = defineStore('homework', () => {
  const homeworks = ref([])
  const currentHomework = ref(null)
  const feedback = ref(null)
  const loading = ref(false)

  const fetchHomeworks = async (params) => {
    loading.value = true
    try {
      const data = await homeworkApi.list(params)
      homeworks.value = data.items || data
      return data
    } finally {
      loading.value = false
    }
  }

  const fetchHomework = async (id) => {
    loading.value = true
    try {
      const data = await homeworkApi.detail(id)
      currentHomework.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const submitHomework = async (id, answers) => {
    loading.value = true
    try {
      const data = await homeworkApi.submit(id, answers)
      return data
    } finally {
      loading.value = false
    }
  }

  const fetchFeedback = async (id) => {
    loading.value = true
    try {
      const data = await homeworkApi.feedback(id)
      feedback.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createHomework = async (data) => {
    loading.value = true
    try {
      const result = await homeworkApi.create(data)
      return result
    } finally {
      loading.value = false
    }
  }

  const updateHomework = async (id, data) => {
    loading.value = true
    try {
      const result = await homeworkApi.update(id, data)
      return result
    } finally {
      loading.value = false
    }
  }

  const deleteHomework = async (id) => {
    loading.value = true
    try {
      const result = await homeworkApi.delete(id)
      return result
    } finally {
      loading.value = false
    }
  }

  return {
    homeworks,
    currentHomework,
    feedback,
    loading,
    fetchHomeworks,
    fetchHomework,
    submitHomework,
    fetchFeedback,
    createHomework,
    updateHomework,
    deleteHomework
  }
})