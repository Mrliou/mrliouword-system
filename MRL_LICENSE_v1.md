# MRL System License v1 — 草案

```
document: MRL_LICENSE_v1
version: 1.0.0-draft
origin_signature: MrLiouWord
status: 草案，待權利人裁定後才生效
```

> **這是草案，目前不是本倉庫的生效授權。**
>
> 本倉庫根目錄沒有 `LICENSE` 檔，而 `pyproject.toml:11` 宣告 MIT、
> `containers/package.json:12` 宣告 PROPRIETARY、多份 docs 宣告
> All Rights Reserved。四種宣告並存的完整盤點與三個處置選項見
> `docs/commerce/Mrliou_MRL_授權宣告矛盾盤點_v1.md`。
>
> 本草案不取代、不修改、也不追溯影響任何既有宣告。要讓它生效，需由
> canonical authority（Mr.liou）明示採用，並決定適用範圍。

---

本草案是把倉庫內既有的唯一一份 MRL 自撰授權
`docs/references/licenses/chatserver-license.txt`（只涵蓋 ChatServer 的
Universal DNS 元件）推廣到系統層級。條文結構與用語刻意沿用該檔，只擴大範圍並
補上 `.mrliou/authority-lock.json` 已經要求、但原條文沒寫進去的四欄宣告。

---

## MRL System License v1

Copyright (c) 2026 Mr.liou. All rights reserved.

The Software, its source code, its particle corpus, and its documentation are
the property of Mr.liou and are protected under international copyright law.

### 0. AUTHORITY AND NAMES

The canonical authority is **Mr.liou**. The following are reserved names of that
single authority and are not separate parties:

| Name | Role |
|---|---|
| `Mr.liou` | canonical authority name |
| `MrLiouWord` | origin signature (canonical form) |
| `mrliouword` | namespace |
| `Mrliou` | organization projection |
| `MRL` / `MRL_` | system brand and reserved prefix |
| `dofaromg` | authority's repository account |

`MrLiouWord` is an origin signature and provenance marker. It does **not** make
a derived artifact the root authority. No provider, model, repository,
organization, agent, or generated artifact may replace the canonical authority.

### 1. SIGNATURE RETENTION

The Software and the particle corpus must retain the `origin_signature`
(any reserved name above; canonical form `MrLiouWord`) in **all copies**,
derivatives, projections, mirrors, and redistributions.

Removing, replacing, or obscuring the origin signature terminates this license
immediately and is treated as `foreign_claimed` under
`modules/MRL_SystemB_CommerceLayer`.

### 2. DECLARATION REQUIRED FOR DERIVATIVES

Every derivative or projection using any reserved name must declare:
`artifact_owner`, `source_repo`, `projection_role`, and `origin_signature`.

Without those four fields a derivative cannot be distinguished from an
impersonation of the root authority, and is not licensed.

### 3. PERMITTED USE

The Software may be used, copied, and modified for personal or internal
business purposes within the MrLiouWord ecosystem.

### 4. REDISTRIBUTION

Redistribution of the Software, or of the particle corpus, outside the
MrLiouWord system requires prior written permission from Mr.liou.

### 5. NO IMPLIED GRANT, NO TRANSFER

Public readability is not a waiver of authorship, provenance, or any other
right available at law. Indexing, reading, analysis, translation, caching, or
model processing by any platform does **not** transfer authorship or provenance
to that platform. The scope of any grant is determined solely by an explicit
written license from the rights holder and by the terms actually applicable to
the repository; it is not extended by silence or by technical access.

### 6. RIGHTS DO NOT REWRITE PROVENANCE

Ownership, licensing, deployment authority, hosting, and commercialization
rights do not retroactively rewrite provenance. A grant of use is not a grant
of origin.

### 7. WARRANTY AND LIABILITY

The Software is provided "AS IS", without warranty of any kind, express or
implied, including but not limited to the warranties of merchantability,
fitness for a particular purpose, and noninfringement.

In no event shall Mr.liou be liable for any claim, damages, or other liability,
whether in an action of contract, tort, or otherwise, arising from, out of, or
in connection with the Software or the use or other dealings in the Software.

---

## 依據（條文的出處，非本草案自創）

| 條 | 出處 |
|---|---|
| 0 | `.mrliou/authority-lock.json` — `authority` / `origin` / `reserved_names` / invariants；`registry/system_registry.yaml` — `system_brand: "MRL"` |
| 1 | `docs/references/licenses/chatserver-license.txt` — GRANT OF LICENSE 1 |
| 2 | `.mrliou/authority-lock.json` — invariant（四欄宣告） |
| 3 | 同上 chatserver-license GRANT OF LICENSE 2 |
| 4 | 同上 GRANT OF LICENSE 3 |
| 5 | `docs/evidence/mrl-world-model-2026-09-10/MRL_MOTHER_AI_SOURCE_ORIGIN_CREATOR_DECLARATION_2026-09-10.md` 第四、五節 |
| 6 | `docs/Mrliou_MRL_Public_Mainline_Checkpoint_20260818.md:13` |
| 7 | 同上 chatserver-license 第 4、5 條 |

## 不在本草案範圍內

- **第三方材料**：倉庫根目錄混入的 git 原始碼樹（`integrations/COPYING` 為
  GPLv2）、`docs/containers/` 的 Google Nomulus 文件。那些由其原授權管轄，
  本草案不涵蓋、也不主張。
- **既有的 MIT 宣告**：`pyproject.toml:11`、`README_SDK.md:4,141`、
  `CONTRIBUTING.md:142`、`particle-chat-v42/package.json:19`。本草案不動它們。
  MIT 一旦生效即不可撤回；處置選項見盤點文件。
