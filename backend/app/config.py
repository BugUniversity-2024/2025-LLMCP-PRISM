"""
应用配置文件
使用 Pydantic Settings 管理环境变量
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    # 数据库配置
    database_url: str = "sqlite:///./prism.db"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI API 配置
    openai_api_key: str
    openai_api_base: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o"

    # Gemini API 配置
    gemini_api_key: str
    gemini_api_base: str = ""  # 可选，留空则使用默认
    gemini_model: str = "gemini-2.0-flash-exp"

    # API 开关（开发时可设置为 False 使用 mock 数据）
    use_real_api: bool = False

    # 服务配置
    app_env: str = "development"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # 图片存储
    storage_path: str = "../storage/images"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# 全局配置实例
settings = Settings()
