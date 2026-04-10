<template>
  <div class="study-mode">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>学习模式</h1>
          <div class="header-actions">
            <el-button type="primary" @click="showNodeSelector = true">
              选择知识点
            </el-button>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <el-row :gutter="20">
          <!-- 左侧：知识内容 -->
          <el-col :span="16">
            <el-card v-loading="loadingNode">
              <template #header>
                <div class="card-header">
                  <span>知识点内容</span>
                  <el-tag v-if="currentNode" type="info">Level {{ currentNode.level }}</el-tag>
                </div>
              </template>
              
              <div v-if="currentNode" class="node-content">
                <h2 class="node-title">{{ currentNode.title }}</h2>
                <div class="node-meta" v-if="currentNode.page_start || currentNode.page_end">
                  <el-icon><Document /></el-icon>
                  <span>页码: {{ currentNode.page_start || '?' }} - {{ currentNode.page_end || '?' }}</span>
                </div>
                <div class="markdown-content" v-html="renderedContent"></div>
              </div>
              
              <el-empty v-else description="请选择一个知识点开始学习" />
            </el-card>
            
            <!-- 相关作业 -->
            <el-card v-loading="loadingHomework" style="margin-top: 20px;" v-if="currentNode">
              <template #header>
                <div class="card-header">
                  <span>相关作业</span>
                  <el-badge :value="relatedHomework.length" type="primary" />
                </div>
              </template>
              
              <div v-if="relatedHomework.length > 0" class="homework-list">
                <el-card 
                  v-for="hw in relatedHomework" 
                  :key="hw.id" 
                  class="homework-item"
                  shadow="hover"
                >
                  <div class="homework-header">
                    <el-link type="primary" @click="$router.push(`/homeworks/${hw.id}`)">
                      {{ hw.title || '无标题作业' }}
                    </el-link>
                    <el-tag :type="getStatusType(hw.status)" size="small">
                      {{ getStatusText(hw.status) }}
                    </el-tag>
                  </div>
                  <div class="homework-content-preview">
                    {{ hw.content.substring(0, 100) }}{{ hw.content.length > 100 ? '...' : '' }}
                  </div>
                  <div class="homework-footer">
                    <span class="mastery-level">
                      掌握度: 
                      <el-rate 
                        v-model="hw.mastery_level" 
                        disabled 
                        :max="5" 
                        size="small"
                      />
                    </span>
                    <el-button type="primary" link @click="$router.push(`/homeworks/${hw.id}`)">
                      查看详情
                    </el-button>
                  </div>
                </el-card>
              </div>
              
              <el-empty v-else description="暂无相关作业" />
            </el-card>
          </el-col>
          
          <!-- 右侧：学习控制面板 -->
          <el-col :span="8">
            <!-- 学习计时器 -->
            <el-card class="timer-card">
              <template #header>
                <span>学习计时器</span>
              </template>
              
              <div class="timer-display">
                <div class="timer-time">{{ formatTime(elapsedSeconds) }}</div>
                <div class="timer-status">
                  <el-tag :type="isStudying ? 'success' : 'info'">
                    {{ isStudying ? '学习中...' : '已暂停' }}
                  </el-tag>
                </div>
              </div>
              
              <div class="timer-controls">
                <el-button 
                  type="primary" 
                  size="large" 
                  @click="toggleTimer"
                  :icon="isStudying ? 'VideoPause' : 'VideoPlay'"
                >
                  {{ isStudying ? '暂停' : '开始学习' }}
                </el-button>
                <el-button size="large" @click="resetTimer" :icon="Refresh">
                  重置
                </el-button>
              </div>
            </el-card>
            
            <!-- 知识点选择 -->
            <el-card class="node-selector-card" style="margin-top: 20px;">
              <template #header>
                <span>当前知识点</span>
              </template>
              
              <div v-if="currentNode" class="current-node-info">
                <h3>{{ currentNode.title }}</h3>
                <div class="node-tags">
                  <el-tag 
                    v-for="tag in currentNode.tags" 
                    :key="tag" 
                    size="small"
                    style="margin-right: 5px;"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
                
                <!-- 学习状态 -->
                <div class="learning-status" v-if="nodeStatus">
                  <el-divider content-position="left">学习状态</el-divider>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="状态">
                      <el-tag :type="getLearningStatusType(nodeStatus.status)">
                        {{ getLearningStatusText(nodeStatus.status) }}
                      </el-tag>
                    </el-descriptions-item>
                    <el-descriptions-item label="学习次数">
                      {{ nodeStatus.review_count || 0 }}
                    </el-descriptions-item>
                    <el-descriptions-item label="正确率">
                      {{ nodeStatus.accuracy ? (nodeStatus.accuracy * 100).toFixed(0) + '%' : 'N/A' }}
                    </el-descriptions-item>
                    <el-descriptions-item label="上次学习">
                      {{ nodeStatus.last_reviewed ? formatDate(nodeStatus.last_reviewed) : '从未' }}
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </div>
              
              <el-empty v-else description="未选择知识点" />
            </el-card>
            
            <!-- 学习自评 -->
            <el-card class="rating-card" style="margin-top: 20px;" v-if="currentNode && !isStudying">
              <template #header>
                <span>学习自评</span>
              </template>
              
              <el-form label-width="80px">
                <el-form-item label="自我评分">
                  <el-rate v-model="selfRating" :max="5" show-text />
                </el-form-item>
                <el-form-item label="学习笔记">
                  <el-input 
                    v-model="learningNotes" 
                    type="textarea" 
                    :rows="3" 
                    placeholder="记录学习心得..."
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="saveLearningRecord" :loading="saving">
                    保存学习记录
                  </el-button>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
    
    <!-- 知识点选择对话框 -->
    <el-dialog v-model="showNodeSelector" title="选择知识点" width="700px" @close="closeNodeSelector">
      <div class="node-selector">
        <el-form inline>
          <el-form-item label="学科">
            <el-select v-model="selectedSubjectId" placeholder="选择学科" @change="handleSubjectChange" clearable>
              <el-option 
                v-for="subject in subjects" 
                :key="subject.id" 
                :label="subject.name" 
                :value="subject.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="教材">
            <el-select v-model="selectedBookId" placeholder="选择教材" @change="handleBookChange" :disabled="!selectedSubjectId" clearable>
              <el-option 
                v-for="book in books" 
                :key="book.id" 
                :label="book.title" 
                :value="book.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
        
        <el-tree
          v-if="nodeTree.length > 0"
          :data="nodeTree"
          :props="{ label: 'title', children: 'children' }"
          node-key="id"
          @node-click="handleNodeSelect"
          :expand-on-click-node="false"
          default-expand-all
          highlight-current
          style="max-height: 400px; overflow-y: auto;"
        >
          <template #default="{ node, data }">
            <span class="tree-node">
              <span>{{ data.title }}</span>
              <el-tag size="small" type="info" style="margin-left: 8px;">
                L{{ data.level }}
              </el-tag>
            </span>
          </template>
        </el-tree>
        
        <el-empty v-else description="请选择学科和教材" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { nodeApi, homeworkApi, learnApi } from '@/api'
import { subjectApi, bookApi } from '@/api'
import { storeToRefs } from 'pinia'
import { useSubjectStore } from '@/stores/subjects'
import { useBookStore } from '@/stores/books'
import { ArrowLeft, Refresh, VideoPlay, VideoPause, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

// 由于没有marked库，使用简单的markdown转HTML函数
const simpleMarkdownRender = (text) => {
  if (!text) return ''
  
  let html = text
    // 转义HTML
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    // 标题
    .replace(/^### (.*$)/gm, '<h3>$1</h3>')
    .replace(/^## (.*$)/gm, '<h2>$1</h2>')
    .replace(/^# (.*$)/gm, '<h1>$1</h1>')
    // 粗体和斜体
    .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    // 代码块
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`(.*?)`/g, '<code>$1</code>')
    // 列表
    .replace(/^\s*[-*]\s+(.*$)/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
    // 换行
    .replace(/\n/g, '<br>')
  
  return html
}

const router = useRouter()
const subjectStore = useSubjectStore()
const bookStore = useBookStore()
const { subjects } = storeToRefs(subjectStore)
const { books } = storeToRefs(bookStore)

const loadingNode = ref(false)
const loadingHomework = ref(false)
const saving = ref(false)
const currentNode = ref(null)
const relatedHomework = ref([])
const nodeStatus = ref(null)
const showNodeSelector = ref(false)
const selectedSubjectId = ref(null)
const selectedBookId = ref(null)
const nodeTree = ref([])

// 计时器相关
const isStudying = ref(false)
const elapsedSeconds = ref(0)
const selfRating = ref(0)
const learningNotes = ref('')
let timerInterval = null

const renderedContent = computed(() => {
  return simpleMarkdownRender(currentNode.value?.content)
})

onMounted(async () => {
  await subjectStore.fetchSubjects()
  
  // 如果路由有nodeId参数，自动加载
  const nodeId = router.currentRoute.value.query.nodeId
  if (nodeId) {
    await loadNode(nodeId)
  }
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})

// 监听学习状态，停止计时器时提示保存
watch(isStudying, (newVal) => {
  if (!newVal && elapsedSeconds.value > 0 && currentNode.value) {
    ElMessage.info('学习已暂停，请对本次学习进行自评并保存记录')
  }
})

const loadNode = async (nodeId) => {
  loadingNode.value = true
  try {
    currentNode.value = await nodeApi.detail(nodeId)
    await Promise.all([
      loadRelatedHomework(nodeId),
      loadNodeStatus(nodeId)
    ])
  } catch (error) {
    ElMessage.error('加载知识点失败')
    console.error(error)
  } finally {
    loadingNode.value = false
  }
}

const loadRelatedHomework = async (nodeId) => {
  loadingHomework.value = true
  try {
    relatedHomework.value = await homeworkApi.list({ node_id: nodeId })
  } catch (error) {
    console.error('加载作业失败:', error)
    relatedHomework.value = []
  } finally {
    loadingHomework.value = false
  }
}

const loadNodeStatus = async (nodeId) => {
  try {
    nodeStatus.value = await learnApi.getNodeStatus(nodeId)
  } catch (error) {
    console.error('加载学习状态失败:', error)
    nodeStatus.value = null
  }
}

const toggleTimer = () => {
  if (!currentNode.value) {
    ElMessage.warning('请先选择一个知识点')
    return
  }
  
  isStudying.value = !isStudying.value
  
  if (isStudying.value) {
    timerInterval = setInterval(() => {
      elapsedSeconds.value++
    }, 1000)
  } else {
    if (timerInterval) {
      clearInterval(timerInterval)
      timerInterval = null
    }
  }
}

const resetTimer = () => {
  isStudying.value = false
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  elapsedSeconds.value = 0
}

const formatTime = (seconds) => {
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = seconds % 60
  return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    new: 'info',
    learning: 'warning',
    reviewed: 'primary',
    mastered: 'success'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    new: '新建',
    learning: '学习中',
    reviewed: '已复习',
    mastered: '已掌握'
  }
  return texts[status] || status
}

const getLearningStatusType = (status) => {
  const types = {
    not_started: 'info',
    learning: 'warning',
    reviewing: 'primary',
    mastered: 'success'
  }
  return types[status] || 'info'
}

const getLearningStatusText = (status) => {
  const texts = {
    not_started: '未开始',
    learning: '学习中',
    reviewing: '复习中',
    mastered: '已掌握'
  }
  return texts[status] || status
}

const saveLearningRecord = async () => {
  if (!currentNode.value) {
    ElMessage.warning('请先选择一个知识点')
    return
  }
  
  if (selfRating.value === 0) {
    ElMessage.warning('请先进行自我评分')
    return
  }
  
  saving.value = true
  try {
    const duration = Math.ceil(elapsedSeconds.value / 60) // 转换为分钟
    await learnApi.createRecord({
      node_id: currentNode.value.id,
      duration: duration,
      notes: learningNotes.value,
      self_rating: selfRating.value
    })
    
    ElMessage.success('学习记录已保存')
    
    // 重置表单
    resetTimer()
    selfRating.value = 0
    learningNotes.value = ''
    
    // 刷新状态
    await loadNodeStatus(currentNode.value.id)
  } catch (error) {
    console.error('保存学习记录失败:', error)
  } finally {
    saving.value = false
  }
}

const handleSubjectChange = async () => {
  selectedBookId.value = null
  nodeTree.value = []
  
  if (selectedSubjectId.value) {
    await bookStore.fetchBooks(selectedSubjectId.value)
  }
}

const handleBookChange = async () => {
  nodeTree.value = []
  
  if (selectedBookId.value) {
    try {
      const treeData = await nodeApi.tree(selectedBookId.value)
      nodeTree.value = treeData
    } catch (error) {
      console.error('加载知识树失败:', error)
      ElMessage.error('加载知识树失败')
    }
  }
}

const handleNodeSelect = async (data) => {
  if (data.level < 2) { // 假设level 2以上是叶子节点
    ElMessage.info('请选择一个具体的知识点（Level 2以上）')
    return
  }
  
  showNodeSelector.value = false
  resetTimer()
  selfRating.value = 0
  learningNotes.value = ''
  await loadNode(data.id)
}

const closeNodeSelector = () => {
  // 不需要额外清理
}
</script>

<style scoped>
.study-mode {
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

.header-actions {
  display: flex;
  gap: 10px;
}

.el-main {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.node-content {
  padding: 10px 0;
}

.node-title {
  font-size: 24px;
  color: #303133;
  margin-bottom: 15px;
}

.node-meta {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.markdown-content {
  line-height: 1.8;
  color: #606266;
}

.markdown-content :deep(h1) {
  font-size: 22px;
  margin: 20px 0 15px;
  color: #303133;
}

.markdown-content :deep(h2) {
  font-size: 18px;
  margin: 18px 0 12px;
  color: #303133;
}

.markdown-content :deep(h3) {
  font-size: 16px;
  margin: 15px 0 10px;
  color: #303133;
}

.markdown-content :deep(code) {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
}

.markdown-content :deep(pre) {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 8px;
  overflow-x: auto;
}

.markdown-content :deep(ul) {
  padding-left: 20px;
}

.markdown-content :deep(li) {
  margin: 5px 0;
}

.homework-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.homework-item {
  border-left: 3px solid #409eff;
}

.homework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.homework-content-preview {
  color: #606266;
  font-size: 14px;
  margin-bottom: 10px;
  line-height: 1.5;
}

.homework-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mastery-level {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #909399;
}

/* 计时器样式 */
.timer-card {
  position: sticky;
  top: 20px;
}

.timer-display {
  text-align: center;
  padding: 30px 0;
}

.timer-time {
  font-size: 48px;
  font-weight: bold;
  color: #303133;
  font-family: monospace;
  margin-bottom: 15px;
}

.timer-status {
  margin-bottom: 20px;
}

.timer-controls {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.timer-controls .el-button {
  width: 120px;
}

/* 当前知识点信息 */
.current-node-info h3 {
  margin: 0 0 10px 0;
  color: #303133;
}

.node-tags {
  margin-bottom: 15px;
}

.learning-status {
  margin-top: 15px;
}

/* 节点选择器 */
.node-selector {
  min-height: 400px;
}

.tree-node {
  display: flex;
  align-items: center;
}
</style>
