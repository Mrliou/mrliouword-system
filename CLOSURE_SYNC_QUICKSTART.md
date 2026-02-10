# 🚀 Closure Sync Quick Start Guide

## 快速開始 (Quick Start)

### 1. 前置需求 (Prerequisites)

- Python 3.11+
- Git
- GitHub Personal Access Token (PAT) with `repo` and `workflow` permissions

### 2. 設置 GitHub Token

1. 生成 PAT: https://github.com/settings/tokens
2. 選擇權限: `repo`, `workflow`
3. 在倉庫中添加 Secret:
   - 名稱: `SYNC_TOKEN`
   - 值: 您的 PAT

### 3. 手動測試同步

```bash
# 進入倉庫目錄
cd /path/to/mrliouword-system

# 安裝 Python (如需要)
python3 --version  # 確認版本 >= 3.11

# 測試 Merkle 樹構建
python3 tools/merkle_builder.py . .mrliou/merkle.json

# 驗證當前倉庫一致性
python3 tools/verify_consistency.py . --check-merkle

# 乾運行模式測試同步 (安全)
python3 tools/sync_manager.py \
  --source . \
  --mode observe \
  --report /tmp/test_report.json
```

### 4. 啟用自動同步

工作流程已配置完成！自動同步將在以下情況觸發：

✅ **每 6 小時** - 自動執行  
✅ **推送到 main** - 當修改粒子文件時  
✅ **手動觸發** - 從 GitHub Actions 頁面

### 5. 手動觸發同步

1. 進入 GitHub 倉庫
2. 點擊 **Actions** 標籤頁
3. 選擇 **"🔄 Closure Sync - 閉環同步"**
4. 點擊 **"Run workflow"**
5. 選擇選項:
   - **mode**: `full` (完整同步) 或 `observe` (僅觀測) 或 `verify` (僅驗證)
   - **dry_run**: `true` (乾運行) 或 `false` (實際執行)
6. 點擊 **"Run workflow"** 確認

### 6. 查看同步狀態

#### 方法 1: 查看健康狀態文件
```bash
cat .mrliou/health.json | python3 -m json.tool
```

#### 方法 2: 查看 GitHub Actions
1. 進入 Actions 標籤頁
2. 查看最近的工作流程執行
3. 下載 sync report artifact

#### 方法 3: 運行驗證工具
```bash
python3 tools/verify_consistency.py . --check-merkle
```

### 7. 常見操作 (Common Operations)

#### 僅觀測，不同步
```bash
python3 tools/sync_manager.py --source . --mode observe
```

#### 查看會同步什麼文件 (乾運行)
```bash
python3 tools/sync_manager.py \
  --source . \
  --targets /path/to/target1,/path/to/target2 \
  --mode full \
  --dry-run
```

#### 生成同步報告
```bash
python3 tools/generate_sync_report.py \
  --source . \
  --output sync_report.json
```

#### 驗證 Merkle 一致性
```bash
python3 tools/verify_consistency.py \
  . /path/to/repo1 /path/to/repo2 \
  --check-merkle \
  --cross-repo
```

### 8. 故障排除 (Troubleshooting)

#### 問題: Merkle root 不一致

**解決方案:**
```bash
# 1. 檢查哪裡不一致
python3 tools/verify_consistency.py . ../repo1 ../repo2

# 2. 恢復缺失文件
python3 tools/node_recovery.py \
  --source . \
  --targets ../repo1,../repo2

# 3. 重新驗證
python3 tools/verify_consistency.py . ../repo1 ../repo2
```

#### 問題: 同步失敗

**解決方案:**
1. 檢查 `.mrliou/health.json` 的 `issues` 欄位
2. 查看 GitHub Actions 日誌
3. 確認 `SYNC_TOKEN` 有正確權限
4. 手動運行工具診斷問題

#### 問題: Python 版本不符

**解決方案:**
```bash
# 檢查版本
python3 --version

# 如果 < 3.11，升級 Python
# Ubuntu/Debian:
sudo apt update
sudo apt install python3.11

# macOS:
brew install python@3.11
```

### 9. 安全建議 (Security Best Practices)

✅ 使用 PAT，不要硬編碼密碼  
✅ 定期輪換 Token  
✅ 最小權限原則  
✅ 不要將 `.env` 文件提交到 Git  
✅ 定期檢查 `.mrliou/health.json` 的 `issues`

### 10. 下一步 (Next Steps)

- 📖 閱讀完整文檔: [.mrliou/README.md](.mrliou/README.md)
- 🔍 了解粒子系統: [docs/particle-dictionary/](docs/particle-dictionary/)
- 🛠️ 自定義同步規則: [.mrliou/sync.config.json](.mrliou/sync.config.json)
- 📊 監控健康狀態: [.mrliou/health.json](.mrliou/health.json)

---

**需要幫助?** 查看 [完整文檔](.mrliou/README.md) 或 [GitHub Issues](../../issues)

**origin_signature**: MrLiouWord  
**principle**: 怎麼過去，就怎麼回來 ✨
