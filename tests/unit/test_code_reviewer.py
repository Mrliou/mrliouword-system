"""
測試 CodeReviewer
"""
import pytest
from mrliouword_agents.agents.code_reviewer import MrliouwordCodeReviewer


@pytest.mark.asyncio
async def test_code_reviewer_creation():
    """測試 CodeReviewer 建立"""
    reviewer = MrliouwordCodeReviewer()
    assert reviewer.name == "CodeReviewer"


@pytest.mark.asyncio
async def test_code_reviewer_review_code(sample_python_file):
    """測試程式碼審查"""
    reviewer = MrliouwordCodeReviewer()
    messages = []
    
    async for msg in reviewer.review_code(sample_python_file):
        messages.append(msg)
    
    assert len(messages) > 0
    assert any("開始審查" in msg for msg in messages)
