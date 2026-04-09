import { defineStore } from 'pinia'
import { ref } from 'vue'
import { bookApi } from '@/api'

export const useBookStore = defineStore('books', () => {
  const books = ref([])
  const currentBook = ref(null)
  const loading = ref(false)

  const fetchBooks = async (subjectId) => {
    loading.value = true
    try {
      const data = await bookApi.list(subjectId)
      books.value = data
    } finally {
      loading.value = false
    }
  }

  const fetchBook = async (id) => {
    loading.value = true
    try {
      const data = await bookApi.detail(id)
      currentBook.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createBook = async (data) => {
    loading.value = true
    try {
      const result = await bookApi.create(data)
      return result
    } finally {
      loading.value = false
    }
  }

  const updateBook = async (id, data) => {
    loading.value = true
    try {
      const result = await bookApi.update(id, data)
      return result
    } finally {
      loading.value = false
    }
  }

  const deleteBook = async (id) => {
    loading.value = true
    try {
      const result = await bookApi.delete(id)
      return result
    } finally {
      loading.value = false
    }
  }

  return {
    books,
    currentBook,
    loading,
    fetchBooks,
    fetchBook,
    createBook,
    updateBook,
    deleteBook
  }
})