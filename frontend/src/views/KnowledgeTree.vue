<template>
  <div class="knowledge-tree">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>知识树</h1>
          <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
            添加节点
          </el-button>
        </div>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <!-- 知识树 -->
          <el-col :xs="24" :lg="expandedNodeId ? 14 : 24">
            <el-card>
              <template #header>
                <div class="tree-header">
                  <span>知识结构图</span>
                  <div class="tree-controls">
                    <el-button link @click="expandAll" size="small">全部展开</el-button>
                    <el-button link @click="collapseAll" size="small">全部折叠</el-button>
                  </div>
                </div>
              </template>
              <div v-if="tree.length > 0" class="tree-container">
                <el-tree
                  ref="treeRef"
                  :data="tree"
                  :props="treeProps"
                  node-key="id"
                  :expand-on-click-node="false"
                  :default-expand-all="false"
                  @node-click="handleNodeClick"
                  :current-node-key="expandedNodeId"
                >
                  <template #default="{ node, data }">
                    <span class="custom-tree-node">
                      <span class="node-label">
                        <el-icon v-if="data.children?.length"><Folder /></el-icon>
                        <el-icon v-else><Document /></el-icon>
                        {{ node.label }}
                      </span>
                      <span class="node-actions">
                        <el-tag size="small" type="info">{{ data.child_count || 0 }}</el-tag>
                        <el-dropdown trigger="click" @command="(cmd) => handleNodeCommand(cmd, data)">
                          <el-button link :icon="MoreFilled" @click.stop />
                          <template #dropdown>
                            <el-dropdown-menu>
                              <el-dropdown-item command="add">添加子节点</el-dropdown-item>
                              <el-dropdown-item command="edit">编辑</el-dropdown-item>
                              <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                            </el-dropdown-menu>
                          </template>
                        </el-dropdown>
                      </span>
                    </span>
                  </template>
                </el-tree>
              </div>
              <el-skeleton v-else-if="loading" :rows="10" animated />
              <el-empty v-else description="暂无知识树数据">
                <el-button type="primary" @click="showCreateDialog = true">添加第一个节点</el-button>
              </el-empty>
            </el-card>
          </el-col>

          <!-- 节点详情面板 -->
          <el-col :xs="24" :lg="10" v-if="expandedNodeId">
            <el-card class="node-detail-card">
              <template #header>
                <span>节点详情</span>
                <el-button link :icon="Close" @click="closeDetail" />
              </template>
              <div v-if="currentNode" class="node-detail">
                <el-descriptions :column="1" border size="small">
                  <el-descriptions-item label="节点名称">
                    {{ currentNode.name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="节点描述">
                    {{ currentNode.description || '暂无描述' }}
                  </el-descriptions-item>
                  <el-descriptions-item label="相关内容">
                    <div class="related-content">
                      <p v-if="currentNode.content">{{ currentNode.content }}</p>
                      <p v-else class="no-content">暂无内容</p>
                    </div>
                  </el-descriptions-item>
                </el-descriptions>

                <!-- 相关作业 -->
                <div class="related-homework" v-if="currentNodeHomeworks.length > 0">
                  <h4>相关作业</h4>
                  <div class="homework-list">
                    <el-tag
                      v-for="hw in currentNodeHomeworks"
                      :key="hw.id"
                      class="homework-tag"
                      @click="goToHomework(hw.id)"
                    >
                      {{ hw.title }}
                    </el-tag>
                  </div>
                </div>

                <div class="detail-actions">
                  <el-button type="primary" @click="goToNodeHomeworks">
                    查看相关作业
                  </el-button>
                </div>
              </div>
              <el-skeleton v-else-if="detailLoading" :rows="5" animated />
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>

    <!-- 创建/编辑节点对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingNode ? '编辑节点' : '创建节点'"
      width="500px"
      @close="resetNodeForm"
    >
      <el-form ref="nodeFormRef" :model="nodeForm" :rules="nodeRules" label-width="80px">
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="nodeForm.name" placeholder="输入节点名称" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="节点描述" prop="description">
          <el-input
            v-model="nodeForm.description"
            type="textarea"
            :rows="2"
            placeholder="简要描述..."
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="详细内容" prop="content">
          <el-input
            v-model="nodeForm.content"
            type="textarea"
            :rows="4"
            placeholder="节点的具体内容..."
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="父节点" v-if="parentNodeOptions.length > 0">
          <el-cascader
            v-model="nodeForm.parent_id"
            :options="parentNodeOptions"
            :props="{ checkStrictly: true, emitPath: false, label: 'name', value: 'id' }"
            placeholder="选择父节点（留空为根节点）"
            clearable
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="handleNodeSubmit" :loading="nodeSubmitting">
          {{ editingNode ? '保存' : '创建' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNodeStore } from '@/stores/nodes'
import { useHomeworkStore } from '@/stores/homework'
import { nodeApi } from '@/api'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Plus, MoreFilled, Close, Folder, Document } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const nodeStore = useNodeStore()
const homeworkStore = useHomeworkStore()
const { tree, loading } = storeToRefs(nodeStore)
const { homeworks } = storeToRefs(homeworkStore)

const treeRef = ref(null)
const expandedNodeId = ref(null)
const currentNode = ref(null)
const detailLoading = ref(false)

const showCreateDialog = ref(false)
const nodeSubmitting = ref(false)
const editingNode = ref(null)
const nodeFormRef = ref(null)

const nodeForm = reactive({
  name: '',
  description: '',
  content: '',
  parent_id: null,
  book_id: route.params.id
})

const nodeRules = {
  name: [
    { required: true, message: '请输入节点名称', trigger: 'blur' },
    { min: 1, max: 100, message: '名称长度在 1 到 100 个字符', trigger: 'blur' }
  ]
}

const treeProps = {
  children: 'children',
  label: 'name'
}

// 获取父节点选项（用于创建子节点时选择）
const parentNodeOptions = computed(() => {
  const flattenNodes = (nodes, result = []) => {
    nodes.forEach(node => {
      result.push({ id: node.id, name: node.name })
      if (node.children?.length) {
        flattenNodes(node.children, result)
      }
    })
    return result
  }
  return flattenNodes(tree.value)
})

// 当前节点的作业列表
const currentNodeHomeworks = computed(() => {
  if (!currentNode.value) return []
  return homeworks.value.filter(hw => hw.node_id === currentNode.value.id)
})

onMounted(async () => {
  const bookId = route.params.id
  await nodeStore.fetchTree(bookId)
  await homeworkStore.fetchHomeworks({ node_id: null, page: 1, page_size: 100 })
})

const handleNodeClick = async (data) => {
  expandedNodeId.value = data.id
  detailLoading.value = true
  try {
    currentNode.value = await nodeStore.fetchNode(data.id)
  } finally {
    detailLoading.value = false
  }
}

const closeDetail = () => {
  expandedNodeId.value = null
  currentNode.value = null
}

const expandAll = () => {
  const nodes = treeRef.value?.store?.nodesMap || {}
  Object.values(nodes).forEach(node => {
    node.expand()
  })
}

const collapseAll = () => {
  const nodes = treeRef.value?.store?.nodesMap || {}
  Object.values(nodes).forEach(node => {
    node.collapse()
  })
}

const handleNodeCommand = (command, node) => {
  if (command === 'add') {
    editingNode.value = null
    nodeForm.name = ''
    nodeForm.description = ''
    nodeForm.content = ''
    nodeForm.parent_id = node.id
    nodeForm.book_id = route.params.id
    showCreateDialog.value = true
  } else if (command === 'edit') {
    editingNode.value = node
    nodeForm.name = node.name
    nodeForm.description = node.description || ''
    nodeForm.content = node.content || ''
    nodeForm.parent_id = node.parent_id
    nodeForm.book_id = route.params.id
    showCreateDialog.value = true
  } else if (command === 'delete') {
    handleNodeDelete(node)
  }
}

const handleNodeSubmit = async () => {
  if (!nodeFormRef.value) return
  
  await nodeFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    nodeSubmitting.value = true
    try {
      const data = {
        name: nodeForm.name,
        description: nodeForm.description,
        content: nodeForm.content,
        book_id: nodeForm.book_id,
        parent_id: nodeForm.parent_id || null
      }
      
      if (editingNode.value) {
        await nodeApi.update(editingNode.value.id, data)
        ElMessage.success('节点更新成功')
      } else {
        await nodeApi.create(data)
        ElMessage.success('节点创建成功')
      }
      
      showCreateDialog.value = false
      resetNodeForm()
      await nodeStore.fetchTree(route.params.id)
    } catch (error) {
      // Error handled by interceptor
    } finally {
      nodeSubmitting.value = false
    }
  })
}

const handleNodeDelete = async (node) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除节点 "${node.name}" 吗？${node.child_count > 0 ? '该节点下有子节点，也将一并删除。' : ''}`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    await nodeApi.delete(node.id)
    ElMessage.success('删除成功')
    
    if (expandedNodeId.value === node.id) {
      closeDetail()
    }
    
    await nodeStore.fetchTree(route.params.id)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const resetNodeForm = () => {
  nodeForm.name = ''
  nodeForm.description = ''
  nodeForm.content = ''
  nodeForm.parent_id = null
  nodeForm.book_id = route.params.id
  editingNode.value = null
  nodeFormRef.value?.resetFields()
}

const goToHomework = (homeworkId) => {
  router.push(`/homeworks/${homeworkId}`)
}

const goToNodeHomeworks = () => {
  if (currentNode.value) {
    router.push(`/homeworks?node_id=${currentNode.value.id}`)
  }
}
</script>

<style scoped>
.knowledge-tree {
  min-height: 100vh;
  background: #f5f7fa;
}

.el-header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-content h1 {
  font-size: 24px;
  color: #333;
  flex: 1;
}

.el-main {
  padding: 20px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tree-controls {
  display: flex;
  gap: 10px;
}

.tree-container {
  min-height: 400px;
}

.custom-tree-node {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding-right: 10px;
}

.node-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-detail-card {
  position: sticky;
  top: 20px;
}

.node-detail {
  padding: 10px 0;
}

.related-content {
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  min-height: 60px;
}

.no-content {
  color: #999;
  font-style: italic;
}

.related-homework {
  margin-top: 20px;
}

.related-homework h4 {
  margin-bottom: 10px;
  color: #333;
}

.homework-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.homework-tag {
  cursor: pointer;
}

.homework-tag:hover {
  opacity: 0.8;
}

.detail-actions {
  margin-top: 20px;
  text-align: center;
}
</style>