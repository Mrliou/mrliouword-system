# Analyze Command

## 描述

快速分析數據檔案

## 語法

```bash
mrliouword analyze <file_path> [--full] [--output <path>]
```

## 參數

- `file_path`: 要分析的檔案路徑
- `--full`: 執行完整分析（選用）
- `--output, -o`: 輸出報告路徑（選用）

## 範例

```bash
# 快速分析
mrliouword analyze sales.csv

# 完整分析
mrliouword analyze sales.csv --full

# 生成報告
mrliouword analyze sales.csv -o report.md
```
