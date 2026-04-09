import { defineStore } from 'pinia'
import { ref } from 'vue'
import { nodeApi } from '@/api'

export const useNodeStore = defineStore('nodes', () => {
  const tree = ref([])
  const currentNode = ref(null)
  const loading = ref(false)

  const fetchTree = async (bookId) => {
    loading.value = true
    try {
      const data = await nodeApi.tree(bookId)
      tree.value = data
    } finally {
      loading.value = false
    }
  }

  const fetchNode = async (id) => {
    loading.value = true
    try {
      const data = await nodeApi.detail(id)
      currentNode.value = data
      return data
    } finally {
      loading.value = false
    }
  }

  const createNode = async (data) => {
    loading.value = true
    try {
      const result = await nodeApi.create(data)
      return result
    } finally {
      loading.value = false
    }
  }

  const updateNode = async (id, data) => {
    loading.value = true
    try {
      const result = await nodeApi.update(id, data)
      return result
    } finally {
      loading.value = false
    }
  }

  const deleteNode = async (id) => {
    loading.value = true
    try {
      const result = await nodeApi.delete(id)
      return result
    } finally {
      loading.value = false
    }
  }

  return {
    tree,
    currentNode,
    loading,
    fetchTree,
    fetchNode,
    createNode,
    updateNode,
    deleteNode
  }
})