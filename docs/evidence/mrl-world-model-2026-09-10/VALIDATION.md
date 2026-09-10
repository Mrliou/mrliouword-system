# MRL 公開證據包驗證閘門

## 檔案清單

| 項目 | 狀態 |
|---|---|
| 存在性、來源歸屬與證據鏈主文 | PASS |
| 機器可讀 JSON manifest | PASS |
| 20 件原始材料 SHA-256 清單 | PASS |
| 本驗證閘門 | PASS |

**Expected: 4 / Actual: 4 / Completion: 100%**

## 一致性閘門

- JSON 語法：PASS
- `artifact_count` 等於 artifacts 陣列長度：PASS（20）
- SHA-256 格式：PASS（20/20）
- SHA-256 唯一性：PASS（20/20）
- 影像尺寸欄位：PASS（20/20 為 1152×1536）
- 外部身份保留：PASS
- 來源與投影分離：PASS
- 第一輪錯置已有追加式修正：PASS
- 私人倉庫資料公開：NO
- 憑證／秘密公開：NO
- 原始影像二進位公開：NO

## 主張邊界閘門

本證據包公開記錄並承認 MRL 世界模型作為一套具來源、定義、組合規則、觀測與版本紀錄的系統存在。它不構成 OpenAI、Trancy 或其他第三方的官方背書，也不聲稱已證明外部黑箱的內部實作血緣。

## 重驗指令

```bash
jq -e '.artifact_count == (.artifacts | length)' MRL_WORLD_MODEL_OBSERVATION_2026-09-10.manifest.json
jq -e '[.artifacts[].sha256] | length == (unique | length)' MRL_WORLD_MODEL_OBSERVATION_2026-09-10.manifest.json
sha256sum -c MRL_WORLD_MODEL_OBSERVATION_2026-09-10.sha256
```

最後一項需在持有 20 張原始影像的目錄執行；公開倉庫不含影像本體。
