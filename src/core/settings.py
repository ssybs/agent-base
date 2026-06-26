from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# 单层扁平化配置，不再嵌套子模型，完美兼容平铺.env
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # 自动忽略.env里多余的旧变量，解决 extra_forbidden 报错
    )

    # 服务
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    ENV: str = "dev"

    # LLM 通义千问
    LLM_API_KEY: str
    LLM_BASE_URL: str
    LLM_MODEL_NAME: str

    # PostgreSQL
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_HOST: str
    DB_PORT: int

# 全局单例
settings = AppSettings()
