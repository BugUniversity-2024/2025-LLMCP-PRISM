<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()

const currentVersion = computed(() => sessionStore.currentVersion)

function switchToVersion(versionNumber: number) {
  sessionStore.switchToVersion(versionNumber)
}
</script>

<template>
  <div class="bg-white rounded-lg border border-slate-200 p-6">
    <h3 class="text-sm font-semibold text-slate-900 mb-4">版本历史</h3>

    <div class="space-y-2">
      <button
        v-for="version in sessionStore.currentSession?.versions"
        :key="version.version_number"
        :class="[
          'w-full px-4 py-3 text-left rounded-md border transition-colors',
          version.version_number === currentVersion?.version_number
            ? 'bg-blue-50 border-blue-200 text-blue-900'
            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
        ]"
        @click="switchToVersion(version.version_number)"
      >
        <div class="flex items-center justify-between mb-1">
          <span class="text-sm font-semibold">v{{ version.version_number }}</span>
          <span class="text-xs text-slate-500">
            {{ new Date(version.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) }}
          </span>
        </div>
        <p class="text-xs text-slate-600 line-clamp-2">
          {{ version.user_input || version.user_feedback || '...' }}
        </p>
      </button>
    </div>
  </div>
</template>
