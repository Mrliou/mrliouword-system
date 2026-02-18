"""
API 成本追蹤系統
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class CostTracker:
    """追蹤 Anthropic API 使用成本"""

    # Claude 4.5 Sonnet 價格 (USD per 1M tokens)
    PRICING = {
        "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
        "claude-haiku-4-20250514": {"input": 0.80, "output": 4.00},
    }

    def __init__(self, storage_file: str = "data/costs.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.costs = self._load_costs()

    def _load_costs(self) -> Dict:
        """載入成本記錄"""
        if self.storage_file.exists():
            with open(self.storage_file, "r") as f:
                return json.load(f)
        return {"total_cost": 0, "sessions": []}

    def _save_costs(self):
        """儲存成本記錄"""
        with open(self.storage_file, "w") as f:
            json.dump(self.costs, f, indent=2)

    def track_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        session_id: Optional[str] = None,
    ) -> float:
        """追蹤單次使用成本"""
        if model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        # 記錄
        session = {
            "timestamp": datetime.now().isoformat(),
            "session_id": session_id,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": total_cost,
        }

        self.costs["sessions"].append(session)
        self.costs["total_cost"] += total_cost
        self._save_costs()

        return total_cost

    def get_total_cost(self) -> float:
        """獲取總成本"""
        return self.costs["total_cost"]

    def get_daily_cost(self, date: Optional[str] = None) -> float:
        """獲取每日成本"""
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        daily_cost = sum(
            s["cost"]
            for s in self.costs["sessions"]
            if s["timestamp"].startswith(target_date)
        )
        return daily_cost

    def generate_report(self) -> str:
        """生成成本報告"""
        total = self.get_total_cost()
        today = self.get_daily_cost()
        sessions = len(self.costs["sessions"])

        report = f"""
═══════════════════════════════════
Mrliouword Agent SDK - 成本報告
═══════════════════════════════════
總成本: ${total:.4f} USD
今日成本: ${today:.4f} USD
總請求數: {sessions}
平均成本: ${(total/sessions if sessions > 0 else 0):.4f} USD/請求
═══════════════════════════════════
"""
        return report
