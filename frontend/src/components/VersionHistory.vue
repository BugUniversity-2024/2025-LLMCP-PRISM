<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { ClockIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

const hasVersions = computed(() => sessionStore.hasVersions)
const currentSession = computed(() => sessionStore.currentSession)
const currentVersion = computed(() => sessionStore.currentVersion)

function switchToVersion(versionNumber: number) {
  sessionStore.switchToVersion(versionNumber)
}
</script>

<template>
  <div v-if="hasVersions" class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-slate-200/50">
    <h3 class="text-lg font-semibold mb-4 text-slate-800 flex items-center gap-2">
      <ClockIcon class="w-5 h-5 text-slate-600" />
      版本历史
    </h3>

    <div class="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
      <button
        v-for="version in currentSession?.versions"
        :key="version.version_number"
        :class="[
          'px-4 py-2 rounded-lg font-medium text-sm transition-all min-w-fit',
          version.version_number === currentVersion?.version_number
            ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg'
            : 'bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 hover:border-purple-200'
        ]"
        @click="switchToVersion(version.version_number)"
      >
        v{{ version.version_number }}
      </button>
    </div>

    <div v-if="currentVersion" class="mt-4 p-4 bg-gradient-to-r from-slate-50 to-purple-50/30 rounded-lg border border-slate-200">
      <p class="text-sm text-slate-600">
        <span class="font-semibold text-slate-700">当前版本：</span>
        v{{ currentVersion.version_number }}
      </p>
      <p v-if="currentVersion.user_input" class="text-sm text-slate-600 mt-1">
        <span class="font-semibold text-slate-700">描述：</span>
        {{ currentVersion.user_input }}
      </p>
      <p v-if="currentVersion.user_feedback" class="text-sm text-slate-600 mt-1">
        <span class="font-semibold text-slate-700">反馈：</span>
        {{ currentVersion.user_feedback }}
      </p>
    </div>
  </div>
</template>
