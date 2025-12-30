<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { SparklesIcon, ArrowPathIcon, ChatBubbleLeftIcon, CheckIcon, XMarkIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const userInput = ref('')
const feedback = ref('')

// 当前步骤：input（输入） 或 preview（预览）
const step = ref<'input' | 'preview'>('input')

const hasImage = computed(() => !!sessionStore.currentVersion)

// 处理预览
async function handlePreview() {
  if (!userInput.value.trim()) return
  try {
    await sessionStore.previewGenerate(userInput.value)
    step.value = 'preview'
  } catch (error) {
    console.error('预览失败:', error)
  }
}

// 处理确认生成
async function handleConfirm() {
  try {
    await sessionStore.confirmGenerate(userInput.value)
    userInput.value = ''
    step.value = 'input'
  } catch (error) {
    console.error('生成失败:', error)
  }
}

// 取消预览
function handleCancel() {
  step.value = 'input'
  sessionStore.previewSchema = null
  sessionStore.previewPrompt = null
}

async function handleFeedback() {
  if (!feedback.value.trim()) return
  try {
    await sessionStore.submitFeedback(feedback.value)
    feedback.value = ''
  } catch (error) {
    console.error('反馈提交失败:', error)
  }
}
</script>

<template>
  <div class="space-y-4">
    <!-- 第一步：创意输入 -->
    <div v-if="!hasImage && step === 'input'" class="card p-5 animate-scale-in">
      <div class="flex items-center gap-2 mb-3">
        <SparklesIcon class="w-4 h-4 text-sky-500" />
        <label class="text-sm font-semibold text-slate-800">创意输入</label>
      </div>
      <textarea
        v-model="userInput"
        placeholder="描述你想要的图片，例如：一只橘猫坐在窗边看日落..."
        :disabled="sessionStore.loading"
        class="w-full h-36 px-4 py-3 text-sm border border-slate-200 rounded-xl input-glow resize-none disabled:bg-slate-50 disabled:cursor-not-allowed text-slate-700 placeholder:text-slate-400 transition-all duration-200"
      />
      <button
        @click="handlePreview"
        :disabled="sessionStore.loading || !userInput.trim()"
        class="w-full mt-4 px-4 py-3 btn-gradient text-sm"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-4 h-4 animate-spin" />
          生成 Prompt 中...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <SparklesIcon class="w-4 h-4" />
          预览 Prompt
        </span>
      </button>

      <!-- 错误提示 -->
      <div
        v-if="sessionStore.error"
        class="mt-3 text-sm text-red-600 bg-red-50 px-4 py-3 rounded-xl border border-red-100 animate-scale-in"
      >
        {{ sessionStore.error }}
      </div>
    </div>

    <!-- 第二步：Prompt 预览 -->
    <div v-if="!hasImage && step === 'preview'" class="card p-5 animate-slide-up">
      <div class="flex items-center gap-2 mb-3">
        <SparklesIcon class="w-4 h-4 text-sky-500" />
        <label class="text-sm font-semibold text-slate-800">生成的 Prompt 预览</label>
      </div>

      <!-- 显示 Prompt -->
      <div class="bg-slate-50 p-4 rounded-xl mb-4 max-h-64 overflow-y-auto">
        <pre class="text-xs whitespace-pre-wrap text-slate-700">{{ sessionStore.previewPrompt }}</pre>
      </div>

      <!-- 显示 Schema（可折叠） -->
      <details class="mb-4">
        <summary class="text-sm font-medium text-slate-600 cursor-pointer hover:text-slate-800 transition-colors">
          查看 Schema 详情
        </summary>
        <div class="mt-2 bg-slate-50 p-4 rounded-xl max-h-48 overflow-y-auto">
          <pre class="text-xs text-slate-700">{{ JSON.stringify(sessionStore.previewSchema, null, 2) }}</pre>
        </div>
      </details>

      <!-- 操作按钮 -->
      <div class="flex gap-3">
        <button
          @click="handleCancel"
          :disabled="sessionStore.loading"
          class="flex-1 px-4 py-3 bg-slate-200 hover:bg-slate-300 disabled:bg-slate-100 text-slate-700 text-sm font-medium rounded-xl transition-all duration-200 disabled:cursor-not-allowed"
        >
          <span class="flex items-center justify-center gap-2">
            <XMarkIcon class="w-4 h-4" />
            取消
          </span>
        </button>
        <button
          @click="handleConfirm"
          :disabled="sessionStore.loading"
          class="flex-1 px-4 py-3 btn-gradient text-sm"
        >
          <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
            <ArrowPathIcon class="w-4 h-4 animate-spin" />
            生成图片中...
          </span>
          <span v-else class="flex items-center justify-center gap-2">
            <CheckIcon class="w-4 h-4" />
            确认生成图片
          </span>
        </button>
      </div>

      <!-- 错误提示 -->
      <div
        v-if="sessionStore.error"
        class="mt-3 text-sm text-red-600 bg-red-50 px-4 py-3 rounded-xl border border-red-100 animate-scale-in"
      >
        {{ sessionStore.error }}
      </div>
    </div>

    <!-- 反馈优化（条件显示） -->
    <div v-if="hasImage" class="card p-5 animate-slide-up">
      <div class="flex items-center gap-2 mb-3">
        <ChatBubbleLeftIcon class="w-4 h-4 text-sky-500" />
        <label class="text-sm font-semibold text-slate-800">反馈优化</label>
      </div>
      <textarea
        v-model="feedback"
        placeholder="对图片有什么不满意的地方？例如：光线太暗、背景太复杂..."
        :disabled="sessionStore.loading"
        class="w-full h-24 px-4 py-3 text-sm border border-slate-200 rounded-xl input-glow resize-none disabled:bg-slate-50 disabled:cursor-not-allowed text-slate-700 placeholder:text-slate-400 transition-all duration-200"
      />
      <button
        @click="handleFeedback"
        :disabled="sessionStore.loading || !feedback.trim()"
        class="w-full mt-4 px-4 py-3 bg-slate-800 hover:bg-slate-700 disabled:bg-slate-300 text-white text-sm font-medium rounded-xl transition-all duration-200 disabled:cursor-not-allowed"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-4 h-4 animate-spin" />
          优化中...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <ChatBubbleLeftIcon class="w-4 h-4" />
          提交反馈
        </span>
      </button>
    </div>
  </div>
</template>
