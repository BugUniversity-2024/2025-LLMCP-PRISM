<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { ChevronRightIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

const currentStep = computed(() => {
  if (!sessionStore.hasSession) return 1
  if (!sessionStore.currentVersion) return 1
  return sessionStore.currentVersion.user_feedback ? 3 : 2
})

const steps = [
  { id: 1, label: '输入创意' },
  { id: 2, label: '生成图片' },
  { id: 3, label: '优化反馈' }
]
</script>

<template>
  <div class="flex items-center justify-center gap-3">
    <div
      v-for="(step, index) in steps"
      :key="step.id"
      class="flex items-center gap-3"
    >
      <div class="flex items-center gap-2">
        <span
          :class="[
            'flex items-center justify-center w-7 h-7 rounded-full text-sm font-medium transition-colors',
            currentStep >= step.id
              ? 'bg-blue-600 text-white'
              : 'bg-slate-200 text-slate-500'
          ]"
        >
          {{ step.id }}
        </span>
        <span
          :class="[
            'text-sm font-medium transition-colors',
            currentStep >= step.id ? 'text-slate-900' : 'text-slate-400'
          ]"
        >
          {{ step.label }}
        </span>
      </div>
      <ChevronRightIcon
        v-if="index < steps.length - 1"
        class="w-4 h-4 text-slate-300"
      />
    </div>
  </div>
</template>
