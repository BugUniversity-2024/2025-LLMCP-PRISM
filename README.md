# PRISM

> **Prompt Refinement & Image Synthesis Manager**
>
> 基于 LLM 的 AI 绘画 Prompt 优化中间层

## 项目简介

PRISM 是一个智能 AI 绘画 Prompt 优化系统，解决用户无法写出高质量 Prompt 的痛点。

### 核心功能

- 🎨 **智能 Prompt 生成**：用户用自然语言描述创意，系统生成专业级详细 Prompt
- 🔄 **多轮迭代优化**：通过 Prompt Diff 机制，精确修改并重新生成
- 📊 **版本管理**：支持历史查看、版本对比、任意回滚

### 技术特点

- 📦 结构化 Prompt Schema 设计
- 🤖 基于 GPT-4o 的 Prompt Engineering
- 🔀 创新的 Prompt Diff 机制
- 🏗️ 前后端分离的现代化架构

## 技术栈

### 后端

- **语言**：Python 3.11+
- **框架**：FastAPI
- **数据库**：SQLite + SQLAlchemy 2.0
- **数据库迁移**：Alembic
- **LLM**：OpenAI GPT-4o（支持第三方中转）
- **图像生成**：火山引擎 Seedream API
- **包管理**：UV

### 前端

- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **状态管理**：Pinia
- **UI 库**：Tailwind CSS v4 + shadcn-vue
- **图标**：Heroicons + Lucide
- **包管理**：pnpm

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- UV (Python 包管理器)
- pnpm (Node.js 包管理器)

### 后端启动

1. 配置环境变量：

```bash
cd backend
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys
# 必须配置：
# - OPENAI_API_KEY: GPT-4o API Key
# - ARK_API_KEY: 火山引擎 API Key
# 可选配置：
# - OPENAI_API_BASE: 第三方中转地址
# - USE_REAL_API: true/false (Mock 模式)
```

2. 初始化数据库（首次运行）：

```bash
uv run alembic upgrade head
```

3. 安装依赖并启动：

```bash
uv sync
uv run python main.py
```

后端服务将运行在 `http://localhost:8000`

### 前端启动

```bash
cd frontend
pnpm install
pnpm dev
```

前端服务将运行在 `http://localhost:5173`

## 项目结构

```
prism/
├── backend/              # 后端服务
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心业务逻辑
│   │   ├── services/    # 外部服务
│   │   ├── models/      # 数据库模型
│   │   └── schemas/     # Pydantic schemas
│   ├── prompts/         # System Prompt 模板
│   └── main.py          # 主入口
├── frontend/            # 前端应用
│   └── src/
│       ├── components/  # Vue 组件
│       ├── api/         # API 调用
│       ├── stores/      # 状态管理
│       └── views/       # 页面
├── docs/                # 文档
│   └── 项目方案.md      # 完整技术方案
├── storage/             # 图片存储
└── docker-compose.yml   # Docker 配置
```

## API 文档

后端启动后访问：`http://localhost:8000/docs`

## 开发指南

详细的开发指南请查看 [项目方案文档](./docs/项目方案.md)

## 📚 文档导航

本项目包含完整的技术文档，帮助理解系统设计和开发过程：

### 核心文档

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| **项目报告** | [`docs/项目报告.md`](./docs/项目报告.md) | 📄 完整的学术报告（16000字），包含需求分析、系统架构、LLM调用流程、数据库设计、对话式开发过程总结 |
| **项目方案** | [`docs/项目方案.md`](./docs/项目方案.md) | 📋 详细技术方案（1130行），涵盖背景、架构、实现细节 |
| **API 文档** | [`docs/API文档.md`](./docs/API文档.md) | 🔌 RESTful API 接口文档（902行），包含请求/响应示例 |
| **数据库设计** | [`docs/数据库设计.md`](./docs/数据库设计.md) | 🗄️ 完整的数据库设计文档，包含 ER 图、表结构、索引设计、迁移记录 |
| **系统架构** | [`docs/系统架构.md`](./docs/系统架构.md) | 🏗️ 系统架构图和核心流程说明，包含技术栈详解和部署建议 |
| **团队分工** | [`docs/团队分工.md`](./docs/团队分工.md) | 👥 团队成员分工与贡献说明（含贡献占比） |

### 对话式编程记录

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| **格式化对话记录** | [`docs/formatted_conversations.md`](./docs/formatted_conversations.md) | 💬 97轮对话式编程过程记录（按阶段分组，Markdown格式） |
| **原始对话记录** | [`docs/filtered_prism_conversations.md`](./docs/filtered_prism_conversations.md) | 📝 原始对话数据（JSON格式） |
| **路演建议** | [`docs/roadshow_conversation_highlights.md`](./docs/roadshow_conversation_highlights.md) | 🎤 路演关键亮点提炼与建议 |

### 演示材料

| 文档名称 | 路径 | 说明 |
|---------|------|------|
| **PPT 路演汇报** | [`docs/PRISM项目PPT路演汇报.pptx`](./docs/PRISM项目PPT路演汇报.pptx) | 📊 10分钟路演 PPT |

### 配置文件

| 文件名称 | 路径 | 说明 |
|---------|------|------|
| **环境变量模板** | [`backend/.env.example`](./backend/.env.example) | ⚙️ 包含详细注释的环境变量配置模板 |
| **依赖配置（后端）** | [`backend/pyproject.toml`](./backend/pyproject.toml) | 📦 Python 项目依赖（UV管理） |
| **依赖配置（前端）** | [`frontend/package.json`](./frontend/package.json) | 📦 Node.js 项目依赖（pnpm管理） |

### 快速查找

- **想了解项目整体？** → 先看 [`README.md`](./README.md)（本文件），再看 [`docs/项目报告.md`](./docs/项目报告.md)
- **想了解技术实现？** → 查看 [`docs/项目方案.md`](./docs/项目方案.md) 和 [`docs/系统架构.md`](./docs/系统架构.md)
- **想了解 API？** → 查看 [`docs/API文档.md`](./docs/API文档.md) 或启动后端访问 `/docs`
- **想了解数据库？** → 查看 [`docs/数据库设计.md`](./docs/数据库设计.md)
- **想了解开发过程？** → 查看 [`docs/formatted_conversations.md`](./docs/formatted_conversations.md)
- **准备路演？** → 查看 [`docs/PRISM项目PPT路演汇报.pptx`](./docs/PRISM项目PPT路演汇报.pptx) 和 [`docs/roadshow_conversation_highlights.md`](./docs/roadshow_conversation_highlights.md)

## 团队

- AptS:1547
- AptS:1548

## License

MIT