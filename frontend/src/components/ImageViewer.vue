<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import {
  PhotoIcon,
  MagnifyingGlassPlusIcon,
  ArrowDownTrayIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

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
}

function nextVersion() {
  if (!hasNext.value || !sessionStore.currentSession) return
  const nextVer = sessionStore.currentSession.versions[currentVersionIndex.value + 1]
  sessionStore.switchToVersion(nextVer.version_number)
}

function formatTime(isoString: string) {
  const date = new Date(isoString)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

function openFullscreen() {
  // TODO: 实现全屏查看
  console.log('打开全屏')
}

function downloadImage() {
  if (!currentVersion.value) return
  const link = document.createElement('a')
  link.href = currentVersion.value.image_url
  link.download = `prism-v${currentVersion.value.version_number}.png`
  link.click()
}
</script>

<template>
  <div class="bg-white rounded-lg border border-slate-200">
    <div v-if="hasImage">
      <!-- 图片容器 -->
      <div class="relative group cursor-pointer" @click="openFullscreen">
        <img
          :src="currentVersion!.image_url"
          :alt="currentVersion!.user_input || '生成的图片'"
          class="w-full h-auto rounded-t-lg"
          loading="lazy"
        />

        <!-- 悬浮工具栏 -->
        <div class="absolute top-4 right-4 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            @click.stop="openFullscreen"
            class="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm hover:bg-white transition-colors"
            title="放大查看"
          >
            <MagnifyingGlassPlusIcon class="w-5 h-5 text-slate-700" />
          </button>
          <button
            @click.stop="downloadImage"
            class="p-2 bg-white/90 backdrop-blur-sm rounded-lg shadow-sm hover:bg-white transition-colors"
            title="下载图片"
          >
            <ArrowDownTrayIcon class="w-5 h-5 text-slate-700" />
          </button>
        </div>
      </div>

      <!-- 图片信息栏 -->
      <div class="p-4 border-t border-slate-200 flex items-center justify-between">
        <div class="text-sm text-slate-600">
          <span class="font-medium text-slate-900">版本 v{{ currentVersion!.version_number }}</span>
          <span class="mx-2 text-slate-300">·</span>
          <span>{{ formatTime(currentVersion!.created_at) }}</span>
        </div>
        <div class="flex gap-1">
          <button
            @click="previousVersion"
            :disabled="!hasPrevious"
            class="p-1.5 hover:bg-slate-100 rounded transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="上一个版本"
          >
            <ChevronLeftIcon class="w-4 h-4 text-slate-700" />
          </button>
          <button
            @click="nextVersion"
            :disabled="!hasNext"
            class="p-1.5 hover:bg-slate-100 rounded transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="下一个版本"
          >
            <ChevronRightIcon class="w-4 h-4 text-slate-700" />
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态（简化，不固定高度） -->
    <div v-else class="p-20 text-center">
      <PhotoIcon class="w-20 h-20 mx-auto text-slate-300 mb-4" />
      <p class="text-sm font-medium text-slate-500">暂无图片</p>
      <p class="text-xs text-slate-400 mt-2">请在左侧输入创意并生成</p>
    </div>
  </div>
</template>
