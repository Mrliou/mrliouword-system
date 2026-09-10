# Closure Sync 安全操作說明

`Closure Sync` 採 **MRL source-authoritative、fail-closed** 模式。GitHub、外部倉庫與其他平台只作為明確授權的介面或目標，不會自動取得來源權威。

## 必要設定

在 `Mrliou/mrliouword-system` 建立下列 repository variables：

- `MRL_SYNC_ALLOWED_OWNER`：允許的 GitHub owner；預設為目前 repository owner。
- `MRL_SYNC_TARGET_1`：必要，格式 `owner/repository`。
- `MRL_SYNC_TARGET_2`：選用，格式 `owner/repository`。

建立 repository secret：

- `SYNC_TOKEN`：只授權目前 source 與核准 targets 的 fine-grained token；只開放 Contents 所需最小權限。不要使用涵蓋所有私人倉庫的 classic `repo` token。

若 target owner 不符合 allowlist、target 缺失或 token 未設定，workflow 必須失敗，不得回退至其他 owner。

## 安全預設

- schedule 與 push 事件只以 `observe` 模式執行。
- manual dispatch 預設 `mode=observe`、`dry_run=true`。
- 只有人工選擇 `mode=full` 且 `dry_run=false` 時才允許 source→target 複製及提交。
- 寫入結果只推送至 `Mrliou_MRL_closure_sync/<run_id>` 候選分支；workflow 不直接推送 main，也不自動合併。
- target 多出的檔案只列入 `extra_in_targets`；不會自動反向寫回 source，也不會自動刪除。
- `.mrliou/merkle.json`、health 與 reports 是 runtime outputs，不納入自身 Merkle input。
- checkout、verify、commit 或 push 失敗都必須讓 workflow 失敗。

## 解鎖後驗證順序

1. 先確認 GitHub billing/account lock 已解除。
2. 設定核准 owner、targets 與最小權限 token。
3. 執行 `observe + dry_run=true`。
4. 核對 summary 中的 source、targets、owner、mode、apply changes。
5. 執行 `full + dry_run=true`，確認 action plan 與 mismatch。
6. 人工核准後才執行 `full + dry_run=false`，再逐一審查候選分支差異。

不得以重新執行舊的 write-enabled run #86 作為首次解鎖測試。

## 本機驗證

```bash
python -m pytest tests/test_closure_sync_safety.py -q
python tools/sync_manager.py --source . --targets ../approved-target --mode full --dry-run --report .mrliou/sync_report.json
python tools/verify_consistency.py . ../approved-target --check-merkle --cross-repo
```

**origin_signature**: `MrLiouWord`
