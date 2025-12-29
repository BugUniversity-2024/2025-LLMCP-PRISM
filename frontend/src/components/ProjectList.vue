<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useSessionStore } from '@/stores/session'
import { FolderIcon, PlusIcon, TrashIcon, PencilIcon } from '@heroicons/vue/24/outline'

const sessionStore = useSessionStore()
const showRenameDialog = ref(false)
const editingSession = ref<{ id: string; name: string } | null>(null)

onMounted(() => {
  sessionStore.fetchSessions()
})

function createNew() {
  sessionStore.reset()
}

function switchProject(sessionId: string) {
  sessionStore.switchToSession(sessionId)
}

function startRename(session: any) {
  editingSession.value = { id: session.id, name: session.name }
  showRenameDialog.value = true
}

async function confirmRename() {
  if (!editingSession.value) return
  await sessionStore.updateSessionName(editingSession.value.name)
  showRenameDialog.value = false
}

async function deleteProject(sessionId: string) {
  if (confirm('确定删除此项目？所有版本和图片将被永久删除。')) {
    await sessionStore.deleteSession(sessionId)
  }
}

function formatDate(isoString: string) {
  const date = new Date(isoString)
  return date.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <div class="card p-5 animate-scale-in">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <FolderIcon class="w-4 h-4 text-sky-500" />
        <h3 class="text-sm font-semibold text-slate-800">我的项目</h3>
        <span class="text-xs text-slate-400">({{ sessionStore.recentSessions.length }})</span>
      </div>
      <button
        @click="createNew"
        class="p-1.5 hover:bg-sky-50 rounded-lg transition-colors text-sky-500"
        title="新建项目"
      >
        <PlusIcon class="w-4 h-4" />
      </button>
    </div>

    <div class="space-y-2 max-h-80 overflow-y-auto scrollbar-hide">
      <div
        v-for="session in sessionStore.recentSessions"
        :key="session.id"
        :class="[
          'group relative p-3 rounded-lg cursor-pointer transition-all',
          sessionStore.currentSession?.id === session.id
            ? 'bg-gradient-to-r from-sky-50 to-cyan-50 border border-sky-200'
            : 'hover:bg-slate-50 border border-transparent'
        ]"
        @click="switchProject(session.id)"
      >
        <div class="flex items-start gap-3">
          <!-- 缩略图 -->
          <div class="w-12 h-12 rounded-lg bg-slate-100 overflow-hidden flex-shrink-0">
            <img
              v-if="session.thumbnail_url"
              :src="session.thumbnail_url"
              class="w-full h-full object-cover"
              loading="lazy"
            />
            <FolderIcon v-else class="w-6 h-6 text-slate-300 m-3" />
          </div>

          <!-- 信息 -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-slate-800 truncate">{{ session.name }}</p>
            <div class="flex items-center gap-2 mt-1">
              <span class="text-xs text-slate-400">{{ session.version_count }} 个版本</span>
              <span class="text-xs text-slate-300">·</span>
              <span class="text-xs text-slate-400">{{ formatDate(session.updated_at) }}</span>
            </div>
          </div>

          <!-- 操作按钮（悬浮显示） -->
          <div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
            <button
              @click.stop="startRename(session)"
              class="p-1 hover:bg-slate-200 rounded"
              title="重命名"
            >
              <PencilIcon class="w-3 h-3 text-slate-500" />
            </button>
            <button
              @click.stop="deleteProject(session.id)"
              class="p-1 hover:bg-red-100 rounded"
              title="删除"
            >
              <TrashIcon class="w-3 h-3 text-red-500" />
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-if="sessionStore.recentSessions.length === 0" class="text-center py-8">
        <FolderIcon class="w-12 h-12 mx-auto text-slate-300 mb-2" />
        <p class="text-sm text-slate-400">暂无项目</p>
      </div>
    </div>

    <!-- 重命名对话框 -->
    <Teleport to="body">
      <div
        v-if="showRenameDialog"
        class="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        @click.self="showRenameDialog = false"
      >
        <div class="bg-white rounded-xl p-6 w-96 animate-scale-in">
          <h3 class="text-lg font-semibold mb-4 text-slate-800">重命名项目</h3>
          <input
            v-if="editingSession"
            v-model="editingSession.name"
            class="w-full px-4 py-2 border border-slate-200 rounded-lg input-glow"
            @keyup.enter="confirmRename"
            autofocus
          />
          <div class="flex gap-2 mt-4">
            <button
              @click="confirmRename"
              class="flex-1 px-4 py-2 btn-gradient text-sm"
            >
              确定
            </button>
            <button
              @click="showRenameDialog = false"
              class="flex-1 px-4 py-2 bg-slate-100 hover:bg-slate-200 rounded-lg text-sm transition-colors"
            >
              取消
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
