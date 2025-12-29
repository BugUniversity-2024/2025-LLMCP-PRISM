<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSessionStore } from '@/stores/session'
import { DocumentTextIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const activeTab = ref('prompt')

const currentVersion = computed(() => sessionStore.currentVersion)
const hasData = computed(() => !!currentVersion.value)

const tabs = computed(() => {
  const baseTabs = [
    { id: 'prompt', label: 'Prompt' },
    { id: 'schema', label: 'Schema' }
  ]

  if (currentVersion.value?.user_input) {
    baseTabs.unshift({ id: 'input', label: '用户输入' })
  }

  if (currentVersion.value?.diff) {
    baseTabs.splice(2, 0, { id: 'diff', label: '优化详情' })
  }

  return baseTabs
})
</script>

<template>
  <div class="bg-white rounded-lg border border-slate-200">
    <div v-if="hasData">
      <!-- Tabs Header -->
      <div class="border-b border-slate-200">
        <div class="flex px-6 pt-4 gap-6">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            :class="[
              'pb-3 border-b-2 text-sm font-medium transition-colors',
              activeTab === tab.id
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            ]"
            @click="activeTab = tab.id"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <!-- Tab Content -->
      <div class="p-6">
        <!-- 用户输入 Tab -->
        <div v-show="activeTab === 'input'" v-if="currentVersion!.user_input">
          <div class="bg-slate-50 rounded-lg p-4 border border-slate-200">
            <p class="text-sm text-slate-700 leading-relaxed">{{ currentVersion!.user_input }}</p>
          </div>
          <div v-if="currentVersion!.user_feedback" class="mt-4 bg-blue-50 rounded-lg p-4 border border-blue-200">
            <p class="text-xs text-slate-600 font-semibold mb-2">用户反馈</p>
            <p class="text-sm text-slate-700">{{ currentVersion!.user_feedback }}</p>
          </div>
        </div>

        <!-- Prompt Tab -->
        <div v-show="activeTab === 'prompt'">
          <pre class="text-sm text-slate-700 font-mono whitespace-pre-wrap leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-200 max-h-96 overflow-y-auto">{{ currentVersion!.prompt }}</pre>
        </div>

        <!-- Diff Tab -->
        <div v-show="activeTab === 'diff'" v-if="currentVersion!.diff">
          <div class="space-y-4">
            <!-- 优化说明 -->
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p class="text-xs text-blue-900 font-semibold mb-2">优化说明</p>
              <p class="text-sm text-slate-700 leading-relaxed">{{ currentVersion!.diff.reasoning }}</p>
            </div>

            <!-- 操作列表 -->
            <div class="space-y-2">
              <p class="text-xs text-slate-600 font-semibold mb-3">变更操作</p>
              <div
                v-for="(op, index) in currentVersion!.diff.operations"
                :key="index"
                class="flex items-start gap-3 text-sm bg-slate-50 p-3 rounded-lg border border-slate-200"
              >
                <span class="px-2 py-0.5 bg-white border border-slate-200 text-slate-700 rounded font-mono text-xs font-semibold">
                  {{ op.action }}
                </span>
                <div class="flex-1">
                  <p class="text-slate-900 font-medium">{{ op.field }}</p>
                  <p v-if="op.values" class="text-xs text-slate-600 mt-1">{{ op.values.join(', ') }}</p>
                  <p v-if="op.delta" class="text-xs text-slate-600 mt-1">delta: {{ op.delta > 0 ? '+' : ''}}{{ op.delta }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Schema Tab -->
        <div v-show="activeTab === 'schema'">
          <pre class="text-xs text-slate-600 font-mono bg-slate-50 p-4 rounded-lg border border-slate-200 max-h-96 overflow-y-auto">{{ JSON.stringify(currentVersion!.schema, null, 2) }}</pre>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="p-16 text-center">
      <DocumentTextIcon class="w-16 h-16 mx-auto text-slate-300 mb-4" />
      <p class="text-sm font-medium text-slate-500">暂无 Prompt 数据</p>
      <p class="text-xs text-slate-400 mt-1">生成图片后查看详情</p>
    </div>
  </div>
</template>
