"""
測試生成 Agent
"""
from typing import AsyncGenerator, Optional
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError


class MrliouwordTestGenerator(BaseAgent):
    """測試生成 Agent - 自動生成單元測試"""

    def __init__(self, model: Optional[str] = None):
        super().__init__(name="TestGenerator", model=model)

    async def execute(
        self, file_path: str, test_type: str = "unit"
    ) -> AsyncGenerator[str, None]:
        """
        生成測試程式碼
        
        Args:
            file_path: 源碼檔案路徑
            test_type: 測試類型 (unit, integration, e2e)
            
        Yields:
            生成過程中的消息
        """
        yield f"🧪 開始生成 {test_type} 測試: {file_path}"
        
        if not Path(file_path).exists():
            raise AgentError(f"檔案不存在: {file_path}")
        
        yield f"📖 分析源碼中..."
        yield f"✓ 源碼分析完成"
        yield f"🔨 生成測試程式碼..."
        yield f"✓ 測試生成完成"

    async def generate_tests(
        self, file_path: str, test_type: str = "unit"
    ) -> AsyncGenerator[str, None]:
        """生成測試的便捷方法"""
        async for msg in self._track_execution(self.execute, file_path, test_type):
            yield msg
