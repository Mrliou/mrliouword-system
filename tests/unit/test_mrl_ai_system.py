"""
測試 MRL_AI_SYSTEM
"""
from mrliouword_agents.core import (
    Guardrail,
    MRLAISystem,
    PolicyRule,
    Principal,
)


def test_permission_resolution_for_repo_scope():
    """測試 scope 權限解析"""
    system = MRLAISystem()
    principal = Principal(
        principal_id="user-1",
        role_bindings={
            "repo:*": ("viewer",),
            "repo:mrliouword-system": ("maintainer",),
        },
    )

    snapshot = system.resolve_permissions(principal, "repo:mrliouword-system")

    assert snapshot.roles == ("maintainer", "viewer")
    assert {"read", "comment", "write", "approve"}.issubset(snapshot.allowed_actions)


def test_policy_composition_replaces_rule_and_prioritizes_deny():
    """測試策略合成會以 deny 覆蓋同名 allow"""
    system = MRLAISystem()
    composed = system.compose_policies(
        (
            PolicyRule(
                rule_id="repo:freeze",
                effect="allow",
                actions=("write",),
                scopes=("repo:mrliouword-system",),
                roles=("contributor",),
            ),
        ),
        (
            PolicyRule(
                rule_id="repo:freeze",
                effect="deny",
                actions=("write",),
                scopes=("repo:mrliouword-system",),
                roles=("contributor",),
                description="凍結期禁止寫入",
            ),
        ),
    )

    assert len(composed) == 1
    assert composed[0].effect == "deny"


def test_guardrail_requires_escalation_and_records_trace():
    """測試高風險操作需要升權且留下 trace"""
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
        principal_id="user-2",
        role_bindings={"repo:mrliouword-system": ("contributor",)},
    )

    decision = system.can_execute(
        principal=principal,
        action="write",
        resource="branch:main",
        scope="repo:mrliouword-system",
        context={"protected_branch": True},
    )

    assert not decision.allowed
    assert decision.escalation_required
    trace = system.get_decision_trace(decision.trace_id)
    assert trace.decision == "deny"
    assert trace.matched_guardrails == ("protect-main",)

    request = system.request_escalation(
        principal=principal,
        decision=decision,
        justification="需要修補 hotfix",
        ttl_seconds=600,
    )
    approved = system.approve_escalation(request.request_id, "admin-1")

    approved_decision = system.can_execute(
        principal=principal,
        action="write",
        resource="branch:main",
        scope="repo:mrliouword-system",
        context={"escalation_request_id": approved.request_id, "protected_branch": True},
    )

    assert approved_decision.allowed


def test_deny_policy_overrides_matching_allow():
    """測試 deny 覆蓋 allow"""
    policies = (
        PolicyRule(
            rule_id="allow-admin-change",
            effect="allow",
            actions=("admin",),
            resources=("repo:settings",),
            scopes=("repo:mrliouword-system",),
            roles=("maintainer",),
        ),
        PolicyRule(
            rule_id="deny-external-admin",
            effect="deny",
            actions=("admin",),
            resources=("repo:settings",),
            scopes=("repo:mrliouword-system",),
            roles=("maintainer",),
            conditions={"outside_collaborator": True},
        ),
    )
    system = MRLAISystem(policies=policies)
    principal = Principal(
        principal_id="user-3",
        role_bindings={"repo:mrliouword-system": ("maintainer",)},
        attributes={"outside_collaborator": True},
    )

    decision = system.can_execute(
        principal=principal,
        action="admin",
        resource="repo:settings",
        scope="repo:mrliouword-system",
        context={"outside_collaborator": True},
    )

    assert not decision.allowed
    assert decision.reason == "策略拒絕此操作"
