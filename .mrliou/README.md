# 🔄 Closure Sync System (閉環同步系統)

## 概述 (Overview)

基於 **Liou Closure Law (劉氏閉環法則)** 的跨倉庫粒子系統自動同步與一致性驗證系統。

**核心原則**: 怎麼過去，就怎麼回來 (How it goes out, is how it comes back)

## 🎯 同步倉庫 (Synchronized Repositories)

1. **主倉庫 (Source of Truth)**
   - `dofaromg/mrliouword-system` (repo_id: 1130234040)
   - 分支: `main`

2. **同步目標倉庫 (Sync Targets)**
   - `dofaromg/flow-tasks` (repo_id: 1010512921) - `main` 分支
   - `dofaromg/flow-tasks-01` (repo_id: 1146449691) - `main` 分支

## 📁 目錄結構 (Directory Structure)

```
.mrliou/                          # 閉環核心配置
├── meta.json                     # 倉庫元數據與同步目標
├── sync.config.json              # 同步規則配置
├── particle.index.json           # 粒子索引
├── merkle.json                   # Merkle tree 校驗數據
├── consistency.map.json          # 倉庫一致性映射
└── health.json                   # 系統健康狀態

tools/                            # 同步工具
├── merkle_builder.py             # Merkle 樹構建器
├── sync_manager.py               # 閉環同步管理器
├── node_recovery.py              # 節點恢復系統
├── verify_consistency.py         # 一致性驗證器
└── generate_sync_report.py       # 同步報告生成器

core/particles/                   # 粒子數據
└── particle_dict.json            # 粒子字典

docs/particle-dictionary/         # 粒子文檔
├── README.md                     # 文檔說明
└── fluin-mapping-system.md       # Fluin 映射系統
```

## 🔁 閉環五階段 (5 Phases of Closure)

### 1. Observe (可觀測)
收集所有倉庫的狀態信息
- 掃描粒子文件
- 構建 Merkle 樹
- 記錄文件列表

### 2. Resolve (可整合)
解決衝突並生成統一狀態
- 檢測缺失文件
- 識別衝突
- 生成行動計劃

### 3. Mirror (可回寫)
將統一狀態回寫到所有倉庫
- 雙向同步文件
- 自動創建目錄
- 保留文件元數據

### 4. Verify (可驗證)
校驗 Merkle root 一致性
- 重新構建 Merkle 樹
- 比對所有倉庫的根哈希
- 報告不一致

### 5. Loop (可重複)
持續監控並循環同步
- 每 6 小時自動執行
- 代碼變更時觸發
- 支持手動觸發

## 🚀 使用方法 (Usage)

### 命令行工具 (CLI Tools)

#### 構建 Merkle 樹
```bash
python tools/merkle_builder.py . .mrliou/merkle.json
```

#### 執行完整同步
```bash
python tools/sync_manager.py \
  --source . \
  --targets ../repo1,../repo2 \
  --mode full \
  --auto-heal
```

#### 僅觀測模式
```bash
python tools/sync_manager.py \
  --source . \
  --targets ../repo1,../repo2 \
  --mode observe
```

#### 驗證一致性
```bash
python tools/verify_consistency.py \
  . ../repo1 ../repo2 \
  --check-merkle \
  --cross-repo
```

#### 恢復缺失節點
```bash
python tools/node_recovery.py \
  --source . \
  --targets ../repo1,../repo2
```

#### 生成同步報告
```bash
python tools/generate_sync_report.py \
  --source . \
  --targets ../repo1,../repo2 \
  --output .mrliou/sync_report.json
```

### GitHub Actions 自動化

工作流程位於 `.github/workflows/closure-sync.yml`

**觸發條件**:
- 每 6 小時自動執行 (`schedule`)
- 推送到 `main` 分支且修改了粒子文件 (`push`)
- 手動觸發 (`workflow_dispatch`)

**手動觸發**:
1. 進入 Actions 標籤頁
2. 選擇 "🔄 Closure Sync - 閉環同步"
3. 點擊 "Run workflow"
4. 選擇模式和選項

## 🔐 安全配置 (Security Configuration)

### GitHub Token

需要創建 Personal Access Token (PAT) 並設置為 `SYNC_TOKEN` secret:

**權限需求**:
- `repo` - 完整倉庫訪問
- `workflow` - 工作流程訪問

**設置步驟**:
1. 生成 PAT: Settings → Developer settings → Personal access tokens
2. 添加到倉庫: Repository → Settings → Secrets → New repository secret
3. 名稱: `SYNC_TOKEN`
4. 值: 您的 PAT

### 憑證管理

`.gitignore` 已配置忽略敏感文件:
```
config/credentials/*.env
clickhouse_credentials*.txt
*.credentials
```

## 📊 同步路徑 (Sync Paths)

配置於 `.mrliou/sync.config.json`:

1. **粒子數據**: `core/particles/**/*.json`
   - 同步模式: 完整
   - 雙向: 是
   - 衝突策略: 最新 Merkle 勝出

2. **粒子文檔**: `docs/particle-dictionary/**/*.md`
   - 同步模式: 完整
   - 雙向: 是
   - 衝突策略: 手動審查

3. **閉環配置**: `.mrliou/**/*.json`
   - 同步模式: 完整
   - 雙向: 是
   - 衝突策略: 手動審查

## 🧪 測試 (Testing)

### 本地測試

```bash
# 創建測試倉庫
mkdir -p /tmp/test_repo1 /tmp/test_repo2

# 乾運行模式測試
python tools/sync_manager.py \
  --source . \
  --targets /tmp/test_repo1,/tmp/test_repo2 \
  --mode full \
  --dry-run

# 實際同步（小心使用！）
python tools/sync_manager.py \
  --source . \
  --targets /tmp/test_repo1,/tmp/test_repo2 \
  --mode full
```

### 工作流測試

使用 `workflow_dispatch` 手動觸發，選擇 `dry_run: true` 進行安全測試。

## 📈 監控與報告 (Monitoring & Reports)

### 健康狀態

查看 `.mrliou/health.json`:
```json
{
  "last_sync": "2026-02-10T07:28:15Z",
  "status": "healthy",
  "repos": {
    "dofaromg/mrliouword-system": {
      "merkle_root": "abc123...",
      "particle_count": 22,
      "last_verified": "2026-02-10T07:28:15Z"
    }
  }
}
```

### 同步報告

GitHub Actions 會自動生成並上傳同步報告為 artifacts。

## 🐛 故障排除 (Troubleshooting)

### Merkle 不一致

```bash
# 檢查哪個倉庫不一致
python tools/verify_consistency.py . ../repo1 ../repo2 --check-merkle

# 恢復缺失節點
python tools/node_recovery.py --source . --targets ../repo1,../repo2

# 重新驗證
python tools/verify_consistency.py . ../repo1 ../repo2 --check-merkle
```

### 同步失敗

1. 檢查 GitHub Actions 日誌
2. 查看 `.mrliou/health.json` 的 `issues` 欄位
3. 下載 sync report artifact
4. 手動運行同步工具診斷

## 🎓 理論基礎 (Theoretical Foundation)

### Merkle Tree

每個粒子文件的哈希值形成葉節點，逐層組合生成根哈希。只要文件內容相同，Merkle root 必定相同。

### 多源恢復

當某個倉庫缺失文件時，系統會從其他倉庫中尋找有效副本進行恢復。

### 雙向同步

系統支持雙向同步：
- 主倉庫 → 目標倉庫 (常規同步)
- 目標倉庫 → 主倉庫 (反向同步，當目標有新文件時)

## 📚 參考資料 (References)

- [Liou Closure Law](docs/particle-dictionary/fluin-mapping-system.md)
- [Particle Dictionary](core/particles/particle_dict.json)
- [Sync Configuration](.mrliou/sync.config.json)
- [Workflow](.github/workflows/closure-sync.yml)

---

**origin_signature**: MrLiouWord  
**version**: v1.0.0  
**principle**: 怎麼過去，就怎麼回來 ✨
