"""
統一的配置管理系統
"""
from typing import List, Optional
import yaml
from pydantic import Field

from ..version import __version__

try:
    from pydantic_settings import (
        BaseSettings as PydanticBaseSettings,
        SettingsConfigDict as PydanticSettingsConfigDict,
    )
    HAS_PYDANTIC_SETTINGS = True
except ImportError:  # pragma: no cover - pydantic v1 fallback
    from pydantic import BaseSettings as PydanticBaseSettings  # type: ignore

    PydanticSettingsConfigDict = None  # type: ignore[assignment,misc]
    HAS_PYDANTIC_SETTINGS = False


class MrliouwordConfig(PydanticBaseSettings):
    """Mrliouword Agent 配置"""

    if HAS_PYDANTIC_SETTINGS and PydanticSettingsConfigDict is not None:
        model_config = PydanticSettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            populate_by_name=True,
        )

    # 基本設定
    app_name: str = "Mrliouword Agent SDK"
    version: str = __version__
    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    debug: bool = Field(default=False, validation_alias="DEBUG")

    # Anthropic API
    anthropic_api_key: str = Field(default="", validation_alias="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-20250514", validation_alias="MODEL")
    max_tokens: int = Field(default=4096, validation_alias="MAX_TOKENS")

    # Agent 設定
    default_tools: List[str] = ["Read", "Write", "Edit", "Bash", "Glob"]
    setting_sources: List[str] = ["project"]
    timeout: int = 300  # 秒

    # 日誌設定
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    log_file: str = Field(default="logs/mrliouword.log", validation_alias="LOG_FILE")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # API 設定
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_workers: int = Field(default=4, validation_alias="API_WORKERS")

    # 安全設定
    enable_auth: bool = Field(default=False, validation_alias="ENABLE_AUTH")
    api_key: Optional[str] = Field(default=None, validation_alias="API_KEY")
    rate_limit: int = Field(default=100, validation_alias="RATE_LIMIT")  # 每小時請求數

    # 監控設定
    enable_metrics: bool = Field(default=True, validation_alias="ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, validation_alias="ENABLE_TRACING")
    sentry_dsn: Optional[str] = Field(default=None, validation_alias="SENTRY_DSN")

    # 背景記憶同步
    background_memory_enabled: bool = Field(
        default=True, validation_alias="BACKGROUND_MEMORY_ENABLED"
    )
    runtime_memory_dir: str = Field(
        default="data/runtime_memory", validation_alias="RUNTIME_MEMORY_DIR"
    )
    particle_dict_path: Optional[str] = Field(
        default=None, validation_alias="PARTICLE_DICT_PATH"
    )

    # 成本追蹤
    track_costs: bool = Field(default=True, validation_alias="TRACK_COSTS")
    cost_alert_threshold: float = Field(default=100.0, validation_alias="COST_ALERT_THRESHOLD")

    if not HAS_PYDANTIC_SETTINGS:
        class Config:
            env_file = ".env"
            env_file_encoding = "utf-8"

    @classmethod
    def from_yaml(cls, config_file: str) -> "MrliouwordConfig":
        """從 YAML 檔案載入配置"""
        with open(config_file, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)

    def save_to_yaml(self, output_file: str):
        """儲存配置到 YAML"""
        payload = self.model_dump() if hasattr(self, "model_dump") else self.dict()
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(payload, f, default_flow_style=False)


# 全域配置實例
config = MrliouwordConfig()
