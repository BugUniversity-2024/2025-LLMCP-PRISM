/**
 * PRISM 类型定义
 */

// Prompt Schema 定义
export interface PromptSchema {
  id?: string
  version?: number
  subject: string[]
  appearance: string[]
  style: string[]
  composition: string[]
  lighting: string[]
  background: string[]
  quality: string[]
  negative: string[]
  weights: {
    style: number
    realism: number
    [key: string]: number
  }
  metadata?: {
    model: string
    created_at: string
    parent_id: string | null
  }
}

// Prompt Diff 操作
export interface PromptDiffOperation {
  action: 'add' | 'remove' | 'adjust' | 'replace'
  field: string
  values?: string[]
  value?: any
  delta?: number
}

export interface PromptDiff {
  operations: PromptDiffOperation[]
  reasoning?: string
}

// 版本信息
export interface Version {
  id: string
  session_id: string
  version_number: number
  parent_version_id: string | null
  user_input?: string
  user_feedback?: string
  schema: PromptSchema
  prompt: string
  diff?: PromptDiff
  image_url: string
  created_at: string
}

// 会话信息
export interface Session {
  id: string
  name?: string
  description?: string
  created_at: string
  updated_at: string
  versions: Version[]
}

// 会话列表项（用于项目列表）
export interface SessionListItem {
  id: string
  name: string
  description?: string
  thumbnail_url?: string
  version_count: number
  created_at: string
  updated_at: string
}

// API 请求/响应类型
export interface PreviewResponse {
  schema: PromptSchema
  prompt: string
}

export interface GenerateRequest {
  user_input: string
  session_id?: string
  schema?: PromptSchema
  prompt?: string
}

export interface GenerateResponse {
  session_id: string
  version: number
  schema: PromptSchema
  prompt: string
  image_url: string
  created_at: string
}

export interface FeedbackRequest {
  version: number
  feedback: string
}

export interface FeedbackResponse {
  session_id: string
  version: number
  parent_version: number
  diff: PromptDiff
  schema: PromptSchema
  prompt: string
  image_url: string
  created_at: string
}
