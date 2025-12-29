<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { ArrowPathIcon } from '@heroicons/vue/24/outline'
import VersionList from './VersionList.vue'

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
    <div class="bg-white rounded-lg border border-slate-200 p-6">
      <label class="block text-sm font-semibold text-slate-900 mb-3">
        创意输入
      </label>
      <textarea
        v-model="userInput"
        placeholder="描述你想要的图片，例如：画一只橘猫坐在窗边看日落"
        :disabled="sessionStore.loading"
        class="w-full h-48 px-3 py-2 text-sm border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-slate-50 disabled:cursor-not-allowed text-slate-700 placeholder:text-slate-400"
      />
      <button
        @click="handleGenerate"
        :disabled="sessionStore.loading || !userInput.trim()"
        class="w-full mt-4 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white text-sm font-medium rounded-md transition-colors disabled:cursor-not-allowed"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-4 h-4 animate-spin" />
          生成中...
        </span>
        <span v-else>生成图片</span>
      </button>
      <div v-if="sessionStore.error" class="mt-3 text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md border border-red-200">
        {{ sessionStore.error }}
      </div>
    </div>

    <!-- 反馈优化（条件显示） -->
    <div v-if="hasImage" class="bg-white rounded-lg border border-slate-200 p-6">
      <label class="block text-sm font-semibold text-slate-900 mb-3">
        反馈优化
      </label>
      <textarea
        v-model="feedback"
        placeholder="对图片有什么不满意的地方？例如：太暗了、背景太复杂"
        :disabled="sessionStore.loading"
        class="w-full h-32 px-3 py-2 text-sm border border-slate-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:bg-slate-50 disabled:cursor-not-allowed text-slate-700 placeholder:text-slate-400"
      />
      <button
        @click="handleFeedback"
        :disabled="sessionStore.loading || !feedback.trim()"
        class="w-full mt-4 px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white text-sm font-medium rounded-md transition-colors disabled:cursor-not-allowed"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-4 h-4 animate-spin" />
          优化中...
        </span>
        <span v-else>提交反馈</span>
      </button>
    </div>

    <!-- 版本历史（条件显示） -->
    <VersionList v-if="sessionStore.hasVersions" />
  </div>
</template>
