/**
 * PRISM API 封装
 */
import axios from 'axios'
import type {
  GenerateRequest,
  GenerateResponse,
  FeedbackRequest,
  FeedbackResponse,
  PreviewResponse,
  Session,
  SessionListItem,
} from '@/types'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 180000, // 图像生成可能需要较长时间（3分钟）
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 方法
export const prismApi = {
  /**
   * 预览 Prompt（不生成图片）
   */
  async preview(userInput: string): Promise<PreviewResponse> {
    return api.post('/v1/preview', { user_input: userInput })
  },

  /**
   * 生成图片
   */
  async generate(data: GenerateRequest): Promise<GenerateResponse> {
    return api.post('/v1/generate', data)
  },

  /**
   * 提交反馈并迭代
   */
  async feedback(sessionId: string, data: FeedbackRequest): Promise<FeedbackResponse> {
    return api.post(`/v1/sessions/${sessionId}/feedback`, data)
  },

  /**
   * 获取会话历史
   */
  async getSessionVersions(sessionId: string): Promise<Session> {
    return api.get(`/v1/sessions/${sessionId}/versions`)
  },

  /**
   * 回滚到指定版本
   */
  async rollback(sessionId: string, targetVersion: number): Promise<FeedbackResponse> {
    return api.post(`/v1/sessions/${sessionId}/rollback`, {
      target_version: targetVersion,
    })
  },

  /**
   * 健康检查
   */
  async health(): Promise<{ status: string }> {
    return api.get('/health')
  },

  /**
   * 获取项目列表
   */
  async listSessions(skip = 0, limit = 20): Promise<{ sessions: SessionListItem[]; total: number }> {
    return api.get('/v1/sessions', { params: { skip, limit } })
  },

  /**
   * 更新项目元数据
   */
  async updateSession(sessionId: string, data: { name?: string; description?: string }): Promise<any> {
    return api.patch(`/v1/sessions/${sessionId}`, data)
  },

  /**
   * 删除项目
   */
  async deleteSession(sessionId: string): Promise<{ status: string; session_id: string }> {
    return api.delete(`/v1/sessions/${sessionId}`)
  },
}

export default api
