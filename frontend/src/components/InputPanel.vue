<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'
import { PencilIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const userInput = ref('')

async function handleGenerate() {
  if (!userInput.value.trim()) return

  try {
    await sessionStore.generate(userInput.value)
    userInput.value = ''
  } catch (error) {
    console.error('生成失败:', error)
  }
}
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-purple-100/50 hover:border-purple-200 backdrop-blur-sm">
    <h3 class="text-lg font-semibold mb-4 text-slate-800 flex items-center gap-2">
      <PencilIcon class="w-5 h-5 text-purple-600" />
      创意输入
    </h3>

    <div class="space-y-4">
      <textarea
        v-model="userInput"
        placeholder="描述你想要的图片，例如：画一只橘猫坐在窗边看日落"
        :disabled="sessionStore.loading"
        class="w-full h-40 px-4 py-3 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none disabled:bg-slate-50 disabled:cursor-not-allowed font-sans text-slate-700 placeholder:text-slate-400"
      />

      <button
        @click="handleGenerate"
        :disabled="sessionStore.loading || !userInput.trim()"
        class="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
      >
        <span v-if="sessionStore.loading" class="flex items-center justify-center gap-2">
          <ArrowPathIcon class="w-5 h-5 animate-spin" />
          生成中...
        </span>
        <span v-else>生成图片</span>
      </button>

      <div v-if="sessionStore.error" class="text-sm text-red-600 bg-red-50 px-4 py-3 rounded-lg border border-red-200">
        {{ sessionStore.error }}
      </div>
    </div>
  </div>
</template>
