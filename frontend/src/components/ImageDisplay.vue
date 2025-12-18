<script setup lang="ts">
import { computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { PhotoIcon, TagIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()

const currentVersion = computed(() => sessionStore.currentVersion)
const hasImage = computed(() => !!currentVersion.value)
</script>

<template>
  <div class="bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-blue-100/50 hover:border-blue-200 backdrop-blur-sm">
    <h3 class="text-lg font-semibold mb-4 text-slate-800 flex items-center gap-2">
      <PhotoIcon class="w-5 h-5 text-blue-600" />
      生成结果
    </h3>

    <div v-if="hasImage" class="space-y-4">
      <div class="relative overflow-hidden rounded-lg bg-slate-100 border border-slate-200 shadow-md">
        <img
          :src="currentVersion!.image_url"
          :alt="currentVersion!.user_input || '生成的图片'"
          class="w-full h-auto object-cover transition-transform hover:scale-105"
          loading="lazy"
        />
      </div>
      <div class="flex items-center justify-between text-sm text-slate-600 bg-slate-50 px-4 py-2 rounded-lg">
        <span class="font-medium flex items-center gap-1">
          <TagIcon class="w-4 h-4" />
          版本: v{{ currentVersion!.version_number }}
        </span>
        <span class="text-xs text-slate-500">{{ new Date(currentVersion!.created_at).toLocaleTimeString() }}</span>
      </div>
    </div>

    <div v-else class="h-80 flex flex-col items-center justify-center text-slate-400 bg-gradient-to-br from-slate-50 to-blue-50/30 rounded-lg border-2 border-dashed border-slate-200">
      <PhotoIcon class="w-20 h-20 mb-4 text-slate-300" />
      <p class="text-sm font-medium">暂无图片</p>
      <p class="text-xs mt-1">请先在左侧输入创意并生成</p>
    </div>
  </div>
</template>
