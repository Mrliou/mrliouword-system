# Mrliouword Agent SDK

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

**Mrliouword Agent SDK** 是一個基於 Claude AI 的強大 Agent 開發框架，提供數據分析、程式碼審查、測試生成等多種功能。

## ✨ 特色功能

- 🤖 **智能 Agent** - 多種預建 Agent（數據分析、程式碼審查、測試生成、文件撰寫）
- 📊 **成本追蹤** - 自動追蹤 API 使用成本
- 📈 **監控指標** - 完整的執行時間和錯誤監控
- 🔧 **CLI 工具** - 便捷的命令列介面
- 🌐 **Web API** - FastAPI 驅動的 REST API
- 📝 **完整日誌** - 統一的日誌系統
- 🧠 **粒子記憶倉庫** - 獨立分類保存向量、函數、API 與 AI 初始權重 token
- ⚙️ **靈活配置** - YAML/環境變數配置支援

## 🚀 快速開始

### 安裝

```bash
# 從 PyPI 安裝（未來支援）
pip install mrliouword-agent-sdk

# 或從源碼安裝
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system
pip install -e .
```

### 配置

建立 `.env` 檔案並填入 API 金鑰：

```bash
cp .env.example .env
# 編輯 .env 並填入你的 ANTHROPIC_API_KEY
```

### 使用範例

#### CLI 使用

```bash
# 初始化專案
mrliouword init my-project

# 分析數據
mrliouword analyze data/sales.csv --full

# 審查程式碼
mrliouword review src/app.py --strict

# 查看成本
mrliouword cost
```

#### Python API 使用

```python
import asyncio
from mrliouword_agents.agents import MrliouwordDataAnalyzer

async def main():
    analyzer = MrliouwordDataAnalyzer()
    
    async for message in analyzer.analyze_file("data/sales.csv"):
        print(message)

asyncio.run(main())
```

## 📚 文件

- [快速入門](docs/getting-started.md)
- [架構說明](docs/architecture.md)
- [API 文件](docs/api/)
- [使用範例](examples/)

## 🧪 執行測試

```bash
# 安裝測試依賴
pip install -r requirements-test.txt

# 執行所有測試
pytest

# 執行特定測試
pytest tests/unit/test_data_analyzer.py

# 生成覆蓋率報告
pytest --cov=mrliouword_agents --cov-report=html
```

## 🛠️ 開發

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 安裝 pre-commit hooks
pre-commit install

# 格式化程式碼
black mrliouword_agents/

# 執行 linting
flake8 mrliouword_agents/

# 型別檢查
mypy mrliouword_agents/
```

## 📦 專案結構

```
mrliouword-agent-sdk/
├── mrliouword_agents/     # 核心程式碼
│   ├── core/              # 核心模組
│   ├── agents/            # Agent 實作
│   ├── cli/               # CLI 工具
│   ├── api/               # Web API
│   ├── tools/             # 工具函數
│   └── utils/             # 通用工具
├── tests/                 # 測試
├── examples/              # 使用範例
├── docs/                  # 文件
├── config/                # 配置檔案
└── scripts/               # 工具腳本
```

## 🤝 貢獻

歡迎貢獻！請查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何開始。

## 📄 授權

本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。

## 🙏 致謝

- 基於 [Anthropic Claude](https://www.anthropic.com/) AI
- 感謝所有貢獻者

## 📞 聯絡

- GitHub: [dofaromg/mrliouword-system](https://github.com/dofaromg/mrliouword-system)
- Issues: [GitHub Issues](https://github.com/dofaromg/mrliouword-system/issues)
