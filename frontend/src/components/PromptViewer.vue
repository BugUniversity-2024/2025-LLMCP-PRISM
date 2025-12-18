<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import {
  DocumentTextIcon,
  UserIcon,
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

const currentVersion = computed(() => sessionStore.currentVersion)
const hasData = computed(() => !!currentVersion.value)
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-indigo-100/50 hover:border-indigo-200 backdrop-blur-sm">
    <h3 class="text-lg font-semibold mb-4 text-slate-800 flex items-center gap-2">
      <DocumentTextIcon class="w-5 h-5 text-indigo-600" />
      Prompt 详情
    </h3>

    <div v-if="hasData" class="space-y-4">
      <!-- 用户输入 -->
      <div v-if="currentVersion!.user_input" class="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4 border border-purple-100">
        <h4 class="font-semibold text-sm mb-2 text-slate-700 flex items-center gap-2">
          <UserIcon class="w-4 h-4 text-purple-600" />
          用户输入
        </h4>
        <p class="text-sm text-slate-600">
          {{ currentVersion!.user_input }}
        </p>
      </div>

      <!-- 用户反馈 -->
      <div v-if="currentVersion!.user_feedback" class="bg-gradient-to-r from-pink-50 to-purple-50 rounded-lg p-4 border border-pink-100">
        <h4 class="font-semibold text-sm mb-2 text-slate-700 flex items-center gap-2">
          <ChatBubbleLeftRightIcon class="w-4 h-4 text-pink-600" />
          用户反馈
        </h4>
        <p class="text-sm text-slate-600">
          {{ currentVersion!.user_feedback }}
        </p>
      </div>

      <!-- 生成的 Prompt -->
      <div class="bg-slate-50 rounded-lg p-4 border border-slate-200">
        <h4 class="font-semibold text-sm mb-2 text-slate-700 flex items-center gap-2">
          <CodeBracketIcon class="w-4 h-4 text-indigo-600" />
          生成的 Prompt
        </h4>
        <pre class="text-xs bg-white p-4 rounded-lg overflow-auto max-h-48 whitespace-pre-wrap font-mono text-slate-600 border border-slate-200">{{ currentVersion!.prompt }}</pre>
      </div>

      <!-- Diff 信息 -->
      <div v-if="currentVersion!.diff" class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
        <h4 class="font-semibold text-sm mb-2 text-slate-700 flex items-center gap-2">
          <CheckCircleIcon class="w-4 h-4 text-green-600" />
          优化说明
        </h4>
        <p class="text-sm text-slate-600">
          {{ currentVersion!.diff.reasoning }}
        </p>
      </div>
    </div>

    <div v-else class="h-80 flex flex-col items-center justify-center text-slate-400 bg-gradient-to-br from-slate-50 to-indigo-50/30 rounded-lg border-2 border-dashed border-slate-200">
      <DocumentTextIcon class="w-16 h-16 mb-4 text-slate-300" />
      <p class="text-sm font-medium">暂无 Prompt 数据</p>
    </div>
  </div>
</template>
