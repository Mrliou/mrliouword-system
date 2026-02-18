"""
基礎 Agent 類別
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, AsyncGenerator
from datetime import datetime

from .config import config
from .logger import get_logger
from .exceptions import AgentError
from .metrics import metrics_collector
from .cost_tracker import CostTracker


class BaseAgent(ABC):
    """Mrliouword Agent 基礎類別"""

    def __init__(
        self,
        name: str,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        self.name = name
        self.model = model or config.model
        self.max_tokens = max_tokens or config.max_tokens
        self.logger = get_logger(f"agent.{name}")
        self.cost_tracker = CostTracker() if config.track_costs else None

        self.logger.info(f"初始化 {name} Agent")

    @abstractmethod
    async def execute(self, *args, **kwargs) -> AsyncGenerator[str, None]:
        """
        執行 Agent 任務
        
        子類必須實現此方法
        
        Yields:
            執行過程中的消息
        """
        pass

    async def _track_execution(self, func, *args, **kwargs):
        """追蹤執行時間和指標"""
        start_time = datetime.now()
        
        try:
            metrics_collector.record_request()
            result = await func(*args, **kwargs)
            
            # 計算執行時間
            duration = (datetime.now() - start_time).total_seconds()
            metrics_collector.record_execution_time(duration)
            metrics_collector.record_agent_call(self.name, duration)
            
            self.logger.info(f"{self.name} 執行完成，耗時: {duration:.2f}秒")
            return result
            
        except Exception as e:
            metrics_collector.record_error()
            self.logger.error(f"{self.name} 執行錯誤: {str(e)}")
            raise AgentError(f"{self.name} 執行失敗: {str(e)}") from e

    def _track_api_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        session_id: Optional[str] = None,
    ):
        """追蹤 API 成本"""
        if self.cost_tracker:
            cost = self.cost_tracker.track_usage(
                self.model, input_tokens, output_tokens, session_id
            )
            self.logger.info(f"API 成本: ${cost:.4f} USD")

    def get_config(self) -> Dict[str, Any]:
        """獲取 Agent 配置"""
        return {
            "name": self.name,
            "model": self.model,
            "max_tokens": self.max_tokens,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', model='{self.model}')>"
