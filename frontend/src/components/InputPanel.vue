<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { SparklesIcon, ArrowPathIcon, ChatBubbleLeftIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const userInput = ref('')
const feedback = ref('')

const hasImage = computed(() => !!sessionStore.currentVersion)

async function handleGenerate() {
  if (!userInput.value.trim()) return
  try {
    await sessionStore.generate(userInput.value)
    userInput.value = ''
  } catch (error) {
    console.error('生成失败:', error)
  }
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
    <!-- 创意输入 -->
    <div v-if="!hasImage" class="card p-5 animate-scale-in">
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
        @click="handleGenerate"
        :disabled="sessionStore.loading || !userInput.trim()"
        class="w-full mt-4 px-4 py-3 btn-gradient text-sm"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-4 h-4 animate-spin" />
          生成中...
        </span>
        <span v-else class="flex items-center justify-center gap-2">
          <SparklesIcon class="w-4 h-4" />
          生成图片
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
