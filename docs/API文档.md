# PRISM API 技术文档

## 概述

PRISM 提供 RESTful API 接口，用于 AI 绘画 Prompt 生成和迭代优化。

**Base URL**: `http://localhost:8000`

**API Version**: v1

**API Prefix**: `/api/v1`

---

## 目录

- [1. 认证与配置](#1-认证与配置)
- [2. 数据模型](#2-数据模型)
- [3. API 接口](#3-api-接口)
  - [3.1 健康检查](#31-健康检查)
  - [3.2 生成图片](#32-生成图片)
  - [3.3 提交反馈并迭代](#33-提交反馈并迭代)
  - [3.4 获取会话历史](#34-获取会话历史)
  - [3.5 回滚到指定版本](#35-回滚到指定版本)
- [4. 错误处理](#4-错误处理)
- [5. 前端 API 调用示例](#5-前端-api-调用示例)

---

## 1. 认证与配置

### 1.1 环境配置

后端需要配置以下环境变量（`.env` 文件）：

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# SeeDream API
SEEDREAM_API_KEY=your_seedream_api_key_here
SEEDREAM_API_URL=https://api.seedream.com/v1

# 数据库
DATABASE_URL=postgresql://prism:prism_dev_password@localhost:5432/prism

# Redis
REDIS_URL=redis://localhost:6379/0
```

### 1.2 CORS 配置

开发环境允许所有来源（`*`），生产环境需要配置白名单。

---

## 2. 数据模型

### 2.1 Prompt Schema

```typescript
interface PromptSchema {
  subject: string[]          // 主体描述
  appearance: string[]       // 外观细节
  style: string[]            // 画风风格
  composition: string[]      // 构图方式
  lighting: string[]         // 光照描述
  background: string[]       // 背景描述
  quality: string[]          // 质量要求
  negative: string[]         // 负面提示
  weights: {
    style: number            // 风格权重
    realism: number          // 写实程度权重
    [key: string]: number    // 其他自定义权重
  }
}
```

**示例**：
```json
{
  "subject": ["一只猫"],
  "appearance": ["橘色毛发", "蓝色眼睛"],
  "style": ["半写实", "动漫风格"],
  "composition": ["特写", "浅景深"],
  "lighting": ["柔和侧光", "暖色调"],
  "background": ["窗边", "清晨"],
  "quality": ["高清", "细节丰富"],
  "negative": ["模糊", "变形"],
  "weights": {
    "style": 1.0,
    "realism": 0.7
  }
}
```

### 2.2 Prompt Diff

```typescript
interface PromptDiff {
  operations: PromptDiffOperation[]
  reasoning?: string         // 优化说明
}

interface PromptDiffOperation {
  action: 'add' | 'remove' | 'adjust' | 'replace'
  field: string              // 要修改的字段
  values?: string[]          // add/remove 操作的值
  value?: any                // replace 操作的新值
  delta?: number             // adjust 操作的增量
}
```

**示例**：
```json
{
  "operations": [
    {
      "action": "add",
      "field": "lighting",
      "values": ["更亮的环境光", "增加高光"]
    },
    {
      "action": "adjust",
      "field": "weights.lighting",
      "delta": 0.3
    }
  ],
  "reasoning": "用户反馈图片太暗，增加光照描述并提升权重"
}
```

### 2.3 Version

```typescript
interface Version {
  id: string                 // 版本 ID
  session_id: string         // 会话 ID
  version_number: number     // 版本号
  parent_version_id: string | null  // 父版本 ID
  user_input?: string        // 用户输入（首次生成）
  user_feedback?: string     // 用户反馈（迭代优化）
  schema: PromptSchema       // Prompt Schema
  prompt: string             // 生成的自然语言 Prompt
  diff?: PromptDiff          // Prompt Diff（迭代版本才有）
  image_url: string          // 图片 URL
  created_at: string         // 创建时间（ISO 8601）
}
```

### 2.4 Session

```typescript
interface Session {
  id: string                 // 会话 ID
  created_at: string         // 创建时间
  updated_at: string         // 更新时间
  versions: Version[]        // 版本列表
}
```

---

## 3. API 接口

### 3.1 健康检查

**接口**: `GET /health`

**描述**: 检查服务健康状态

**请求**:
```bash
curl http://localhost:8000/health
```

**响应**:
```json
{
  "status": "healthy"
}
```

**状态码**:
- `200`: 服务正常

---

### 3.2 生成图片

**接口**: `POST /api/v1/generate`

**描述**: 根据用户输入生成详细 Prompt 和图片

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```typescript
{
  user_input: string          // 用户的创意描述（必填）
  session_id?: string         // 会话 ID（可选，不提供则创建新会话）
}
```

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "画一只橘猫坐在窗边看日落"
  }'
```

**响应**:
```typescript
{
  session_id: string          // 会话 ID
  version: number             // 版本号（首次生成为 1）
  schema: PromptSchema        // 生成的结构化 Schema
  prompt: string              // 生成的自然语言 Prompt
  image_url: string           // 生成的图片 URL
  created_at: string          // 创建时间（ISO 8601）
}
```

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": 1,
  "schema": {
    "subject": ["一只橘猫", "坐姿"],
    "appearance": ["橘色毛发", "蓝色眼睛"],
    "style": ["半写实", "动漫风格"],
    "composition": ["特写", "浅景深"],
    "lighting": ["柔和侧光", "暖色调", "日落光"],
    "background": ["窗边", "日落"],
    "quality": ["高清", "细节丰富", "16:9"],
    "negative": ["模糊", "变形"],
    "weights": {
      "style": 1.0,
      "realism": 0.7
    }
  },
  "prompt": "画面比例：16:9，高清，细节丰富\n风格要求：半写实，动漫风格...",
  "image_url": "https://storage.prism.com/images/abc-123-v1.png",
  "created_at": "2025-12-18T16:30:00.000Z"
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误（user_input 为空）
- `500`: 服务器错误（GPT-4o 调用失败、图像生成失败）
- `503`: 外部服务不可用（OpenAI/SeeDream API 不可用）

---

### 3.3 提交反馈并迭代

**接口**: `POST /api/v1/feedback`

**描述**: 根据用户反馈优化 Prompt 并重新生成图片

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```typescript
{
  session_id: string          // 会话 ID（必填）
  version: number             // 当前版本号（必填）
  feedback: string            // 用户反馈（必填）
}
```

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "version": 1,
    "feedback": "太暗了，而且背景太复杂"
  }'
```

**响应**:
```typescript
{
  session_id: string          // 会话 ID
  version: number             // 新版本号
  parent_version: number      // 父版本号
  diff: PromptDiff            // Prompt Diff
  schema: PromptSchema        // 优化后的 Schema
  prompt: string              // 优化后的 Prompt
  image_url: string           // 新生成的图片 URL
  created_at: string          // 创建时间
}
```

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": 2,
  "parent_version": 1,
  "diff": {
    "operations": [
      {
        "action": "add",
        "field": "lighting",
        "values": ["更亮的环境光", "增加高光"]
      },
      {
        "action": "adjust",
        "field": "weights.lighting",
        "delta": 0.3
      },
      {
        "action": "replace",
        "field": "background",
        "values": ["窗边", "日落", "简洁背景"]
      }
    ],
    "reasoning": "用户反馈图片太暗且背景复杂，增强光照描述并简化背景"
  },
  "schema": {
    "subject": ["一只橘猫", "坐姿"],
    "appearance": ["橘色毛发", "蓝色眼睛"],
    "style": ["半写实", "动漫风格"],
    "composition": ["特写", "浅景深"],
    "lighting": ["柔和侧光", "暖色调", "日落光", "更亮的环境光", "增加高光"],
    "background": ["窗边", "日落", "简洁背景"],
    "quality": ["高清", "细节丰富", "16:9"],
    "negative": ["模糊", "变形"],
    "weights": {
      "style": 1.0,
      "realism": 0.7,
      "lighting": 1.0
    }
  },
  "prompt": "画面比例：16:9，高清，细节丰富\n风格要求：半写实，动漫风格...\n【光照与氛围】（已优化）\n...",
  "image_url": "https://storage.prism.com/images/abc-123-v2.png",
  "created_at": "2025-12-18T16:35:00.000Z"
}
```

**状态码**:
- `200`: 成功
- `400`: 请求参数错误
- `404`: Session 或 Version 不存在
- `409`: Schema 冲突（修改导致矛盾）
- `500`: 服务器错误

---

### 3.4 获取会话历史

**接口**: `GET /api/v1/sessions/{session_id}/versions`

**描述**: 获取指定会话的所有版本历史

**路径参数**:
- `session_id`: 会话 ID

**请求示例**:
```bash
curl http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/versions
```

**响应**:
```typescript
{
  session_id: string
  versions: Version[]        // 版本数组，按时间顺序排列
}
```

**响应示例**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "versions": [
    {
      "id": "v1-id",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "version_number": 1,
      "parent_version_id": null,
      "user_input": "画一只橘猫坐在窗边看日落",
      "schema": {...},
      "prompt": "...",
      "image_url": "https://storage.prism.com/images/abc-123-v1.png",
      "created_at": "2025-12-18T16:30:00.000Z"
    },
    {
      "id": "v2-id",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "version_number": 2,
      "parent_version_id": "v1-id",
      "user_feedback": "太暗了",
      "diff": {...},
      "schema": {...},
      "prompt": "...",
      "image_url": "https://storage.prism.com/images/abc-123-v2.png",
      "created_at": "2025-12-18T16:35:00.000Z"
    }
  ]
}
```

**状态码**:
- `200`: 成功
- `404`: Session 不存在

---

### 3.5 回滚到指定版本

**接口**: `POST /api/v1/sessions/{session_id}/rollback`

**描述**: 回滚到指定版本，并可选择性地应用新的修改

**路径参数**:
- `session_id`: 会话 ID

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```typescript
{
  target_version: number      // 目标版本号（必填）
  new_feedback?: string       // 新的修改描述（可选）
}
```

**请求示例**:
```bash
curl -X POST http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000/rollback \
  -H "Content-Type: application/json" \
  -d '{
    "target_version": 1,
    "new_feedback": "在版本1的基础上，把猫改成黑色"
  }'
```

**响应**:
```typescript
{
  session_id: string
  version: number             // 新版本号
  parent_version: number      // 父版本号（即 target_version）
  diff?: PromptDiff           // Prompt Diff（如果提供了 new_feedback）
  schema: PromptSchema
  prompt: string
  image_url: string
  created_at: string
}
```

**状态码**:
- `200`: 成功
- `404`: Session 或 Version 不存在
- `400`: 请求参数错误

---

## 4. 错误处理

### 4.1 错误响应格式

```typescript
{
  detail: string              // 错误描述
  error_code?: string         // 错误代码
  field?: string              // 错误相关字段（可选）
}
```

### 4.2 常见错误

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 400 | `INVALID_INPUT` | 用户输入为空或格式错误 |
| 404 | `SESSION_NOT_FOUND` | 会话不存在 |
| 404 | `VERSION_NOT_FOUND` | 版本不存在 |
| 409 | `SCHEMA_CONFLICT` | Schema 冲突（修改导致矛盾） |
| 500 | `OPENAI_ERROR` | OpenAI API 调用失败 |
| 500 | `SEEDREAM_ERROR` | SeeDream API 调用失败 |
| 503 | `SERVICE_UNAVAILABLE` | 外部服务不可用 |

**错误示例**:
```json
{
  "detail": "用户输入不能为空",
  "error_code": "INVALID_INPUT",
  "field": "user_input"
}
```

---

## 5. 前端 API 调用示例

### 5.1 API 客户端封装

前端使用 Axios 封装 API 调用（`src/api/prism.ts`）：

```typescript
import axios from 'axios'
import type {
  GenerateRequest,
  GenerateResponse,
  FeedbackRequest,
  FeedbackResponse,
  Session,
} from '@/types'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',           // Vite 代理到 http://localhost:8000/api
  timeout: 60000,            // 60秒超时
  headers: {
    'Content-Type': 'application/json',
  },
})

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// API 方法
export const prismApi = {
  // 生成图片
  async generate(data: GenerateRequest): Promise<GenerateResponse> {
    return api.post('/v1/generate', data)
  },

  // 提交反馈
  async feedback(data: FeedbackRequest): Promise<FeedbackResponse> {
    return api.post('/v1/feedback', data)
  },

  // 获取会话历史
  async getSessionVersions(sessionId: string): Promise<Session> {
    return api.get(`/v1/sessions/${sessionId}/versions`)
  },

  // 回滚到指定版本
  async rollback(sessionId: string, targetVersion: number): Promise<FeedbackResponse> {
    return api.post(`/v1/sessions/${sessionId}/rollback`, {
      target_version: targetVersion,
    })
  },

  // 健康检查
  async health(): Promise<{ status: string }> {
    return api.get('/health')
  },
}
```

### 5.2 在组件中使用

#### 方法1: 直接调用 API

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { prismApi } from '@/api/prism'

const userInput = ref('')

async function handleGenerate() {
  try {
    const response = await prismApi.generate({
      user_input: userInput.value
    })
    console.log('生成成功:', response)
  } catch (error) {
    console.error('生成失败:', error)
  }
}
</script>
```

#### 方法2: 使用 Pinia Store（推荐）

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()
const userInput = ref('')

async function handleGenerate() {
  try {
    await sessionStore.generate(userInput.value)
    // Store 会自动管理状态
  } catch (error) {
    console.error('生成失败:', error)
  }
}
</script>

<template>
  <div>
    <textarea v-model="userInput" />
    <button
      @click="handleGenerate"
      :disabled="sessionStore.loading"
    >
      {{ sessionStore.loading ? '生成中...' : '生成图片' }}
    </button>
  </div>
</template>
```

### 5.3 Pinia Store API

Store 提供了更高级的状态管理（`src/stores/session.ts`）：

```typescript
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()

// 状态
sessionStore.currentSession   // 当前会话
sessionStore.currentVersion   // 当前版本
sessionStore.loading          // 加载状态
sessionStore.error            // 错误信息

// 计算属性
sessionStore.hasSession       // 是否有活动会话
sessionStore.hasVersions      // 是否有版本记录
sessionStore.latestVersion    // 最新版本

// 方法
await sessionStore.generate('画一只猫')                    // 生成图片
await sessionStore.submitFeedback('太暗了')                // 提交反馈
sessionStore.switchToVersion(2)                            // 切换版本
await sessionStore.rollbackTo(1)                           // 回滚到版本1
await sessionStore.loadSession('session-id')               // 加载会话
sessionStore.reset()                                       // 重置状态
```

### 5.4 完整流程示例

```vue
<script setup lang="ts">
import { ref } from 'vue'
import { useSessionStore } from '@/stores/session'

const sessionStore = useSessionStore()
const userInput = ref('')
const feedback = ref('')

// 首次生成
async function generate() {
  await sessionStore.generate(userInput.value)
  userInput.value = ''
}

// 迭代优化
async function optimize() {
  await sessionStore.submitFeedback(feedback.value)
  feedback.value = ''
}

// 切换版本
function switchVersion(versionNumber: number) {
  sessionStore.switchToVersion(versionNumber)
}
</script>

<template>
  <div>
    <!-- 生成 -->
    <input v-model="userInput" />
    <button @click="generate" :disabled="sessionStore.loading">
      生成
    </button>

    <!-- 显示图片 -->
    <img
      v-if="sessionStore.currentVersion"
      :src="sessionStore.currentVersion.image_url"
    />

    <!-- 反馈 -->
    <input v-model="feedback" :disabled="!sessionStore.hasSession" />
    <button @click="optimize" :disabled="sessionStore.loading || !sessionStore.hasSession">
      优化
    </button>

    <!-- 版本历史 -->
    <div v-if="sessionStore.hasVersions">
      <button
        v-for="version in sessionStore.currentSession?.versions"
        :key="version.version_number"
        @click="switchVersion(version.version_number)"
      >
        v{{ version.version_number }}
      </button>
    </div>
  </div>
</template>
```

---

## 6. 开发指南

### 6.1 启动后端

```bash
cd backend

# 启动数据库和 Redis
docker-compose up -d

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API keys

# 启动服务
uv run python main.py
```

后端将运行在：`http://localhost:8000`

API 文档（Swagger UI）：`http://localhost:8000/docs`

### 6.2 启动前端

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

前端将运行在：`http://localhost:5173`

### 6.3 API 代理配置

前端通过 Vite 代理访问后端 API（`vite.config.ts`）：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

这样前端可以通过 `/api/v1/generate` 直接访问后端的 `/api/v1/generate`。

---

## 7. 性能考虑

### 7.1 超时设置

- **前端请求超时**: 60秒（图像生成可能需要较长时间）
- **后端 OpenAI 超时**: 30秒
- **后端 SeeDream 超时**: 45秒

### 7.2 并发控制

- 使用 Redis 作为任务队列
- 限制同时进行的图像生成任务数量

### 7.3 缓存策略

- Prompt Engine 结果缓存（相同输入返回缓存）
- 图片 URL 有效期管理

---

## 8. 安全建议

### 8.1 API Key 管理

- ⚠️ 永远不要在前端暴露 API Keys
- ⚠️ 所有 LLM/图像生成 API 调用必须在后端进行
- ⚠️ 使用环境变量管理敏感信息

### 8.2 输入验证

- 用户输入长度限制（建议 < 1000 字符）
- 防止 SQL 注入（使用 ORM）
- 防止 XSS（前端自动转义）

### 8.3 速率限制

建议实现：
- 每个 IP 每分钟最多 10 次生成请求
- 每个 Session 每天最多 100 次迭代

---

## 9. 版本管理

### 9.1 版本树结构

```
Session: abc-123
│
├─ v1: "画一只猫" (初始生成)
│   │
│   ├─ v2: "太暗了" (迭代优化)
│   │   │
│   │   └─ v3: "背景简化" (继续优化)
│   │
│   └─ v4: "换个角度" (从v1分支)
│
└─ v5: 回滚到v1并修改 "改成黑猫"
```

### 9.2 版本关系

- `parent_version_id`: 指向父版本
- 支持分支（同一个父版本可以有多个子版本）
- 支持回滚（可以从任意版本创建新分支）

---

## 10. Mock 数据说明

当前 API 使用 Mock 数据（假数据）：

- **图片**: 使用 `https://picsum.photos/seed/{随机数}/1920/1080` 提供随机图片
- **Schema**: 使用预定义的假 Schema
- **Prompt**: 根据假 Schema 生成的文本
- **Diff**: 假的优化操作

后续实现真实功能时，需要：
1. 集成 OpenAI API（Prompt Engine）
2. 集成 SeeDream API（图像生成）
3. 实现数据库存储（PostgreSQL）
4. 实现 Prompt Diff 逻辑

---

## 11. 附录

### 11.1 HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 409 | 冲突（Schema 矛盾） |
| 500 | 服务器内部错误 |
| 503 | 外部服务不可用 |

### 11.2 日期时间格式

所有时间字段使用 ISO 8601 格式：

```
2025-12-18T16:30:00.000Z
```

### 11.3 图片格式

- **格式**: PNG / JPEG
- **分辨率**: 1920x1080 (16:9)
- **大小限制**: < 10MB

---

**文档版本**: v1.0
**最后更新**: 2025-12-18
**维护者**：全员协作
