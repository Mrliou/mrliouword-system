"""
自訂例外類別
"""


class MrliouwordException(Exception):
    """Mrliouword Agent SDK 基礎例外"""

    pass


class ConfigurationError(MrliouwordException):
    """配置錯誤"""

    pass


class AgentError(MrliouwordException):
    """Agent 執行錯誤"""

    pass


class APIError(MrliouwordException):
    """API 呼叫錯誤"""

    pass


class ValidationError(MrliouwordException):
    """輸入驗證錯誤"""

    pass


class AuthenticationError(MrliouwordException):
    """認證錯誤"""

    pass


class RateLimitError(MrliouwordException):
    """速率限制錯誤"""

    pass
