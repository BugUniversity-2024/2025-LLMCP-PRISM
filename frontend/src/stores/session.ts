/**
 * PRISM 会话状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import type { Session, Version, GenerateRequest, FeedbackRequest, SessionListItem } from '@/types'
import { prismApi } from '@/api/prism'

export const useSessionStore = defineStore('session', () => {
  // 状态
  const currentSession = ref<Session | null>(null)
  const currentVersion = ref<Version | null>(null)
  const recentSessions = ref<SessionListItem[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 监听当前会话 ID 变化，自动持久化到 localStorage
  watch(
    () => currentSession.value?.id,
    (newId) => {
      if (newId) {
        localStorage.setItem('prism:current_session_id', newId)
      } else {
        localStorage.removeItem('prism:current_session_id')
      }
    }
  )

  // 计算属性
  const hasSession = computed(() => currentSession.value !== null)
  const hasVersions = computed(() => (currentSession.value?.versions.length ?? 0) > 0)
  const latestVersion = computed(() => {
    if (!currentSession.value?.versions.length) return null
    return currentSession.value.versions[currentSession.value.versions.length - 1]
  })

  // 方法

  /**
   * 生成图片
   */
  async function generate(userInput: string) {
    loading.value = true
    error.value = null

    try {
      const request: GenerateRequest = {
        user_input: userInput,
        session_id: currentSession.value?.id,
      }

      const response = await prismApi.generate(request)

      // 更新会话状态
      if (!currentSession.value) {
        currentSession.value = {
          id: response.session_id,
          created_at: response.created_at,
          updated_at: response.created_at,
          versions: [],
        }
      }

      // 添加新版本
      const newVersion: Version = {
        id: `${response.session_id}-v${response.version}`,
        session_id: response.session_id,
        version_number: response.version,
        parent_version_id: null,
        user_input: userInput,
        schema: response.schema,
        prompt: response.prompt,
        image_url: response.image_url,
        created_at: response.created_at,
      }

      currentSession.value.versions.push(newVersion)
      currentVersion.value = newVersion

      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || '生成失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 提交反馈并迭代
   */
  async function submitFeedback(feedback: string) {
    if (!currentSession.value || !currentVersion.value) {
      error.value = '请先生成图片'
      return
    }

    loading.value = true
    error.value = null

    try {
      const request: FeedbackRequest = {
        session_id: currentSession.value.id,
        version: currentVersion.value.version_number,
        feedback,
      }

      const response = await prismApi.feedback(request)

      // 添加新版本
      const newVersion: Version = {
        id: `${response.session_id}-v${response.version}`,
        session_id: response.session_id,
        version_number: response.version,
        parent_version_id: `${response.session_id}-v${response.parent_version}`,
        user_feedback: feedback,
        schema: response.schema,
        prompt: response.prompt,
        diff: response.diff,
        image_url: response.image_url,
        created_at: response.created_at,
      }

      currentSession.value.versions.push(newVersion)
      currentVersion.value = newVersion

      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || '反馈提交失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 切换到指定版本
   */
  function switchToVersion(versionNumber: number) {
    if (!currentSession.value) return

    const version = currentSession.value.versions.find(
      (v) => v.version_number === versionNumber
    )

    if (version) {
      currentVersion.value = version
    }
  }

  /**
   * 回滚到指定版本
   */
  async function rollbackTo(versionNumber: number) {
    if (!currentSession.value) {
      error.value = '没有活动会话'
      return
    }

    loading.value = true
    error.value = null

    try {
      const response = await prismApi.rollback(currentSession.value.id, versionNumber)

      // 添加新版本（基于回滚版本）
      const newVersion: Version = {
        id: `${response.session_id}-v${response.version}`,
        session_id: response.session_id,
        version_number: response.version,
        parent_version_id: `${response.session_id}-v${versionNumber}`,
        schema: response.schema,
        prompt: response.prompt,
        diff: response.diff,
        image_url: response.image_url,
        created_at: response.created_at,
      }

      currentSession.value.versions.push(newVersion)
      currentVersion.value = newVersion

      return response
    } catch (err: any) {
      error.value = err.response?.data?.message || '回滚失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 加载会话历史
   */
  async function loadSession(sessionId: string) {
    loading.value = true
    error.value = null

    try {
      const session = await prismApi.getSessionVersions(sessionId)
      currentSession.value = session
      currentVersion.value = session.versions[session.versions.length - 1] || null
    } catch (err: any) {
      error.value = err.response?.data?.message || '加载会话失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 重置状态
   */
  function reset() {
    currentSession.value = null
    currentVersion.value = null
    loading.value = false
    error.value = null
  }

  /**
   * 从 localStorage 恢复状态
   */
  async function hydrate() {
    const savedId = localStorage.getItem('prism:current_session_id')
    if (savedId) {
      try {
        await loadSession(savedId)
        console.log('✅ 恢复会话:', savedId)
      } catch (err) {
        console.warn('恢复会话失败，可能已被删除')
        localStorage.removeItem('prism:current_session_id')
      }
    }
  }

  /**
   * 获取项目列表
   */
  async function fetchSessions(skip = 0, limit = 20) {
    loading.value = true
    error.value = null

    try {
      const response = await prismApi.listSessions(skip, limit)
      recentSessions.value = response.sessions
      return response
    } catch (err: any) {
      error.value = '获取项目列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 切换到其他项目
   */
  async function switchToSession(sessionId: string) {
    await loadSession(sessionId)
  }

  /**
   * 更新项目名称
   */
  async function updateSessionName(name: string) {
    if (!currentSession.value) return

    try {
      await prismApi.updateSession(currentSession.value.id, { name })
      currentSession.value.name = name

      // 更新列表中的名称
      const item = recentSessions.value.find(s => s.id === currentSession.value!.id)
      if (item) {
        item.name = name
      }
    } catch (err: any) {
      error.value = '更新项目名称失败'
      throw err
    }
  }

  /**
   * 删除项目
   */
  async function deleteSession(sessionId: string) {
    try {
      await prismApi.deleteSession(sessionId)

      // 如果删除的是当前项目，重置状态
      if (currentSession.value?.id === sessionId) {
        reset()
      }

      // 刷新项目列表
      await fetchSessions()
    } catch (err: any) {
      error.value = '删除项目失败'
      throw err
    }
  }

  return {
    // 状态
    currentSession,
    currentVersion,
    recentSessions,
    loading,
    error,

    // 计算属性
    hasSession,
    hasVersions,
    latestVersion,

    // 方法
    generate,
    submitFeedback,
    switchToVersion,
    rollbackTo,
    loadSession,
    reset,
    hydrate,
    fetchSessions,
    switchToSession,
    updateSessionName,
    deleteSession,
  }
})
