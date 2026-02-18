# 貢獻指南

感謝你對 Mrliouword Agent SDK 的興趣！我們歡迎任何形式的貢獻。

## 開發流程

1. Fork 此專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 程式碼規範

### Python 風格指南

- 使用 Black 格式化程式碼
- 遵循 PEP 8 規範
- 添加型別提示
- 撰寫 docstring
- 保持行長度 88 字元

### 提交訊息規範

使用 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文件更新
- `style`: 程式碼格式（不影響功能）
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 雜項任務

範例：
```
feat: 新增數據分析 Agent
fix: 修復成本追蹤錯誤
docs: 更新 API 文件
```

## 測試

### 執行測試

```bash
# 執行所有測試
pytest

# 執行特定測試
pytest tests/unit/test_data_analyzer.py

# 生成覆蓋率報告
pytest --cov=mrliouword_agents --cov-report=html
```

### 撰寫測試

- 每個功能都應該有對應的測試
- 測試覆蓋率應該 > 80%
- 使用描述性的測試名稱
- 測試應該獨立且可重複執行

```python
def test_data_analyzer_should_analyze_csv_file():
    """測試數據分析器能夠分析 CSV 檔案"""
    # Arrange
    analyzer = MrliouwordDataAnalyzer()
    
    # Act
    result = analyzer.analyze_file("test.csv")
    
    # Assert
    assert result is not None
```

## 程式碼審查

提交 PR 前請確保：

1. ✅ 所有測試通過
2. ✅ 程式碼已格式化（`black mrliouword_agents/`）
3. ✅ 無 linting 錯誤（`flake8 mrliouword_agents/`）
4. ✅ 型別檢查通過（`mypy mrliouword_agents/`）
5. ✅ 已更新相關文件
6. ✅ 已添加測試

## 開發環境設定

```bash
# 1. Clone 專案
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system

# 2. 執行設定腳本
./scripts/setup.sh

# 3. 啟動虛擬環境
source venv/bin/activate

# 4. 安裝 pre-commit hooks
pre-commit install
```

## 文件

- 為新功能撰寫文件
- 更新 README.md（如需要）
- 在 docs/ 目錄中添加詳細說明
- 提供使用範例

## 報告問題

使用 GitHub Issues 報告問題時，請包含：

1. 問題描述
2. 重現步驟
3. 預期行為
4. 實際行為
5. 環境資訊（Python 版本、作業系統等）
6. 錯誤訊息或截圖

## 功能請求

我們歡迎功能建議！請在 Issue 中說明：

1. 功能描述
2. 使用場景
3. 預期實作方式（如有想法）

## 取得幫助

如有任何問題，可以：

- 查看 [文件](docs/)
- 搜尋現有的 [Issues](https://github.com/dofaromg/mrliouword-system/issues)
- 開啟新的 Issue
- 在 Pull Request 中提問

## 授權

貢獻的程式碼將採用 MIT 授權。

## 行為準則

請尊重所有貢獻者，保持友善和專業的交流。

---

再次感謝你的貢獻！ 🙏
