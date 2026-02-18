"""
程式碼審查 Agent
"""
from typing import AsyncGenerator, Optional
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError


class MrliouwordCodeReviewer(BaseAgent):
    """程式碼審查 Agent - 審查程式碼品質、安全性和最佳實踐"""

    def __init__(self, model: Optional[str] = None):
        super().__init__(name="CodeReviewer", model=model)

    async def execute(
        self, file_path: str, strict_mode: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        執行程式碼審查
        
        Args:
            file_path: 程式碼檔案路徑
            strict_mode: 是否使用嚴格模式
            
        Yields:
            審查過程中的消息
        """
        yield f"🔍 開始審查檔案: {file_path}"
        
        # 檢查檔案是否存在
        if not Path(file_path).exists():
            raise AgentError(f"檔案不存在: {file_path}")
        
        yield f"📖 讀取程式碼中..."
        
        # 這裡應該調用 Claude API 進行實際審查
        # 目前為示範實作
        yield f"✓ 程式碼載入完成"
        yield f"🔎 開始{'嚴格' if strict_mode else '標準'}審查..."
        
        # 模擬審查過程
        yield f"✓ 審查完成"
        yield f"📋 審查報告已生成"

    async def review_code(
        self, file_path: str, strict_mode: bool = False
    ) -> AsyncGenerator[str, None]:
        """審查程式碼的便捷方法"""
        async for msg in self._track_execution(
            self.execute, file_path, strict_mode
        ):
            yield msg

    async def review_directory(
        self, directory_path: str, pattern: str = "*.py"
    ) -> AsyncGenerator[str, None]:
        """審查整個目錄"""
        yield f"📁 掃描目錄: {directory_path}"
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise AgentError(f"目錄不存在: {directory_path}")
        
        files = list(dir_path.glob(pattern))
        yield f"找到 {len(files)} 個檔案"
        
        for file in files:
            yield f"\n審查: {file}"
            async for msg in self.review_code(str(file)):
                yield f"  {msg}"
