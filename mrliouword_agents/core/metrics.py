"""
監控指標系統
"""

import time
from typing import Dict, Optional
from datetime import datetime


class MetricsCollector:
    """收集和管理監控指標"""

    def __init__(self):
        self.metrics: Dict = {
            "requests": 0,
            "errors": 0,
            "total_execution_time": 0,
            "agent_calls": {},
            "start_time": datetime.now().isoformat(),
        }

    def record_request(self):
        """記錄請求"""
        self.metrics["requests"] += 1

    def record_error(self):
        """記錄錯誤"""
        self.metrics["errors"] += 1

    def record_execution_time(self, duration: float):
        """記錄執行時間"""
        self.metrics["total_execution_time"] += duration

    def record_agent_call(self, agent_name: str, duration: float):
        """記錄 Agent 呼叫"""
        if agent_name not in self.metrics["agent_calls"]:
            self.metrics["agent_calls"][agent_name] = {
                "count": 0,
                "total_time": 0,
            }
        self.metrics["agent_calls"][agent_name]["count"] += 1
        self.metrics["agent_calls"][agent_name]["total_time"] += duration

    def get_metrics(self) -> Dict:
        """獲取所有指標"""
        return self.metrics

    def get_summary(self) -> str:
        """獲取指標摘要"""
        avg_time = (
            self.metrics["total_execution_time"] / self.metrics["requests"]
            if self.metrics["requests"] > 0
            else 0
        )
        error_rate = (
            self.metrics["errors"] / self.metrics["requests"] * 100
            if self.metrics["requests"] > 0
            else 0
        )

        summary = f"""
═══════════════════════════════════
Mrliouword Agent SDK - 指標報告
═══════════════════════════════════
總請求數: {self.metrics["requests"]}
錯誤數: {self.metrics["errors"]}
錯誤率: {error_rate:.2f}%
總執行時間: {self.metrics["total_execution_time"]:.2f}秒
平均執行時間: {avg_time:.2f}秒
═══════════════════════════════════
"""
        return summary


# 全域指標收集器
metrics_collector = MetricsCollector()
