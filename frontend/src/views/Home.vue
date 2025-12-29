<script setup lang="ts">
import StepIndicator from '@/components/StepIndicator.vue'
import InputPanel from '@/components/InputPanel.vue'
import VersionList from '@/components/VersionList.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import PromptDetails from '@/components/PromptDetails.vue'
import Lightbox from '@/components/Lightbox.vue'
import { useSessionStore } from '@/stores/session'
import { ref } from 'vue'

const sessionStore = useSessionStore()
const showLightbox = ref(false)

function openLightbox() {
  if (sessionStore.currentVersion) {
    showLightbox.value = true
  }
}
</script>

<template>
  <div class="min-h-screen" style="background: var(--gradient-subtle)">
    <!-- Header: 简洁一行 -->
    <header class="h-14 flex items-center justify-between px-6 border-b border-slate-200/60 bg-white/80 backdrop-blur-sm sticky top-0 z-40">
      <div class="flex items-center gap-3">
        <h1 class="text-xl font-bold text-gradient">PRISM</h1>
        <span class="text-xs text-slate-400 hidden sm:inline">Prompt Refinement & Image Synthesis</span>
      </div>
      <StepIndicator />
    </header>

    <!-- 三栏主体 -->
    <main class="grid grid-cols-12 gap-4 p-4 h-[calc(100vh-56px)]">
      <!-- 左侧：输入区 -->
      <aside class="col-span-12 lg:col-span-3 space-y-4 overflow-y-auto scrollbar-hide animate-slide-up">
        <InputPanel />
        <VersionList v-if="sessionStore.hasVersions" />
      </aside>

      <!-- 中间：图片展示区 -->
      <section class="col-span-12 lg:col-span-6 animate-fade-in" style="animation-delay: 50ms">
        <ImageViewer @open-lightbox="openLightbox" />
      </section>

      <!-- 右侧：详情区 -->
      <aside class="col-span-12 lg:col-span-3 overflow-y-auto scrollbar-hide animate-slide-up" style="animation-delay: 100ms">
        <PromptDetails />
      </aside>
    </main>

    <!-- Lightbox 全屏查看 -->
    <Lightbox v-model:visible="showLightbox" />
  </div>
</template>
