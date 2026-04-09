<template>
  <div class="homework-detail">
    <el-container>
      <el-header>
        <div class="header-content">
          <el-button @click="$router.back()" :icon="ArrowLeft">返回</el-button>
          <h1>{{ homework?.title || '作业详情' }}</h1>
        </div>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <el-col :xs="24" :lg="16">
            <!-- 题目卡片 -->
            <el-card v-if="homework" class="homework-card">
              <template #header>
                <span>📝 作业内容</span>
              </template>
              
              <div class="homework-info">
                <el-descriptions :column="2" border size="small">
                  <el-descriptions-item label="学科">{{ homework.subject_name }}</el-descriptions-item>
                  <el-descriptions-item label="知识点">
                    <span v-if="homework.node_name">{{ homework.node_name }}</span>
                    <span v-else class="no-data">未指定</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="截止日期">
                    <span v-if="homework.due_date">{{ homework.due_date }}</span>
                    <span v-else class="no-data">无</span>
                  </el-descriptions-item>
                  <el-descriptions-item label="状态">
                    <el-tag :type="getStatusType(homework.status)">{{ getStatusText(homework.status) }}</el-tag>
                  </el-descriptions-item>
                </el-descriptions>
              </div>

              <el-divider>📋 题目</el-divider>
              
              <div class="questions">
                <div v-for="(q, index) in homework.questions" :key="q.id" class="question-item">
                  <h4>题目 {{ index + 1 }} ({{ q.type === 'choice' ? '选择题' : '主观题' }})</h4>
                  <p class="question-content">{{ q.content }}</p>
                  
                  <!-- 选择题选项 -->
                  <div v-if="q.type === 'choice'" class="choices">
                    <el-radio-group v-model="answers[q.id]" :disabled="solutionSubmitted">
                      <el-radio
                        v-for="opt in q.options"
                        :key="opt.key"
                        :value="opt.key"
                        class="choice-option"
                      >
                        <span class="choice-key">{{ opt.key }}.</span>
                        <span class="choice-content">{{ opt.content }}</span>
                      </el-radio>
                    </el-radio-group>
                  </div>
                  <!-- 主观题输入 -->
                  <div v-else class="answer-input">
                    <el-input
                      v-model="answers[q.id]"
                      type="textarea"
                      :rows="3"
                      :placeholder="'请输入你的答案'"
                      :disabled="solutionSubmitted"
                    />
                  </div>
                </div>
              </div>

              <!-- ========== 认知门控核心流程 ========== -->
              <el-divider>💭 我的解题思路</el-divider>
              
              <div class="cognitive-gating">
                <!-- 步骤1: 必填提示 -->
                <div class="step-hint">
                  <el-alert
                    v-if="!solutionSubmitted"
                    type="info"
                    :closable="false"
                    show-icon
                  >
                    <template #title>
                      <span>请先 <strong>认真思考并填写你的解题思路</strong>，然后提交。</span>
                    </template>
                    <template #default>
                      <span class="char-count">至少需要填写 <strong>20</strong> 个字符</span>
                    </template>
                  </el-alert>
                </div>

                <!-- 步骤2: 解题思路输入 -->
                <div class="solution-section">
                  <el-input
                    v-model="userSolution"
                    type="textarea"
                    :rows="5"
                    :placeholder="'在这里写下你的解题思路、步骤和方法...'"
                    :disabled="solutionSubmitted"
                    maxlength="2000"
                    show-word-limit
                    class="solution-input"
                  />
                  <div class="char-counter" :class="{ 'enough': userSolution.length >= 20 }">
                    已输入 {{ userSolution.length }} / 20 字符
                  </div>
                </div>

                <!-- 步骤3: 提交按钮 -->
                <div class="submit-section" v-if="!solutionSubmitted">
                  <el-button 
                    type="primary" 
                    size="large" 
                    @click="submitSolution" 
                    :loading="submittingSolution"
                    :disabled="userSolution.length < 20"
                  >
                    🚀 提交思路
                  </el-button>
                  <span v-if="userSolution.length < 20" class="submit-hint">
                    请填写至少20个字符后再提交
                  </span>
                </div>

                <!-- 步骤4: AI分析结果 (提交后显示) -->
                <div v-if="solutionSubmitted && aiAnalysis" class="ai-analysis-section">
                  <el-divider content-position="left">
                    <span class="section-title">🤖 AI 分析结果</span>
                  </el-divider>
                  
                  <el-card class="analysis-card" shadow="never">
                    <div class="analysis-content">
                      <h4>💡 AI 对你思路的评价</h4>
                      <p>{{ aiAnalysis.evaluation || '分析中...' }}</p>
                      
                      <h4>📌 关键点分析</h4>
                      <ul class="key-points">
                        <li v-for="(point, idx) in aiAnalysis.key_points" :key="idx">
                          {{ point }}
                        </li>
                      </ul>

                      <h4>⚠️ 需要注意的问题</h4>
                      <ul class="issues">
                        <li v-for="(issue, idx) in aiAnalysis.issues" :key="idx">
                          {{ issue }}
                        </li>
                      </ul>
                    </div>
                  </el-card>

                  <!-- AI答案展示 -->
                  <div class="ai-answer-section">
                    <el-divider content-position="left">
                      <span class="section-title">📖 参考答案</span>
                    </el-divider>
                    
                    <div class="ai-answer-toggle">
                      <el-button @click="showAiAnswer = !showAiAnswer">
                        {{ showAiAnswer ? '🙈 隐藏答案' : '👁️ 查看答案' }}
                      </el-button>
                    </div>

                    <el-card v-if="showAiAnswer && aiAnswer" class="answer-card" shadow="never">
                      <div class="answer-content">
                        <div v-for="(ans, idx) in aiAnswer" :key="idx" class="answer-item">
                          <h5>题目 {{ idx + 1 }} 参考答案：</h5>
                          <p>{{ ans }}</p>
                        </div>
                      </div>
                    </el-card>
                  </div>

                  <!-- 对比思考提示 -->
                  <el-divider content-position="left">
                    <span class="section-title">🔄 对比思考</span>
                  </el-divider>
                  
                  <el-card class="reflection-card" shadow="never">
                    <template #header>
                      <span>💭 思考引导</span>
                    </template>
                    <div class="reflection-content">
                      <ul>
                        <li>你的解题思路和AI的分析有哪些 <strong>相似之处</strong>？</li>
                        <li>AI提出的关键点中，有哪些是你 <strong>没有想到</strong> 的？</li>
                        <li>你的方法与参考答案相比，<strong>效率</strong> 上有何差异？</li>
                        <li>通过这道题，你对这类知识点有了哪些 <strong>新的理解</strong>？</li>
                      </ul>
                    </div>
                  </el-card>

                  <!-- 完成学习 -->
                  <div class="complete-section">
                    <el-button 
                      type="success" 
                      size="large" 
                      @click="completeLearning"
                      :loading="completing"
                    >
                      ✅ 完成学习
                    </el-button>
                  </div>
                </div>
              </div>
            </el-card>

            <el-skeleton v-if="loading" :rows="10" animated />
          </el-col>

          <!-- 右侧边栏 -->
          <el-col :xs="24" :lg="8">
            <!-- 学习反馈 -->
            <el-card v-if="feedback" class="feedback-card">
              <template #header>
                <span>📊 学习反馈</span>
              </template>
              <div class="feedback-content">
                <el-progress
                  :percentage="feedback.score || 0"
                  :color="getScoreColor(feedback.score)"
                  :stroke-width="20"
                />
                <el-divider />
                <div class="feedback-items">
                  <div v-for="(item, index) in feedback.feedbacks" :key="index" class="feedback-item">
                    <h5>{{ item.node_name }}</h5>
                    <p>{{ item.suggestion }}</p>
                    <el-tag size="small" :type="getMasteryType(item.mastery_level)">
                      {{ item.mastery_level }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-card>
            
            <!-- 相关知识点 -->
            <el-card v-if="homework?.related_nodes?.length" class="related-card">
              <template #header>
                <span>📚 相关知识点</span>
              </template>
              <div class="related-nodes">
                <el-tag
                  v-for="node in homework.related_nodes"
                  :key="node.id"
                  class="node-tag"
                  @click="goToNode(node.id)"
                >
                  {{ node.name }}
                </el-tag>
              </div>
            </el-card>

            <!-- 学习建议 -->
            <el-card class="tips-card">
              <template #header>
                <span>💡 学习技巧</span>
              </template>
              <div class="tips-content">
                <ul>
                  <li>先独立思考，再查看答案</li>
                  <li>记录自己的解题过程</li>
                  <li>对比AI分析发现思维盲点</li>
                  <li>总结归纳，形成知识体系</li>
                </ul>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHomeworkStore } from '@/stores/homework'
import { storeToRefs } from 'pinia'
import { ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { aiApi } from '@/api'

const route = useRoute()
const router = useRouter()
const homeworkStore = useHomeworkStore()
const { currentHomework: homework, feedback, loading } = storeToRefs(homeworkStore)

const answers = reactive({})
const userSolution = ref('')
const solutionSubmitted = ref(false)
const submittingSolution = ref(false)
const aiAnalysis = ref(null)
const aiAnswer = ref(null)
const showAiAnswer = ref(false)
const completing = ref(false)

onMounted(async () => {
  const id = route.params.id
  await homeworkStore.fetchHomework(id)
  await homeworkStore.fetchFeedback(id)
  
  // 初始化答案
  if (homework.value?.questions) {
    homework.value.questions.forEach(q => {
      answers[q.id] = q.user_answer || ''
    })
  }

  // 检查是否已提交过思路（刷新页面后状态丢失，可用localStorage持久化）
  const submittedKey = `homework_solution_submitted_${id}`
  if (localStorage.getItem(submittedKey)) {
    solutionSubmitted.value = true
    userSolution.value = localStorage.getItem(`homework_solution_${id}`) || ''
    // 可以恢复AI分析结果（如果需要）
    const cachedAnalysis = localStorage.getItem(`homework_ai_analysis_${id}`)
    if (cachedAnalysis) {
      aiAnalysis.value = JSON.parse(cachedAnalysis)
    }
  }
})

// 提交解题思路
const submitSolution = async () => {
  if (userSolution.value.length < 20) {
    ElMessage.warning('请至少填写20个字符')
    return
  }

  submittingSolution.value = true
  try {
    // 保存解题思路
    const savedSolution = userSolution.value
    
    // 调用AI分析接口
    const analysis = await aiApi.analyzeSolution(route.params.id, {
      user_solution: savedSolution
    })
    
    aiAnalysis.value = analysis
    
    // 获取AI答案
    try {
      aiAnswer.value = await aiApi.getAnswer(route.params.id)
    } catch (e) {
      console.error('获取AI答案失败:', e)
      aiAnswer.value = homework.value?.questions?.map(q => q.correct_answer || '暂无答案')
    }

    solutionSubmitted.value = true

    // 持久化状态
    const submittedKey = `homework_solution_submitted_${route.params.id}`
    localStorage.setItem(submittedKey, 'true')
    localStorage.setItem(`homework_solution_${route.params.id}`, savedSolution)
    if (analysis) {
      localStorage.setItem(`homework_ai_analysis_${route.params.id}`, JSON.stringify(analysis))
    }

    ElMessage.success('思路提交成功！请查看AI分析结果')
  } catch (error) {
    ElMessage.error('提交失败，请重试')
    console.error('AI分析失败:', error)
    
    // 即使AI分析失败，也允许用户查看答案
    solutionSubmitted.value = true
    aiAnalysis.value = {
      evaluation: '（AI分析暂时不可用，请自行思考或查看参考答案）',
      key_points: ['无法获取AI分析'],
      issues: []
    }
    aiAnswer.value = homework.value?.questions?.map(q => q.correct_answer || '暂无答案')
  } finally {
    submittingSolution.value = false
  }
}

// 完成学习
const completeLearning = async () => {
  completing.value = true
  try {
    // 可以记录学习完成状态
    ElMessage.success('恭喜完成本次学习！')
    await router.push('/homeworks')
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    completing.value = false
  }
}

const goToNode = (nodeId) => {
  router.push(`/homeworks?node_id=${nodeId}`)
}

const getStatusType = (status) => {
  const types = { pending: 'warning', completed: 'success', graded: 'info' }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = { pending: '未完成', completed: '已完成', graded: '已批改' }
  return texts[status] || status
}

const getScoreColor = (score) => {
  if (score >= 90) return '#67c23a'
  if (score >= 70) return '#e6a23c'
  return '#f56c6c'
}

const getMasteryType = (level) => {
  const types = { '掌握': 'success', '熟悉': 'warning', '了解': 'info' }
  return types[level] || 'info'
}
</script>

<style scoped>
.homework-detail {
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
}

.el-main {
  padding: 20px;
}

.homework-card, .feedback-card, .related-card, .tips-card {
  margin-bottom: 20px;
}

.no-data {
  color: #999;
  font-style: italic;
}

.question-item {
  margin-bottom: 30px;
  padding: 15px;
  background: #f9fafb;
  border-radius: 8px;
}

.question-content {
  margin: 15px 0;
  font-size: 16px;
  line-height: 1.6;
}

.choices {
  margin-top: 15px;
}

.choice-option {
  display: block;
  margin-bottom: 10px;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
}

.choice-key {
  font-weight: bold;
  margin-right: 8px;
}

.answer-input {
  margin-top: 15px;
}

/* ========== 认知门控样式 ========== */
.cognitive-gating {
  padding: 20px 0;
}

.step-hint {
  margin-bottom: 20px;
}

.char-count {
  font-size: 13px;
  color: #909399;
}

.solution-section {
  margin-bottom: 20px;
}

.solution-input :deep(.el-textarea__inner) {
  font-size: 15px;
  line-height: 1.8;
}

.char-counter {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.char-counter.enough {
  color: #67c23a;
}

.submit-section {
  text-align: center;
  margin: 30px 0;
}

.submit-hint {
  display: block;
  margin-top: 10px;
  font-size: 13px;
  color: #909399;
}

/* AI分析结果 */
.ai-analysis-section {
  margin-top: 30px;
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-title {
  font-size: 16px;
  font-weight: bold;
}

.analysis-card, .answer-card, .reflection-card {
  margin-top: 15px;
}

.analysis-content h4,
.answer-content h5 {
  color: #333;
  margin: 15px 0 10px;
}

.analysis-content h4:first-child {
  margin-top: 0;
}

.key-points, .issues {
  padding-left: 20px;
  color: #606266;
}

.key-points li, .issues li {
  margin-bottom: 8px;
}

.ai-answer-section {
  margin-top: 20px;
}

.ai-answer-toggle {
  margin-bottom: 15px;
}

.answer-item {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px dashed #ebeef5;
}

.answer-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.answer-content p {
  color: #409eff;
  font-size: 15px;
  line-height: 1.6;
}

.reflection-content ul {
  padding-left: 20px;
  color: #606266;
}

.reflection-content li {
  margin-bottom: 12px;
  line-height: 1.6;
}

.complete-section {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

/* 反馈卡片 */
.feedback-content {
  text-align: center;
}

.feedback-items {
  text-align: left;
}

.feedback-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.feedback-item h5 {
  margin: 0 0 8px;
  color: #333;
}

.feedback-item p {
  margin: 0 0 8px;
  color: #606266;
  font-size: 14px;
}

.node-tag {
  margin: 5px;
  cursor: pointer;
}

.tips-content ul {
  padding-left: 20px;
  color: #606266;
}

.tips-content li {
  margin-bottom: 8px;
}
</style>