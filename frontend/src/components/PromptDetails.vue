<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { DocumentTextIcon, ClipboardIcon, CheckIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const activeTab = ref('prompt')
const copied = ref(false)

const currentVersion = computed(() => sessionStore.currentVersion)
const hasData = computed(() => !!currentVersion.value)

const tabs = computed(() => {
  const baseTabs = [
    { id: 'prompt', label: 'Prompt' },
    { id: 'schema', label: 'Schema' }
  ]

  if (currentVersion.value?.user_input) {
    baseTabs.unshift({ id: 'input', label: '输入' })
  }

  if (currentVersion.value?.diff) {
    baseTabs.splice(2, 0, { id: 'diff', label: '优化' })
  }

  return baseTabs
})

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch (err) {
    console.error('复制失败:', err)
  }
}
</script>

<template>
  <div class="card h-full flex flex-col overflow-hidden">
    <div v-if="hasData" class="flex flex-col h-full">
      <!-- Tabs Header -->
      <div class="flex items-center gap-1 px-4 pt-4 pb-3 border-b border-slate-100">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          :class="[
            'px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200',
            activeTab === tab.id
              ? 'bg-gradient-to-r from-cyan-500 to-sky-500 text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100'
          ]"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="flex-1 overflow-y-auto p-4 scrollbar-hide">
        <!-- 用户输入 Tab -->
        <div v-show="activeTab === 'input'" v-if="currentVersion!.user_input" class="animate-fade-in">
          <div class="bg-slate-50 rounded-xl p-4">
            <p class="text-sm text-slate-700 leading-relaxed">{{ currentVersion!.user_input }}</p>
          </div>
          <div v-if="currentVersion!.user_feedback" class="mt-3 bg-sky-50 rounded-xl p-4">
            <p class="text-[10px] text-sky-600 font-semibold uppercase tracking-wide mb-2">用户反馈</p>
            <p class="text-sm text-slate-700">{{ currentVersion!.user_feedback }}</p>
          </div>
        </div>

        <!-- Prompt Tab -->
        <div v-show="activeTab === 'prompt'" class="animate-fade-in">
          <div class="relative group">
            <pre class="text-sm text-slate-700 font-mono whitespace-pre-wrap leading-relaxed bg-slate-50 p-4 rounded-xl max-h-[calc(100vh-280px)] overflow-y-auto scrollbar-hide">{{ currentVersion!.prompt }}</pre>
            <button
              @click="copyToClipboard(currentVersion!.prompt)"
              class="absolute top-3 right-3 p-2 bg-white rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-slate-50"
              title="复制"
            >
              <CheckIcon v-if="copied" class="w-4 h-4 text-green-500" />
              <ClipboardIcon v-else class="w-4 h-4 text-slate-500" />
            </button>
          </div>
        </div>

        <!-- Diff Tab -->
        <div v-show="activeTab === 'diff'" v-if="currentVersion!.diff" class="space-y-3 animate-fade-in">
          <!-- 优化说明 -->
          <div class="bg-sky-50 rounded-xl p-4">
            <p class="text-[10px] text-sky-600 font-semibold uppercase tracking-wide mb-2">优化说明</p>
            <p class="text-sm text-slate-700 leading-relaxed">{{ currentVersion!.diff.reasoning }}</p>
          </div>

          <!-- 操作列表 -->
          <div class="space-y-2">
            <p class="text-[10px] text-slate-500 font-semibold uppercase tracking-wide px-1">变更操作</p>
            <div
              v-for="(op, index) in currentVersion!.diff.operations"
              :key="index"
              class="flex items-start gap-3 bg-slate-50 p-3 rounded-xl"
            >
              <span
                :class="[
                  'px-2 py-0.5 rounded-md text-[10px] font-bold uppercase',
                  op.action === 'add' ? 'bg-green-100 text-green-700' :
                  op.action === 'remove' ? 'bg-red-100 text-red-700' :
                  op.action === 'adjust' ? 'bg-amber-100 text-amber-700' :
                  'bg-sky-100 text-sky-700'
                ]"
              >
                {{ op.action }}
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-sm text-slate-800 font-medium">{{ op.field }}</p>
                <p v-if="op.values" class="text-xs text-slate-500 mt-0.5 truncate">{{ op.values.join(', ') }}</p>
                <p v-if="op.delta" class="text-xs text-slate-500 mt-0.5">
                  delta: <span :class="op.delta > 0 ? 'text-green-600' : 'text-red-600'">{{ op.delta > 0 ? '+' : '' }}{{ op.delta }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Schema Tab -->
        <div v-show="activeTab === 'schema'" class="animate-fade-in">
          <div class="relative group">
            <pre class="text-xs text-slate-600 font-mono bg-slate-50 p-4 rounded-xl max-h-[calc(100vh-280px)] overflow-y-auto scrollbar-hide">{{ JSON.stringify(currentVersion!.schema, null, 2) }}</pre>
            <button
              @click="copyToClipboard(JSON.stringify(currentVersion!.schema, null, 2))"
              class="absolute top-3 right-3 p-2 bg-white rounded-lg shadow-sm opacity-0 group-hover:opacity-100 transition-all duration-200 hover:bg-slate-50"
              title="复制"
            >
              <CheckIcon v-if="copied" class="w-4 h-4 text-green-500" />
              <ClipboardIcon v-else class="w-4 h-4 text-slate-500" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="flex-1 flex flex-col items-center justify-center p-8">
      <div class="w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center mb-4">
        <DocumentTextIcon class="w-8 h-8 text-slate-400" />
      </div>
      <p class="text-sm font-medium text-slate-600 mb-1">暂无数据</p>
      <p class="text-xs text-slate-400">生成图片后查看详情</p>
    </div>
  </div>
</template>
