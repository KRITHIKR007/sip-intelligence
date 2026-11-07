"""
SIP Intelligence — Deterministic Validation Rule Engine
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.engineering import EngineeringEntity
from app.models.validation import (
    Severity,
    ValidationResult,
    ValidationRule,
    ValidationStatus,
)

logger = structlog.get_logger()


@dataclass
class ValidationFinding:
    """Result of a single rule evaluation."""
    rule_id: str
    rule_name: str
    status: str
    severity: str
    expected: Optional[str] = None
    observed: Optional[str] = None
    evidence: Optional[str] = None
    entity_id: Optional[str] = None


class RuleEngine:
    """
    Deterministic validation rule execution engine.

    CRITICAL: This engine does NOT use LLMs for validation.
    All rules are evaluated deterministically based on entity data
    and configured rule logic.

    Rules must be explicitly provided by engineers or sourced from
    approved standards. The engine never invents rules.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_validation(
        self,
        document_id: uuid.UUID,
        rule_ids: Optional[list[uuid.UUID]] = None,
    ) -> list[ValidationFinding]:
        """Run configured validation rules against a document's entities."""
        # Get applicable rules
        rule_query = select(ValidationRule).where(ValidationRule.is_active == True)
        if rule_ids:
            rule_query = rule_query.where(ValidationRule.id.in_(rule_ids))
        rules = (await self.db.execute(rule_query)).scalars().all()

        if not rules:
            return [ValidationFinding(
                rule_id="",
                rule_name="No rules configured",
                status=ValidationStatus.NOT_APPLICABLE.value,
                severity=Severity.INFO.value,
                evidence="No validation rules are currently configured. "
                         "Rules must be provided by engineers based on approved standards.",
            )]

        # Get document entities
        entities = (await self.db.execute(
            select(EngineeringEntity).where(EngineeringEntity.document_id == document_id)
        )).scalars().all()

        findings = []
        for rule in rules:
            finding = await self._evaluate_rule(rule, entities)
            findings.append(finding)

            # Store result
            result = ValidationResult(
                rule_id=rule.id,
                document_id=document_id,
                status=finding.status,
                expected_value=finding.expected,
                observed_value=finding.observed,
                evidence=finding.evidence,
                entity_id=uuid.UUID(finding.entity_id) if finding.entity_id else None,
            )
            self.db.add(result)

        await self.db.flush()
        return findings

    async def _evaluate_rule(
        self,
        rule: ValidationRule,
        entities: list[EngineeringEntity],
    ) -> ValidationFinding:
        """Evaluate a single rule against entities."""
        try:
            logic = rule.evaluation_logic.strip().lower()

            # Check preconditions
            applicable_types = rule.applicable_types or []
            relevant_entities = [
                e for e in entities
                if not applicable_types or e.entity_type in applicable_types
            ]

            if not relevant_entities:
                return ValidationFinding(
                    rule_id=str(rule.id),
                    rule_name=rule.name,
                    status=ValidationStatus.NOT_APPLICABLE.value,
                    severity=rule.severity.value,
                    evidence=f"No entities of applicable types found.",
                )

            # Built-in rule evaluators
            if logic == "check_entity_exists":
                return self._check_entity_exists(rule, relevant_entities)
            elif logic == "check_entity_has_label":
                return self._check_entity_has_label(rule, relevant_entities)
            elif logic == "check_entity_confidence":
                return self._check_entity_confidence(rule, relevant_entities)
            else:
                return ValidationFinding(
                    rule_id=str(rule.id),
                    rule_name=rule.name,
                    status=ValidationStatus.REVIEW_REQUIRED.value,
                    severity=rule.severity.value,
                    evidence=f"Rule logic '{logic}' requires manual evaluation.",
                )

        except Exception as e:
            return ValidationFinding(
                rule_id=str(rule.id),
                rule_name=rule.name,
                status=ValidationStatus.INSUFFICIENT_EVIDENCE.value,
                severity=rule.severity.value,
                evidence=f"Rule evaluation error: {e}",
            )

    def _check_entity_exists(self, rule, entities) -> ValidationFinding:
        """Check that required entity types exist."""
        required = rule.preconditions.get("required_types", []) if rule.preconditions else []
        found_types = {e.entity_type for e in entities}
        missing = [t for t in required if t not in found_types]

        if missing:
            return ValidationFinding(
                rule_id=str(rule.id),
                rule_name=rule.name,
                status=ValidationStatus.FAIL.value,
                severity=rule.severity.value,
                expected=f"Entity types: {required}",
                observed=f"Found: {list(found_types)}, Missing: {missing}",
                evidence=f"Drawing is missing required entity types: {missing}",
            )
        return ValidationFinding(
            rule_id=str(rule.id),
            rule_name=rule.name,
            status=ValidationStatus.PASS.value,
            severity=rule.severity.value,
            expected=f"Entity types: {required}",
            observed=f"All found: {list(found_types)}",
        )

    def _check_entity_has_label(self, rule, entities) -> ValidationFinding:
        """Check that all entities have labels."""
        unlabeled = [e for e in entities if not e.label]
        if unlabeled:
            return ValidationFinding(
                rule_id=str(rule.id),
                rule_name=rule.name,
                status=ValidationStatus.REVIEW_REQUIRED.value,
                severity=rule.severity.value,
                observed=f"{len(unlabeled)} entities missing labels",
                evidence=f"Entity types without labels: {[e.entity_type for e in unlabeled[:5]]}",
            )
        return ValidationFinding(
            rule_id=str(rule.id),
            rule_name=rule.name,
            status=ValidationStatus.PASS.value,
            severity=rule.severity.value,
            observed=f"All {len(entities)} entities have labels",
        )

    def _check_entity_confidence(self, rule, entities) -> ValidationFinding:
        """Check entity detection confidence thresholds."""
        threshold = (rule.preconditions or {}).get("min_confidence", 0.5)
        low_conf = [e for e in entities if e.confidence and e.confidence < threshold]

        if low_conf:
            return ValidationFinding(
                rule_id=str(rule.id),
                rule_name=rule.name,
                status=ValidationStatus.REVIEW_REQUIRED.value,
                severity=rule.severity.value,
                expected=f"Confidence ≥ {threshold}",
                observed=f"{len(low_conf)} entities below threshold",
                evidence=f"Low confidence entities: {[(e.entity_type, e.confidence) for e in low_conf[:5]]}",
            )
        return ValidationFinding(
            rule_id=str(rule.id),
            rule_name=rule.name,
            status=ValidationStatus.PASS.value,
            severity=rule.severity.value,
            observed=f"All entities above confidence threshold {threshold}",
        )

