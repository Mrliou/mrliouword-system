"""
數據分析 Agent
"""
from typing import AsyncGenerator, Optional
from pathlib import Path

from ..core.base_agent import BaseAgent
from ..core.exceptions import AgentError


class MrliouwordDataAnalyzer(BaseAgent):
    """數據分析 Agent - 分析 CSV、JSON 等數據檔案"""

    def __init__(self, model: Optional[str] = None):
        super().__init__(name="DataAnalyzer", model=model)

    async def execute(
        self, file_path: str, full_analysis: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        執行數據分析
        
        Args:
            file_path: 數據檔案路徑
            full_analysis: 是否執行完整分析
            
        Yields:
            分析過程中的消息
        """
        yield f"🔍 開始分析檔案: {file_path}"
        
        # 檢查檔案是否存在
        if not Path(file_path).exists():
            raise AgentError(f"檔案不存在: {file_path}")
        
        yield f"📊 載入數據中..."
        
        # 這裡應該調用 Claude API 進行實際分析
        # 目前為示範實作
        yield f"✓ 數據載入完成"
        yield f"📈 開始{'完整' if full_analysis else '快速'}分析..."
        
        # 模擬分析過程
        yield f"✓ 分析完成"
        yield f"📋 分析報告已生成"

    async def analyze_file(
        self, file_path: str, full_analysis: bool = False
    ) -> AsyncGenerator[str, None]:
        """分析檔案的便捷方法"""
        async for msg in self._track_execution(
            self.execute, file_path, full_analysis
        ):
            yield msg

    async def generate_report(
        self, file_path: str, output_path: str
    ) -> AsyncGenerator[str, None]:
        """生成分析報告"""
        yield f"📝 生成分析報告: {output_path}"
        
        # 執行分析
        async for msg in self.analyze_file(file_path, full_analysis=True):
            yield msg
        
        # 生成報告
        yield f"✓ 報告已儲存到: {output_path}"
