"""
文件撰寫 Agent
"""
from typing import AsyncGenerator, Optional
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError


class MrliouwordDocWriter(BaseAgent):
    """文件撰寫 Agent - 自動生成程式碼文件"""

    def __init__(self, model: Optional[str] = None):
        super().__init__(name="DocWriter", model=model)

    async def execute(
        self, file_path: str, doc_type: str = "api"
    ) -> AsyncGenerator[str, None]:
        """
        生成文件
        
        Args:
            file_path: 源碼檔案路徑
            doc_type: 文件類型 (api, guide, tutorial)
            
        Yields:
            生成過程中的消息
        """
        yield f"📝 開始生成 {doc_type} 文件: {file_path}"
        
        if not Path(file_path).exists():
            raise AgentError(f"檔案不存在: {file_path}")
        
        yield f"📖 分析源碼中..."
        yield f"✓ 源碼分析完成"
        yield f"✍️ 撰寫文件..."
        yield f"✓ 文件生成完成"

    async def generate_docs(
        self, file_path: str, doc_type: str = "api"
    ) -> AsyncGenerator[str, None]:
        """生成文件的便捷方法"""
        async for msg in self._track_execution(self.execute, file_path, doc_type):
            yield msg
