<template>
  <div class="ai-chat">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>AI 问答助手</h1>
          <el-select v-model="chatType" placeholder="对话类型" style="width: 150px;">
            <el-option label="通用问答" value="general" />
            <el-option label="作业辅导" value="homework_help" />
            <el-option label="概念讲解" value="concept_explain" />
          </el-select>
        </div>
      </el-header>
      <el-main>
        <div class="chat-container">
          <!-- 知识点信息 -->
          <el-card class="checkpoint-info-card" v-if="checkpointName">
            <div class="checkpoint-info">
              <el-icon><Document /></el-icon>
              <span>当前知识点：{{ checkpointName }}</span>
            </div>
          </el-card>

          <!-- 聊天消息区域 -->
          <div class="chat-messages" ref="messagesContainer">
            <div class="messages-wrapper">
              <!-- 欢迎消息 -->
              <div v-if="messages.length === 0" class="welcome-message">
                <div class="welcome-icon">
                  <el-icon :size="60" color="#409eff"><ChatDotRound /></el-icon>
                </div>
                <h3>你好！我是你的AI学习助手</h3>
                <p>我可以帮你解答问题、讲解概念、辅导作业</p>
                <div class="quick-questions">
                  <span class="quick-label">试试这样问：</span>
                  <el-tag 
                    v-for="q in quickQuestions" 
                    :key="q" 
                    class="quick-tag"
                    @click="sendQuickQuestion(q)"
                  >
                    {{ q }}
                  </el-tag>
                </div>
              </div>

              <!-- 消息列表 -->
              <div 
                v-for="(msg, index) in messages" 
                :key="index" 
                class="message-item"
                :class="{ user: msg.role === 'user', ai: msg.role === 'assistant' }"
              >
                <div class="message-avatar">
                  <el-avatar 
                    :size="36" 
                    :icon="msg.role === 'user' ? UserFilled : ChatDotRound"
                    :color="msg.role === 'user' ? '#409eff' : '#67c23a'"
                  />
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="sender-name">{{ msg.role === 'user' ? '你' : 'AI 助手' }}</span>
                    <span class="message-time">{{ msg.time }}</span>
                  </div>
                  <div class="message-body">
                    <pre v-if="msg.content">{{ msg.content }}</pre>
                    <div v-else class="loading-dots">
                      <span></span><span></span><span></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入区域 -->
          <div class="chat-input-area">
            <div class="input-container">
              <el-input
                v-model="inputMessage"
                type="textarea"
                :rows="2"
                placeholder="输入你的问题... (Shift+Enter换行，Enter发送)"
                @keydown.enter.exact.prevent="handleSend"
                @keydown.enter.shift.exact="handleNewLine"
                :disabled="sending"
              />
              <div class="input-actions">
                <span class="char-count">{{ inputMessage.length }}/500</span>
                <el-button 
                  type="primary" 
                  :disabled="!inputMessage.trim() || sending"
                  :loading="sending"
                  @click="handleSend"
                >
                  发送
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewApi, aiApi } from '@/api'
import { ArrowLeft, UserFilled, ChatDotRound, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()

const planId = computed(() => route.params.id)
const checkpointId = computed(() => route.query.checkpoint_id)

const messagesContainer = ref(null)
const messages = ref([])
const inputMessage = ref('')
const sending = ref(false)
const checkpointName = ref('')
const chatType = ref('general')

const quickQuestions = [
  '帮我解释这个知识点',
  '出一道相关的练习题',
  '这个概念有什么重点？',
  '和之前学的有什么联系？'
]

onMounted(async () => {
  if (checkpointId.value) {
    await loadCheckpointInfo()
  }
})

const loadCheckpointInfo = async () => {
  try {
    const checkpoints = await reviewApi.getCheckpoints(planId.value)
    const checkpoint = checkpoints.find(cp => cp.id.toString() === checkpointId.value.toString())
    if (checkpoint) {
      checkpointName.value = checkpoint.node_name
    }
  } catch (error) {
    console.error('获取知识点信息失败:', error)
  }
}

const handleSend = async () => {
  const content = inputMessage.value.trim()
  if (!content || sending.value) return

  // Add user message
  messages.value.push({
    role: 'user',
    content: content,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  })
  
  inputMessage.value = ''
  await scrollToBottom()
  
  sending.value = true
  
  try {
    // Add placeholder for AI response
    const aiMsgIndex = messages.value.length
    messages.value.push({
      role: 'assistant',
      content: '',
      time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    })

    // Build context for AI
    const context = {
      plan_id: planId.value,
      checkpoint_id: checkpointId.value,
      chat_type: chatType.value,
      history: messages.value.slice(0, -1).map(m => ({
        role: m.role,
        content: m.content
      }))
    }

    // Call AI API
    const response = await aiApi.chat(context, { message: content })
    
    // Update AI message
    messages.value[aiMsgIndex].content = response.message || response.content || '抱歉，我无法回答这个问题。'
    
  } catch (error) {
    console.error('发送消息失败:', error)
    // Remove placeholder and show error
    messages.value.pop()
    ElMessage.error('发送消息失败，请重试')
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}

const handleNewLine = () => {
  // Allow Shift+Enter to add newline in textarea
}

const sendQuickQuestion = async (question) => {
  inputMessage.value = question
  await handleSend()
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-chat {
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
  height: calc(100vh - 80px);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.checkpoint-info-card {
  margin-bottom: 16px;
}

.checkpoint-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.welcome-message {
  text-align: center;
  padding: 40px 20px;
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome-message h3 {
  margin: 0 0 8px 0;
  color: #303133;
}

.welcome-message p {
  margin: 0 0 20px 0;
  color: #909399;
}

.quick-questions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  align-items: center;
}

.quick-label {
  color: #909399;
  font-size: 14px;
}

.quick-tag {
  cursor: pointer;
}

.message-item {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.message-item.user {
  flex-direction: row-reverse;
  margin-left: auto;
}

.message-item.ai {
  flex-direction: row;
}

.message-avatar {
  flex-shrink: 0;
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.message-item.user .message-header {
  flex-direction: row-reverse;
}

.sender-name {
  font-size: 13px;
  color: #909399;
}

.message-time {
  font-size: 12px;
  color: #c0c4cc;
}

.message-body {
  background: #f5f7fa;
  padding: 12px 16px;
  border-radius: 8px;
  word-break: break-word;
}

.message-item.user .message-body {
  background: #409eff;
  color: #fff;
}

.message-body pre {
  margin: 0;
  white-space: pre-wrap;
  font-family: inherit;
  line-height: 1.6;
}

.loading-dots {
  display: flex;
  gap: 4px;
  padding: 4px 0;
}

.loading-dots span {
  width: 8px;
  height: 8px;
  background: #c0c4cc;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}

.loading-dots span:nth-child(1) { animation-delay: -0.32s; }
.loading-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.chat-input-area {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.input-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.char-count {
  color: #c0c4cc;
  font-size: 12px;
}
</style>
