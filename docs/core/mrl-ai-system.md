# MRL_AI_SYSTEM 模組說明

## Requested vs Generated

- **Requested**：把 GitHub access-permission 概念吸收、蒸餾、重命名、重組成可落地的 `MRL_AI_SYSTEM` 模組，且要有真實可執行的權限解析、策略合成、風險閘門、升權 hook、trace logging、guardrail enforcement。
- **Generated**：在 `mrliouword_agents.core.mrl_ai_system` 提供可直接匯入的 Python 實作，附帶單元測試、README 入口說明、相依性更新與驗證命令。

## Scope Capture

- Identity / Scope：`Principal.role_bindings`
- Policy Decision：`PolicyRule`、`PolicyComposer`、`PermissionResolver`
- Risk-aware Execution Gating：`RiskAwareExecutionGate`
- Escalation Flow Hooks：`EscalationOrchestrator`
- Decision Trace Logging：`DecisionTraceLogger`
- Guardrail Enforcement：`Guardrail`、`GuardrailEnforcer`

## Files and Dependency Relationships

- `mrliouword_agents/core/mrl_ai_system.py`
  - 新增主模組，依賴 Python 標準庫 dataclasses / datetime / fnmatch / uuid
- `mrliouword_agents/core/__init__.py`
  - 匯出 `MRLAISystem` 與相關資料模型
- `mrliouword_agents/core/config.py`
  - 修正 `pydantic>=2` 下的 `BaseSettings` 相容性，讓測試可執行
- `tests/unit/test_mrl_ai_system.py`
  - 驗證 scope 權限解析、策略合成、風險閘門、升權流程、deny 優先權
- `pyproject.toml` / `setup.py` / `requirements.txt`
  - 新增 `pydantic-settings>=2.14.2`，支援 `BaseSettings` 在 pydantic v2 的實際載入
- `README.md`
  - 新增模組入口與文件連結

## Cross-repo Assumptions

- 本倉庫提供 repository-ready 的 Python 實作。
- 若 `dofaromg/MRL_AI_SYSTEM` 後續需要共用策略包或外部 adapter，本模組介面以純 Python 類別與 callback hook 溝通，不綁定特定 repo。
- 目前沒有在此倉庫中發現直接引用另一個 repo 的程式碼，因此以「文件化介面假設」處理跨 repo 協調需求。

## Usage

```python
from mrliouword_agents.core import Guardrail, MRLAISystem, Principal

system = MRLAISystem(
    guardrails=(
        Guardrail(
            guardrail_id="protect-main",
            actions=("write",),
            resources=("branch:main",),
            scopes=("repo:mrliouword-system",),
            requires_approval=True,
            description="main 分支需要人工核准",
        ),
    )
)

principal = Principal(
    principal_id="user-1",
    role_bindings={"repo:mrliouword-system": ("contributor",)},
)

decision = system.can_execute(
    principal=principal,
    action="write",
    resource="branch:main",
    scope="repo:mrliouword-system",
    context={"protected_branch": True},
)

if decision.escalation_required:
    request = system.request_escalation(principal, decision, "release hotfix")
    system.approve_escalation(request.request_id, "admin-1")
```

## Acceptance Criteria

- [x] `MRL_AI_SYSTEM` 提供真實可執行的 permission resolution
- [x] `MRL_AI_SYSTEM` 提供 policy composition
- [x] `MRL_AI_SYSTEM` 提供 risk-aware execution gating
- [x] `MRL_AI_SYSTEM` 提供 escalation flow hooks
- [x] `MRL_AI_SYSTEM` 提供 decision trace logging
- [x] `MRL_AI_SYSTEM` 提供 guardrail enforcement
- [x] 有對應單元測試
- [x] 有外部使用說明與依賴說明

## Validation Commands

```bash
python -m pytest tests/unit/test_mrl_ai_system.py -q
python -m pytest tests/unit -q
python -m compileall mrliouword_agents
```

## Coverage Report

- **Missing files**: 0
- **Empty files**: 0
- **Placeholder files**: 0
- **Extra files**: 0（僅新增模組、測試、文件與相依性宣告）
- **Mismatch**: 0（模組命名採 Python 慣例 `mrl_ai_system.py`，對外類別名為 `MRLAISystem`）
- **Coverage justification**: 以最小可維護實作完成六個指定能力，並維持現有 Python package 結構。
