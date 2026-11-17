"""
MRL_AI_SYSTEM - GitHub 權限概念蒸餾後的授權模組
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from fnmatch import fnmatch
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
)
from uuid import uuid4

ROLE_ACTIONS: Dict[str, Tuple[str, ...]] = {
    "viewer": ("read",),
    "triage": ("read", "comment"),
    "contributor": ("read", "comment", "write"),
    "maintainer": ("read", "comment", "write", "approve"),
    "admin": ("read", "comment", "write", "approve", "admin"),
}


def _as_tuple(values: Optional[Sequence[str]]) -> Tuple[str, ...]:
    if not values:
        return tuple()
    return tuple(values)


def _matches_any(value: str, patterns: Sequence[str]) -> bool:
    return any(fnmatch(value, pattern) for pattern in patterns)


def _matches_conditions(
    conditions: Mapping[str, Any],
    principal_attributes: Mapping[str, Any],
    context: Mapping[str, Any],
) -> bool:
    if not conditions:
        return True

    merged: Dict[str, Any] = dict(principal_attributes)
    merged.update(context)

    for key, expected in conditions.items():
        actual = merged.get(key)
        if callable(expected):
            if not expected(actual):
                return False
            continue
        if isinstance(expected, (set, tuple, list)):
            if actual not in expected:
                return False
            continue
        if actual != expected:
            return False

    return True


@dataclass(frozen=True)
class Principal:
    """權限主體"""

    principal_id: str
    principal_type: str = "user"
    role_bindings: Mapping[str, Sequence[str]] = field(default_factory=dict)
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PolicyRule:
    """策略規則"""

    rule_id: str
    effect: str = "allow"
    actions: Tuple[str, ...] = ("read",)
    resources: Tuple[str, ...] = ("*",)
    scopes: Tuple[str, ...] = ("*",)
    roles: Tuple[str, ...] = tuple()
    conditions: Mapping[str, Any] = field(default_factory=dict)
    description: str = ""

    def matches(
        self,
        principal: Principal,
        action: str,
        resource: str,
        scope: str,
        context: Mapping[str, Any],
    ) -> bool:
        if self.roles and not set(self.roles).intersection(
            principal_roles(principal, scope)
        ):
            return False
        if not _matches_any(action, self.actions):
            return False
        if not _matches_any(resource, self.resources):
            return False
        if not _matches_any(scope, self.scopes):
            return False
        return _matches_conditions(self.conditions, principal.attributes, context)


@dataclass(frozen=True)
class Guardrail:
    """保護規則"""

    guardrail_id: str
    actions: Tuple[str, ...] = ("*",)
    resources: Tuple[str, ...] = ("*",)
    scopes: Tuple[str, ...] = ("*",)
    blocked_context: Mapping[str, Any] = field(default_factory=dict)
    max_risk: Optional[int] = None
    requires_approval: bool = False
    escalation_allowed: bool = True
    description: str = ""

    def matches(self, action: str, resource: str, scope: str) -> bool:
        return (
            _matches_any(action, self.actions)
            and _matches_any(resource, self.resources)
            and _matches_any(scope, self.scopes)
        )


@dataclass(frozen=True)
class PermissionSnapshot:
    """解析後的權限快照"""

    principal_id: str
    scope: str
    resource: str
    roles: Tuple[str, ...]
    allowed_actions: Tuple[str, ...]
    denied_actions: Tuple[str, ...]
    policy_ids: Tuple[str, ...]


@dataclass(frozen=True)
class PermissionDecision:
    """執行決策"""

    allowed: bool
    action: str
    resource: str
    scope: str
    reason: str
    roles: Tuple[str, ...]
    matched_policies: Tuple[str, ...]
    matched_guardrails: Tuple[str, ...]
    risk_score: int
    escalation_required: bool = False
    trace_id: str = ""


@dataclass(frozen=True)
class DecisionTrace:
    """決策追蹤"""

    trace_id: str
    principal_id: str
    action: str
    resource: str
    scope: str
    decision: str
    reason: str
    roles: Tuple[str, ...]
    matched_policies: Tuple[str, ...]
    matched_guardrails: Tuple[str, ...]
    risk_score: int
    created_at: str


@dataclass(frozen=True)
class EscalationRequest:
    """升權請求"""

    request_id: str
    principal_id: str
    action: str
    resource: str
    scope: str
    justification: str
    status: str
    requested_at: str
    expires_at: str
    approver_id: Optional[str] = None


def principal_roles(principal: Principal, scope: str) -> Tuple[str, ...]:
    roles: set[str] = set()
    for binding_scope, binding_roles in principal.role_bindings.items():
        if fnmatch(scope, binding_scope):
            roles.update(binding_roles)
    return tuple(sorted(roles))


def default_policy_rules() -> Tuple[PolicyRule, ...]:
    rules: List[PolicyRule] = []
    for role, actions in ROLE_ACTIONS.items():
        for action in actions:
            rules.append(
                PolicyRule(
                    rule_id=f"default:{role}:{action}",
                    effect="allow",
                    actions=(action,),
                    roles=(role,),
                    description=f"{role} 可執行 {action}",
                )
            )
    return tuple(rules)


class PolicyComposer:
    """合成策略規則"""

    def compose(self, *policy_sets: Iterable[PolicyRule]) -> Tuple[PolicyRule, ...]:
        merged: Dict[str, PolicyRule] = {}
        for policy_set in policy_sets:
            for rule in policy_set:
                merged[rule.rule_id] = rule

        return tuple(
            sorted(
                merged.values(),
                key=lambda rule: (rule.effect != "deny", rule.rule_id),
            )
        )


class PermissionResolver:
    """解析有效權限"""

    def resolve(
        self,
        principal: Principal,
        scope: str,
        resource: str = "*",
        policies: Sequence[PolicyRule] = (),
        context: Optional[Mapping[str, Any]] = None,
    ) -> PermissionSnapshot:
        resolved_roles = principal_roles(principal, scope)
        allowed_actions: set[str] = set()
        denied_actions: set[str] = set()
        matched_policy_ids: List[str] = []
        effective_context = context or {}

        for role in resolved_roles:
            allowed_actions.update(ROLE_ACTIONS.get(role, tuple()))

        for rule in policies:
            if not rule.matches(principal, "*", resource, scope, effective_context):
                continue
            matched_policy_ids.append(rule.rule_id)
            target = denied_actions if rule.effect == "deny" else allowed_actions
            target.update(rule.actions)

        allowed_actions.difference_update(denied_actions)

        return PermissionSnapshot(
            principal_id=principal.principal_id,
            scope=scope,
            resource=resource,
            roles=resolved_roles,
            allowed_actions=tuple(sorted(allowed_actions)),
            denied_actions=tuple(sorted(denied_actions)),
            policy_ids=tuple(matched_policy_ids),
        )


class DecisionTraceLogger:
    """記錄決策追蹤"""

    def __init__(self):
        self._traces: Dict[str, DecisionTrace] = {}

    def record(
        self,
        principal: Principal,
        decision: PermissionDecision,
    ) -> DecisionTrace:
        trace_id = decision.trace_id or f"trace-{uuid4().hex}"
        trace = DecisionTrace(
            trace_id=trace_id,
            principal_id=principal.principal_id,
            action=decision.action,
            resource=decision.resource,
            scope=decision.scope,
            decision="allow" if decision.allowed else "deny",
            reason=decision.reason,
            roles=decision.roles,
            matched_policies=decision.matched_policies,
            matched_guardrails=decision.matched_guardrails,
            risk_score=decision.risk_score,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._traces[trace_id] = trace
        return trace

    def get(self, trace_id: str) -> DecisionTrace:
        return self._traces[trace_id]


class EscalationOrchestrator:
    """升權流程協調器"""

    def __init__(
        self,
        on_request: Optional[Callable[[EscalationRequest], None]] = None,
        on_approval: Optional[Callable[[EscalationRequest], None]] = None,
    ):
        self._requests: Dict[str, EscalationRequest] = {}
        self._on_request = on_request
        self._on_approval = on_approval

    def request(
        self,
        principal: Principal,
        action: str,
        resource: str,
        scope: str,
        justification: str,
        ttl_seconds: int = 1800,
    ) -> EscalationRequest:
        now = datetime.now(timezone.utc)
        request = EscalationRequest(
            request_id=f"escalation-{uuid4().hex}",
            principal_id=principal.principal_id,
            action=action,
            resource=resource,
            scope=scope,
            justification=justification,
            status="pending",
            requested_at=now.isoformat(),
            expires_at=(now + timedelta(seconds=ttl_seconds)).isoformat(),
        )
        self._requests[request.request_id] = request
        if self._on_request:
            self._on_request(request)
        return request

    def approve(self, request_id: str, approver_id: str) -> EscalationRequest:
        request = self._requests[request_id]
        approved = EscalationRequest(
            **{
                **request.__dict__,
                "status": "approved",
                "approver_id": approver_id,
            }
        )
        self._requests[request_id] = approved
        if self._on_approval:
            self._on_approval(approved)
        return approved

    def get(self, request_id: str) -> EscalationRequest:
        return self._requests[request_id]

    def is_active(self, request_id: str) -> bool:
        request = self._requests.get(request_id)
        if not request or request.status != "approved":
            return False
        return datetime.fromisoformat(request.expires_at) > datetime.now(timezone.utc)


class GuardrailEnforcer:
    """執行保護規則"""

    def evaluate(
        self,
        guardrails: Sequence[Guardrail],
        action: str,
        resource: str,
        scope: str,
        risk_score: int,
        context: Mapping[str, Any],
        approved: bool,
    ) -> Tuple[Tuple[str, ...], bool, Optional[str]]:
        matched_guardrails: List[str] = []
        escalation_required = False

        for guardrail in guardrails:
            if not guardrail.matches(action, resource, scope):
                continue

            matched_guardrails.append(guardrail.guardrail_id)

            if guardrail.blocked_context and _matches_conditions(
                guardrail.blocked_context,
                {},
                context,
            ):
                return (
                    tuple(matched_guardrails),
                    False,
                    guardrail.description or f"{guardrail.guardrail_id} 已阻擋此操作",
                )

            if guardrail.max_risk is not None and risk_score > guardrail.max_risk:
                if guardrail.escalation_allowed and not approved:
                    escalation_required = True
                elif not approved:
                    return (
                        tuple(matched_guardrails),
                        False,
                        guardrail.description or f"{guardrail.guardrail_id} 風險過高",
                    )

            if guardrail.requires_approval and not approved:
                if guardrail.escalation_allowed:
                    escalation_required = True
                else:
                    return (
                        tuple(matched_guardrails),
                        False,
                        guardrail.description or f"{guardrail.guardrail_id} 需要審批",
                    )

        return tuple(matched_guardrails), escalation_required, None


class RiskAwareExecutionGate:
    """風險感知執行閘門"""

    def __init__(
        self,
        resolver: Optional[PermissionResolver] = None,
        enforcer: Optional[GuardrailEnforcer] = None,
        trace_logger: Optional[DecisionTraceLogger] = None,
        escalation_orchestrator: Optional[EscalationOrchestrator] = None,
    ):
        self._resolver = resolver or PermissionResolver()
        self._enforcer = enforcer or GuardrailEnforcer()
        self._trace_logger = trace_logger or DecisionTraceLogger()
        self._escalation_orchestrator = escalation_orchestrator

    def score_risk(
        self,
        action: str,
        resource: str,
        scope: str,
        context: Mapping[str, Any],
    ) -> int:
        score = 0
        if action in {"write", "approve"}:
            score += 30
        if action == "admin":
            score += 50
        if "main" in resource or context.get("protected_branch"):
            score += 25
        if "production" in resource or "production" in scope:
            score += 25
        if context.get("destructive"):
            score += 20
        if context.get("contains_sensitive_data"):
            score += 20
        return min(score, 100)

    def evaluate(
        self,
        principal: Principal,
        action: str,
        resource: str,
        scope: str,
        policies: Sequence[PolicyRule],
        guardrails: Sequence[Guardrail],
        context: Optional[Mapping[str, Any]] = None,
    ) -> PermissionDecision:
        effective_context = dict(context or {})
        snapshot = self._resolver.resolve(
            principal=principal,
            scope=scope,
            resource=resource,
            policies=policies,
            context=effective_context,
        )
        risk_score = self.score_risk(action, resource, scope, effective_context)
        matched_rules = tuple(
            rule.rule_id
            for rule in policies
            if rule.matches(principal, action, resource, scope, effective_context)
        )

        if any(
            rule.effect == "deny" for rule in policies if rule.rule_id in matched_rules
        ):
            decision = PermissionDecision(
                allowed=False,
                action=action,
                resource=resource,
                scope=scope,
                reason="策略拒絕此操作",
                roles=snapshot.roles,
                matched_policies=matched_rules,
                matched_guardrails=tuple(),
                risk_score=risk_score,
                trace_id=f"trace-{uuid4().hex}",
            )
            trace = self._trace_logger.record(principal, decision)
            return PermissionDecision(
                **{**decision.__dict__, "trace_id": trace.trace_id}
            )

        allowed_by_role = (
            action in snapshot.allowed_actions or "*" in snapshot.allowed_actions
        )
        if not allowed_by_role and not any(
            rule.effect == "allow" for rule in policies if rule.rule_id in matched_rules
        ):
            decision = PermissionDecision(
                allowed=False,
                action=action,
                resource=resource,
                scope=scope,
                reason="主體在目前 scope 沒有對應權限",
                roles=snapshot.roles,
                matched_policies=matched_rules,
                matched_guardrails=tuple(),
                risk_score=risk_score,
                trace_id=f"trace-{uuid4().hex}",
            )
            trace = self._trace_logger.record(principal, decision)
            return PermissionDecision(
                **{**decision.__dict__, "trace_id": trace.trace_id}
            )

        request_id = effective_context.get("escalation_request_id")
        approved = bool(effective_context.get("approved"))
        if (
            not approved
            and request_id
            and self._escalation_orchestrator
            and self._escalation_orchestrator.is_active(request_id)
        ):
            approved = True

        matched_guardrails, escalation_required, denial_reason = (
            self._enforcer.evaluate(
                guardrails=guardrails,
                action=action,
                resource=resource,
                scope=scope,
                risk_score=risk_score,
                context=effective_context,
                approved=approved,
            )
        )

        decision = PermissionDecision(
            allowed=not denial_reason and not escalation_required,
            action=action,
            resource=resource,
            scope=scope,
            reason=denial_reason
            or ("需要升權審批" if escalation_required else "允許執行"),
            roles=snapshot.roles,
            matched_policies=matched_rules,
            matched_guardrails=matched_guardrails,
            risk_score=risk_score,
            escalation_required=escalation_required,
            trace_id=f"trace-{uuid4().hex}",
        )
        trace = self._trace_logger.record(principal, decision)
        return PermissionDecision(**{**decision.__dict__, "trace_id": trace.trace_id})


class MRLAISystem:
    """MRL_AI_SYSTEM 統一授權中樞"""

    def __init__(
        self,
        policies: Optional[Sequence[PolicyRule]] = None,
        guardrails: Optional[Sequence[Guardrail]] = None,
        trace_logger: Optional[DecisionTraceLogger] = None,
        escalation_orchestrator: Optional[EscalationOrchestrator] = None,
    ):
        self.policy_composer = PolicyComposer()
        self.permission_resolver = PermissionResolver()
        self.trace_logger = trace_logger or DecisionTraceLogger()
        self.escalation_orchestrator = (
            escalation_orchestrator or EscalationOrchestrator()
        )
        self.guardrails = tuple(guardrails or ())
        self.policies = tuple(policies or default_policy_rules())
        self.execution_gate = RiskAwareExecutionGate(
            resolver=self.permission_resolver,
            trace_logger=self.trace_logger,
            escalation_orchestrator=self.escalation_orchestrator,
        )

    def compose_policies(
        self, *policy_sets: Iterable[PolicyRule]
    ) -> Tuple[PolicyRule, ...]:
        self.policies = self.policy_composer.compose(*policy_sets)
        return self.policies

    def resolve_permissions(
        self,
        principal: Principal,
        scope: str,
        resource: str = "*",
        context: Optional[Mapping[str, Any]] = None,
    ) -> PermissionSnapshot:
        return self.permission_resolver.resolve(
            principal=principal,
            scope=scope,
            resource=resource,
            policies=self.policies,
            context=context,
        )

    def can_execute(
        self,
        principal: Principal,
        action: str,
        resource: str,
        scope: str,
        context: Optional[Mapping[str, Any]] = None,
    ) -> PermissionDecision:
        return self.execution_gate.evaluate(
            principal=principal,
            action=action,
            resource=resource,
            scope=scope,
            policies=self.policies,
            guardrails=self.guardrails,
            context=context,
        )

    def request_escalation(
        self,
        principal: Principal,
        decision: PermissionDecision,
        justification: str,
        ttl_seconds: int = 1800,
    ) -> EscalationRequest:
        return self.escalation_orchestrator.request(
            principal=principal,
            action=decision.action,
            resource=decision.resource,
            scope=decision.scope,
            justification=justification,
            ttl_seconds=ttl_seconds,
        )

    def approve_escalation(
        self, request_id: str, approver_id: str
    ) -> EscalationRequest:
        return self.escalation_orchestrator.approve(request_id, approver_id)

    def get_decision_trace(self, trace_id: str) -> DecisionTrace:
        return self.trace_logger.get(trace_id)
