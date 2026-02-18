"""
測試 BaseAgent
"""
import pytest
from mrliouword_agents.core.base_agent import BaseAgent
from mrliouword_agents.core.exceptions import AgentError


class TestAgent(BaseAgent):
    """測試用 Agent"""

    async def execute(self, *args, **kwargs):
        yield "Test message"


def test_base_agent_creation():
    """測試 Agent 建立"""
    agent = TestAgent(name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.model is not None


def test_base_agent_config():
    """測試 Agent 配置"""
    agent = TestAgent(name="TestAgent", model="test-model")
    config = agent.get_config()
    assert config["name"] == "TestAgent"
    assert config["model"] == "test-model"
