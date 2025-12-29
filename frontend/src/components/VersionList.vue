<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { ClockIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

const currentVersion = computed(() => sessionStore.currentVersion)
const versions = computed(() => sessionStore.currentSession?.versions || [])

function switchToVersion(versionNumber: number) {
  sessionStore.switchToVersion(versionNumber)
}

function formatTime(isoString: string) {
  const date = new Date(isoString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="card p-5 animate-slide-up" style="animation-delay: 150ms">
    <div class="flex items-center gap-2 mb-4">
      <ClockIcon class="w-4 h-4 text-sky-500" />
      <h3 class="text-sm font-semibold text-slate-800">版本历史</h3>
      <span class="text-xs text-slate-400">({{ versions.length }})</span>
    </div>

    <!-- 时间轴 -->
    <div class="relative">
      <!-- 连接线 -->
      <div class="absolute left-[7px] top-3 bottom-3 w-0.5 bg-slate-200 rounded-full" />

      <!-- 版本列表 -->
      <div class="space-y-1">
        <button
          v-for="version in versions"
          :key="version.version_number"
          :class="[
            'relative w-full pl-6 pr-3 py-2.5 text-left rounded-lg transition-all duration-200',
            version.version_number === currentVersion?.version_number
              ? 'bg-gradient-to-r from-sky-50 to-cyan-50'
              : 'hover:bg-slate-50'
          ]"
          @click="switchToVersion(version.version_number)"
        >
          <!-- 时间轴节点 -->
          <span
            :class="[
              'absolute left-0 top-1/2 -translate-y-1/2 w-[15px] h-[15px] rounded-full border-2 transition-all duration-200',
              version.version_number === currentVersion?.version_number
                ? 'bg-gradient-to-br from-cyan-400 to-sky-500 border-white shadow-md'
                : 'bg-white border-slate-300'
            ]"
          />

          <!-- 内容 -->
          <div class="flex items-center justify-between mb-0.5">
            <span
              :class="[
                'text-sm font-semibold transition-colors',
                version.version_number === currentVersion?.version_number
                  ? 'text-sky-700'
                  : 'text-slate-700'
              ]"
            >
              v{{ version.version_number }}
            </span>
            <span class="text-[10px] text-slate-400 font-medium">
              {{ formatTime(version.created_at) }}
            </span>
          </div>
          <p
            :class="[
              'text-xs line-clamp-1 transition-colors',
              version.version_number === currentVersion?.version_number
                ? 'text-sky-600'
                : 'text-slate-500'
            ]"
          >
            {{ version.user_input || version.user_feedback || '初始版本' }}
          </p>
        </button>
      </div>
    </div>
  </div>
</template>
