# Data Analyzer Skill

## 描述

數據分析 Agent - 能夠分析 CSV、JSON 等數據檔案，提供深入的洞察和報告。

## 功能

- 數據載入和驗證
- 統計分析
- 趨勢識別
- 異常檢測
- 生成可視化報告

## 使用方式

```python
from mrliouword_agents.agents import MrliouwordDataAnalyzer

analyzer = MrliouwordDataAnalyzer()
async for msg in analyzer.analyze_file("data.csv", full_analysis=True):
    print(msg)
```

## CLI 使用

```bash
mrliouword analyze data.csv --full
mrliouword analyze data.csv --output report.md
```
