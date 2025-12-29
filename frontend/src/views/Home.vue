<script setup lang="ts">
import StepIndicator from '@/components/StepIndicator.vue'
import WorkPanel from '@/components/WorkPanel.vue'
import ImageViewer from '@/components/ImageViewer.vue'
import PromptDetails from '@/components/PromptDetails.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <!-- Header -->
    <header class="bg-white border-b border-slate-200">
      <div class="container-prism py-6">
        <h1 class="text-2xl font-bold text-slate-900">PRISM</h1>
        <p class="text-sm text-slate-600 mt-1">Prompt Refinement & Image Synthesis Manager</p>
      </div>
    </header>

    <!-- 步骤指示器 -->
    <div class="bg-white border-b border-slate-200">
      <div class="container-prism py-4">
        <StepIndicator />
      </div>
    </div>

    <!-- 主内容区：左右分栏 -->
    <main class="container-prism py-6">
      <div class="grid grid-cols-12 gap-6 min-h-[calc(100vh-240px)]">
        <!-- 左侧工作区 (35%) -->
        <div class="col-span-12 lg:col-span-4 space-y-4 overflow-y-auto">
          <WorkPanel />
        </div>

        <!-- 右侧结果区 (65%) -->
        <div class="col-span-12 lg:col-span-8 space-y-4 overflow-y-auto">
          <ImageViewer />
          <PromptDetails />
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="py-6 text-center text-xs text-slate-500 border-t border-slate-200 bg-white">
      <p class="font-medium">PRISM - Powered by GPT-4o & SeeDream</p>
    </footer>
  </div>
</template>
