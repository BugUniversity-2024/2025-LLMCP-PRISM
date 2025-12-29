<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { CheckIcon } from '@heroicons/vue/24/solid'

const sessionStore = useSessionStore()

const currentStep = computed(() => {
  if (!sessionStore.hasSession) return 1
  if (!sessionStore.currentVersion) return 1
  return sessionStore.currentVersion.user_feedback ? 3 : 2
})

const steps = [
  { id: 1, label: '输入' },
  { id: 2, label: '生成' },
  { id: 3, label: '优化' }
]
</script>

<template>
  <div class="flex items-center gap-1">
    <template v-for="(step, index) in steps" :key="step.id">
      <!-- 步骤指示 -->
      <div
        :class="[
          'flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200',
          currentStep > step.id
            ? 'bg-gradient-to-r from-cyan-500 to-sky-500 text-white'
            : currentStep === step.id
              ? 'bg-sky-100 text-sky-700'
              : 'bg-slate-100 text-slate-400'
        ]"
      >
        <span
          v-if="currentStep > step.id"
          class="w-4 h-4 flex items-center justify-center"
        >
          <CheckIcon class="w-3 h-3" />
        </span>
        <span
          v-else
          :class="[
            'w-4 h-4 flex items-center justify-center rounded-full text-[10px] font-bold',
            currentStep === step.id
              ? 'bg-sky-500 text-white'
              : 'bg-slate-300 text-white'
          ]"
        >
          {{ step.id }}
        </span>
        <span class="hidden sm:inline">{{ step.label }}</span>
      </div>

      <!-- 连接线 -->
      <div
        v-if="index < steps.length - 1"
        :class="[
          'w-6 h-0.5 rounded-full transition-colors duration-200',
          currentStep > step.id ? 'bg-sky-400' : 'bg-slate-200'
        ]"
      />
    </template>
  </div>
</template>
