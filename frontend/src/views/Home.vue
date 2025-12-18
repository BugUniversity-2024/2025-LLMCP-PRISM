<script setup lang="ts">
import InputPanel from '@/components/InputPanel.vue'
import ImageDisplay from '@/components/ImageDisplay.vue'
import FeedbackPanel from '@/components/FeedbackPanel.vue'
import PromptViewer from '@/components/PromptViewer.vue'
import VersionHistory from '@/components/VersionHistory.vue'
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
    <!-- Header with Glass Effect -->
    <header class="sticky top-0 z-10 bg-white/80 backdrop-blur-lg shadow-lg border-b border-purple-100">
      <div class="container-prism py-8">
        <h1 class="text-4xl font-bold text-gradient-purple-blue">
          PRISM
        </h1>
        <p class="text-slate-600 mt-2 text-lg font-medium">
          Prompt Refinement & Image Synthesis Manager
        </p>
      </div>
    </header>

    <!-- Main Content -->
    <main class="container-prism py-10">
      <!-- 2x2 Grid with Better Spacing -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <InputPanel class="transform hover:scale-[1.02] transition-transform duration-300" />
        <ImageDisplay class="transform hover:scale-[1.02] transition-transform duration-300" />
        <FeedbackPanel class="transform hover:scale-[1.02] transition-transform duration-300" />
        <PromptViewer class="transform hover:scale-[1.02] transition-transform duration-300" />
      </div>

      <!-- Version History (Full Width) -->
      <VersionHistory />
    </main>

    <!-- Footer -->
    <footer class="py-8 text-center text-sm text-slate-500">
      <p class="font-medium">PRISM - Powered by GPT-4o & SeeDream</p>
      <p class="mt-1">AptS:1547 & AptS:1548</p>
    </footer>
  </div>
</template>
