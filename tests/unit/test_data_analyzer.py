"""
測試 DataAnalyzer
"""
import pytest
from mrliouword_agents.agents.data_analyzer import MrliouwordDataAnalyzer


@pytest.mark.asyncio
async def test_data_analyzer_creation():
    """測試 DataAnalyzer 建立"""
    analyzer = MrliouwordDataAnalyzer()
    assert analyzer.name == "DataAnalyzer"


@pytest.mark.asyncio
async def test_data_analyzer_analyze_file(sample_csv_file):
    """測試檔案分析"""
    analyzer = MrliouwordDataAnalyzer()
    messages = []
    
    async for msg in analyzer.analyze_file(sample_csv_file):
        messages.append(msg)
    
    assert len(messages) > 0
    assert any("開始分析" in msg for msg in messages)
