<template>
  <div class="book-detail">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>{{ book?.name || '教材详情' }}</h1>
        </div>
      </el-header>
      <el-main>
        <el-card v-if="book">
          <template #header>
            <span>教材信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="教材名称">{{ book.name }}</el-descriptions-item>
            <el-descriptions-item label="学科">{{ book.subject_name }}</el-descriptions-item>
            <el-descriptions-item label="出版社">{{ book.publisher || '未知' }}</el-descriptions-item>
            <el-descriptions-item label="知识点数量">{{ book.node_count || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="tree-card" v-if="book">
          <template #header>
            <span>知识树</span>
            <el-button type="primary" size="small" @click="goToKnowledgeTree">
              查看完整知识树
            </el-button>
          </template>
          <div v-if="tree.length > 0" class="tree-preview">
            <el-tree
              :data="tree"
              :props="{ children: 'children', label: 'name' }"
              default-expand-all
              @node-click="handleNodeClick"
            />
          </div>
          <el-empty v-else description="暂无知识树数据" />
        </el-card>

        <el-skeleton v-if="loading" :rows="5" animated />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useBookStore } from '@/stores/books'
import { useNodeStore } from '@/stores/nodes'
import { storeToRefs } from 'pinia'
import { ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const bookStore = useBookStore()
const nodeStore = useNodeStore()

const { currentBook: book, loading } = storeToRefs(bookStore)
const { tree } = storeToRefs(nodeStore)

onMounted(async () => {
  const bookId = route.params.id
  await bookStore.fetchBook(bookId)
  await nodeStore.fetchTree(bookId)
})

const goToKnowledgeTree = () => {
  router.push(`/nodes/${route.params.id}`)
}

const handleNodeClick = (data) => {
  router.push(`/homeworks?node_id=${data.id}`)
}
</script>

<style scoped>
.book-detail {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-content h1 {
  font-size: 24px;
  color: #333;
}

.el-main {
  padding: 20px;
}

.tree-card {
  margin-top: 20px;
}

.tree-preview {
  max-height: 400px;
  overflow-y: auto;
}
</style>
