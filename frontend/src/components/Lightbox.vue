<script setup lang="ts">
import { computed, watch, onMounted, onUnmounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import {
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const sessionStore = useSessionStore()

const currentVersion = computed(() => sessionStore.currentVersion)
const versions = computed(() => sessionStore.currentSession?.versions || [])

const currentIndex = computed(() => {
  if (!currentVersion.value) return -1
  return versions.value.findIndex(v => v.version_number === currentVersion.value!.version_number)
})

const hasPrevious = computed(() => currentIndex.value > 0)
const hasNext = computed(() => currentIndex.value < versions.value.length - 1)

function close() {
  emit('update:visible', false)
}

function previous() {
  if (!hasPrevious.value) return
  const prevVersion = versions.value[currentIndex.value - 1]
  sessionStore.switchToVersion(prevVersion.version_number)
}

function next() {
  if (!hasNext.value) return
  const nextVersion = versions.value[currentIndex.value + 1]
  sessionStore.switchToVersion(nextVersion.version_number)
}

function download() {
  if (!currentVersion.value) return
  const link = document.createElement('a')
  link.href = currentVersion.value.image_url
  link.download = `prism-v${currentVersion.value.version_number}.png`
  link.click()
}

function handleKeydown(e: KeyboardEvent) {
  if (!props.visible) return
  switch (e.key) {
    case 'Escape':
      close()
      break
    case 'ArrowLeft':
      previous()
      break
    case 'ArrowRight':
      next()
      break
  }
}

watch(() => props.visible, (visible) => {
  if (visible) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="visible && currentVersion"
        class="fixed inset-0 z-50 flex items-center justify-center"
        @click.self="close"
      >
        <!-- 背景遮罩 -->
        <div class="absolute inset-0 bg-black/90 backdrop-blur-sm" />

        <!-- 关闭按钮 -->
        <button
          @click="close"
          class="absolute top-4 right-4 z-10 p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors"
        >
          <XMarkIcon class="w-6 h-6" />
        </button>

        <!-- 下载按钮 -->
        <button
          @click="download"
          class="absolute top-4 right-16 z-10 p-2 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors"
          title="下载图片"
        >
          <ArrowDownTrayIcon class="w-6 h-6" />
        </button>

        <!-- 上一张 -->
        <button
          v-if="hasPrevious"
          @click="previous"
          class="absolute left-4 top-1/2 -translate-y-1/2 z-10 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors"
        >
          <ChevronLeftIcon class="w-8 h-8" />
        </button>

        <!-- 下一张 -->
        <button
          v-if="hasNext"
          @click="next"
          class="absolute right-4 top-1/2 -translate-y-1/2 z-10 p-3 text-white/70 hover:text-white hover:bg-white/10 rounded-full transition-colors"
        >
          <ChevronRightIcon class="w-8 h-8" />
        </button>

        <!-- 图片 -->
        <img
          :src="currentVersion.image_url"
          :alt="currentVersion.user_input || '生成的图片'"
          class="relative z-10 max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl animate-scale-in"
        />

        <!-- 底部信息 -->
        <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-10 flex items-center gap-4 px-6 py-3 bg-white/10 backdrop-blur-md rounded-full text-white">
          <span class="text-sm font-medium">v{{ currentVersion.version_number }}</span>
          <span class="text-xs text-white/60">{{ currentIndex + 1 }} / {{ versions.length }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
