"""
Audit Entity Tests — ทดสอบ entity audit
"""

from __future__ import annotations

import pytest
from audit.domain.entities import AuditLog
from audit.domain.exceptions import (
    AuditImmutableDomainError,
    AuditMissingActorError,
    AuditMissingResourceError,
)


def test_actor_required() -> None:
    """Every log must have actor_id — ทุก log ต้องมี actor_id"""
    with pytest.raises(AuditMissingActorError):
        AuditLog(
            action="UPDATE",
            resource_type="Invoice",
            resource_id="inv-001",
            actor_id="",
        )


def test_resource_required() -> None:
    """Resource type/id are required — ต้องมี resource type/id"""
    with pytest.raises(AuditMissingResourceError):
        AuditLog(
            action="UPDATE",
            resource_type="",
            resource_id="",
            actor_id="user-001",
        )


def test_diff_accuracy(sample_log: AuditLog) -> None:
    """diff() must match before/after — diff ต้องตรงกับ before/after"""
    diff = sample_log.diff()
    fields = {d["field"] for d in diff}
    assert fields == {"status", "amount", "note"}
    status = next(d for d in diff if d["field"] == "status")
    assert status["before"] == "DRAFT"
    assert status["after"] == "APPROVED"


def test_diff_empty_when_equal() -> None:
    """diff() empty when states equal — diff ว่างเมื่อ state เท่ากัน"""
    log = AuditLog(
        action="READ",
        resource_type="Invoice",
        resource_id="inv-001",
        actor_id="user-001",
        before_state={"a": 1},
        after_state={"a": 1},
    )
    assert log.diff() == []


def test_property_diff_symmetric() -> None:
    """
    Property: diff(before, after) == -diff(after, before)
    ทดสอบสมบัติ: diff สมมาตร
    """
    before = {"a": 1, "b": 2, "c": 3}
    after = {"a": 1, "b": 99, "c": 3, "d": 4}

    log_fwd = AuditLog(
        action="UPDATE",
        resource_type="X",
        resource_id="1",
        actor_id="u",
        before_state=before,
        after_state=after,
    )
    log_bwd = AuditLog(
        action="UPDATE",
        resource_type="X",
        resource_id="1",
        actor_id="u",
        before_state=after,
        after_state=before,
    )

    fwd = {d["field"]: d for d in log_fwd.diff()}
    bwd = {d["field"]: d for d in log_bwd.diff()}

    assert set(fwd.keys()) == set(bwd.keys()), "fields must match"
    for field, f in fwd.items():
        b = bwd[field]
        assert f["before"] == b["after"]
        assert f["after"] == b["before"]


def test_append_only_mutation_blocked(sample_log: AuditLog) -> None:
    """Attempting to update frozen field must raise — แก้ไข field หลัง freeze ต้อง raise"""
    with pytest.raises(AuditImmutableDomainError):
        sample_log.action = "TAMPERED"


def test_append_only_mutation_blocked_actor(sample_log: AuditLog) -> None:
    with pytest.raises(AuditImmutableDomainError):
        sample_log.actor_id = "attacker"


def test_changes_auto_computed(sample_log: AuditLog) -> None:
    """changes must be auto-computed from before/after — changes ต้องถูกคำนวณอัตโนมัติ"""
    assert len(sample_log.changes) == 3
    assert {c["field"] for c in sample_log.changes} == {"status", "amount", "note"}
