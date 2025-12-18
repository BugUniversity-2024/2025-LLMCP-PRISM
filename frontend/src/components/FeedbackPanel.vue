<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { PencilSquareIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const feedback = ref('')

const hasSession = computed(() => sessionStore.hasSession)

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
  <div class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-pink-100/50 hover:border-pink-200 backdrop-blur-sm">
    <h3 class="text-lg font-semibold mb-4 text-slate-800 flex items-center gap-2">
      <PencilSquareIcon class="w-5 h-5 text-pink-600" />
      反馈优化
    </h3>

    <div class="space-y-4">
      <textarea
        v-model="feedback"
        placeholder="对图片有什么不满意的地方？例如：太暗了、背景太复杂"
        :disabled="!hasSession || sessionStore.loading"
        class="w-full h-40 px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all resize-none disabled:bg-slate-50 disabled:cursor-not-allowed font-sans text-slate-700 placeholder:text-slate-400"
      />

      <button
        @click="handleFeedback"
        :disabled="sessionStore.loading || !feedback.trim() || !hasSession"
        class="w-full px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 hover:from-pink-700 hover:to-purple-700 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-5 h-5 animate-spin" />
          优化中...
        </span>
        <span v-else>提交反馈</span>
      </button>

      <div v-if="!hasSession" class="text-sm text-slate-500 bg-slate-50 px-4 py-3 rounded-lg border border-slate-200">
        💡 请先生成图片后再提交反馈
      </div>
    </div>
  </div>
</template>
