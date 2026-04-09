import { defineStore } from 'pinia'
import { ref } from 'vue'
import { subjectApi } from '@/api'

export const useSubjectStore = defineStore('subjects', () => {
  const subjects = ref([])
  const currentSubject = ref(null)
  const loading = ref(false)

  const fetchSubjects = async () => {
    loading.value = true
    try {
      const data = await subjectApi.list()
      subjects.value = data
    } finally {
      loading.value = false
    }
  }

  const fetchSubject = async (id) => {
    loading.value = true
    try {
      const data = await subjectApi.detail(id)
      currentSubject.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createSubject = async (data) => {
    loading.value = true
    try {
      const result = await subjectApi.create(data)
      await fetchSubjects()
      return result
    } finally {
      loading.value = false
    }
  }

  const updateSubject = async (id, data) => {
    loading.value = true
    try {
      const result = await subjectApi.update(id, data)
      await fetchSubjects()
      return result
    } finally {
      loading.value = false
    }
  }

  const deleteSubject = async (id) => {
    loading.value = true
    try {
      const result = await subjectApi.delete(id)
      await fetchSubjects()
      return result
    } finally {
      loading.value = false
    }
  }

  return {
    subjects,
    currentSubject,
    loading,
    fetchSubjects,
    fetchSubject,
    createSubject,
    updateSubject,
    deleteSubject
  }
})