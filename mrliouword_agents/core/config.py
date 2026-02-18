"""
統一的配置管理系統
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional, List
import yaml
from pydantic import BaseSettings, Field


class MrliouwordConfig(BaseSettings):
    """Mrliouword Agent 配置"""

    # 基本設定
    app_name: str = "Mrliouword Agent SDK"
    version: str = "1.0.0"
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")

    # Anthropic API
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    model: str = Field(default="claude-sonnet-4-20250514", env="MODEL")
    max_tokens: int = Field(default=4096, env="MAX_TOKENS")

    # Agent 設定
    default_tools: List[str] = ["Read", "Write", "Edit", "Bash", "Glob"]
    setting_sources: List[str] = ["project"]
    timeout: int = 300  # 秒

    # 日誌設定
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/mrliouword.log", env="LOG_FILE")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # API 設定
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_workers: int = Field(default=4, env="API_WORKERS")

    # 安全設定
    enable_auth: bool = Field(default=False, env="ENABLE_AUTH")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    rate_limit: int = Field(default=100, env="RATE_LIMIT")  # 每小時請求數

    # 監控設定
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    enable_tracing: bool = Field(default=False, env="ENABLE_TRACING")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")

    # 成本追蹤
    track_costs: bool = Field(default=True, env="TRACK_COSTS")
    cost_alert_threshold: float = Field(default=100.0, env="COST_ALERT_THRESHOLD")

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
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(self.dict(), f, default_flow_style=False)


# 全域配置實例
config = MrliouwordConfig()
