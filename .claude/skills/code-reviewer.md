# Code Reviewer Skill

## 描述

程式碼審查 Agent - 自動審查程式碼品質、安全性和最佳實踐。

## 功能

- 程式碼風格檢查
- 安全漏洞掃描
- 最佳實踐建議
- 效能優化建議
- 技術債務識別

## 使用方式

```python
from mrliouword_agents.agents import MrliouwordCodeReviewer

reviewer = MrliouwordCodeReviewer()
async for msg in reviewer.review_code("app.py", strict_mode=True):
    print(msg)
```

## CLI 使用

```bash
mrliouword review code.py --strict
```
