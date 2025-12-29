<script setup lang="ts">
import { computed, ref } from 'vue'
import { useSessionStore } from '@/stores/session'
import {
  PhotoIcon,
  ArrowsPointingOutIcon,
  ArrowDownTrayIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import Skeleton from './Skeleton.vue'

const emit = defineEmits<{
  openLightbox: []
}>()

const sessionStore = useSessionStore()
const imageLoading = ref(true)

const currentVersion = computed(() => sessionStore.currentVersion)
const hasImage = computed(() => !!currentVersion.value)

const currentVersionIndex = computed(() => {
  if (!sessionStore.currentSession || !currentVersion.value) return -1
  return sessionStore.currentSession.versions.findIndex(
    v => v.version_number === currentVersion.value!.version_number
  )
})

const hasPrevious = computed(() => currentVersionIndex.value > 0)
const hasNext = computed(() => {
  if (!sessionStore.currentSession) return false
  return currentVersionIndex.value < sessionStore.currentSession.versions.length - 1
})

function previousVersion() {
  if (!hasPrevious.value || !sessionStore.currentSession) return
  const prevVersion = sessionStore.currentSession.versions[currentVersionIndex.value - 1]
  sessionStore.switchToVersion(prevVersion.version_number)
  imageLoading.value = true
}

function nextVersion() {
  if (!hasNext.value || !sessionStore.currentSession) return
  const nextVer = sessionStore.currentSession.versions[currentVersionIndex.value + 1]
  sessionStore.switchToVersion(nextVer.version_number)
  imageLoading.value = true
}

function formatTime(isoString: string) {
  const date = new Date(isoString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function downloadImage() {
  if (!currentVersion.value) return
  const link = document.createElement('a')
  link.href = currentVersion.value.image_url
  link.download = `prism-v${currentVersion.value.version_number}.png`
  link.click()
}

function onImageLoad() {
  imageLoading.value = false
}
</script>

<template>
  <div class="card h-full flex flex-col overflow-hidden">
    <div v-if="hasImage" class="flex-1 flex flex-col min-h-0">
      <!-- 图片容器 -->
      <div
        class="flex-1 relative flex items-center justify-center p-4 bg-slate-50/50 cursor-pointer group min-h-0"
        @click="emit('openLightbox')"
      >
        <!-- 骨架屏 -->
        <Skeleton v-if="imageLoading" class="absolute inset-4 rounded-xl" />

        <!-- 图片 -->
        <img
          :src="currentVersion!.image_url"
          :alt="currentVersion!.user_input || '生成的图片'"
          :class="[
            'max-w-full max-h-full object-contain rounded-xl shadow-lg transition-all duration-300',
            imageLoading ? 'opacity-0' : 'opacity-100'
          ]"
          loading="lazy"
          @load="onImageLoad"
        />

        <!-- 悬浮工具栏 -->
        <div class="absolute bottom-6 left-1/2 -translate-x-1/2 flex items-center gap-2 px-4 py-2 bg-white/90 backdrop-blur-md rounded-full shadow-lg opacity-0 group-hover:opacity-100 transition-all duration-200 translate-y-2 group-hover:translate-y-0">
          <button
            @click.stop="emit('openLightbox')"
            class="p-2 hover:bg-slate-100 rounded-full transition-colors"
            title="放大查看"
          >
            <ArrowsPointingOutIcon class="w-4 h-4 text-slate-600" />
          </button>
          <div class="w-px h-4 bg-slate-200" />
          <button
            @click.stop="downloadImage"
            class="p-2 hover:bg-slate-100 rounded-full transition-colors"
            title="下载图片"
          >
            <ArrowDownTrayIcon class="w-4 h-4 text-slate-600" />
          </button>
        </div>
      </div>

      <!-- 底部信息栏 -->
      <div class="flex items-center justify-between px-5 py-3 border-t border-slate-100">
        <div class="flex items-center gap-3">
          <span class="text-sm font-semibold text-slate-800">v{{ currentVersion!.version_number }}</span>
          <span class="text-xs text-slate-400">{{ formatTime(currentVersion!.created_at) }}</span>
        </div>
        <div class="flex items-center gap-1">
          <button
            @click="previousVersion"
            :disabled="!hasPrevious"
            class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="上一个版本"
          >
            <ChevronLeftIcon class="w-4 h-4 text-slate-600" />
          </button>
          <button
            @click="nextVersion"
            :disabled="!hasNext"
            class="p-1.5 hover:bg-slate-100 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="下一个版本"
          >
            <ChevronRightIcon class="w-4 h-4 text-slate-600" />
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center p-8">
      <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-cyan-100 to-sky-100 flex items-center justify-center mb-4">
        <PhotoIcon class="w-10 h-10 text-sky-400" />
      </div>
      <p class="text-sm font-medium text-slate-600 mb-1">暂无图片</p>
      <p class="text-xs text-slate-400">在左侧输入创意并生成</p>
    </div>
  </div>
</template>
