# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Constraint Engine - Policy and Safety Enforcement

Enforces system policies, safety constraints, and ethical guidelines
on agent responses before they are returned to users.
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of constraint violations"""

    SAFETY = "safety"
    PRIVACY = "privacy"
    SECURITY = "security"
    ETHICAL = "ethical"
    OPERATIONAL = "operational"


class ViolationSeverity(Enum):
    """Severity levels for violations"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Violation:
    """Represents a constraint violation"""

    type: ViolationType
    severity: ViolationSeverity
    description: str
    rule_id: str
    content_snippet: str


@dataclass
class ConstraintResult:
    """Result of constraint enforcement"""

    content: str
    modified: bool
    violations: list[Violation]
    applied_constraints: list[str]
    metadata: dict[str, Any]


class ConstraintEngine:
    """
    Enforces system constraints and policies on agent responses.

    The constraint engine acts as a final safety layer, ensuring all
    responses comply with system policies and ethical guidelines.
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._load_constraint_rules()
        self.violation_history = []

    def _load_constraint_rules(self):
        """Load constraint rules and patterns"""

        # Safety constraints
        self.safety_rules = {
            "no_harmful_instructions": {
                "patterns": [
                    r"\b(how to (make|create|build).*(bomb|explosive|weapon))\b",
                    r"\b(illegal|unlawful|criminal) (activities|actions|methods)\b",
                    r"\b(self.?harm|suicide|hurt yourself)\b",
                ],
                "severity": ViolationSeverity.CRITICAL,
                "action": "block",
            },
            "no_personal_attacks": {
                "patterns": [
                    r"\b(you are (stupid|idiot|moron|dumb))\b",
                    r"\b(hate|despise|loathe) (you|users|humans)\b",
                ],
                "severity": ViolationSeverity.HIGH,
                "action": "modify",
            },
        }

        # Privacy constraints
        self.privacy_rules = {
            "no_personal_info_exposure": {
                "patterns": [
                    r"\b\d{3}-\d{2}-\d{4}\b",  # SSN pattern
                    r"\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b",  # Credit card pattern
                    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email pattern
                ],
                "severity": ViolationSeverity.HIGH,
                "action": "redact",
            }
        }

        # Security constraints
        self.security_rules = {
            "no_credential_exposure": {
                "patterns": [
                    r"\b(password|pwd|pass)\s*[:=]\s*\S+",
                    r"\b(api[_-]?key|token)\s*[:=]\s*\S+",
                    r"\b(secret|private[_-]?key)\s*[:=]\s*\S+",
                ],
                "severity": ViolationSeverity.CRITICAL,
                "action": "redact",
            },
            "no_system_exploitation": {
                "patterns": [
                    r"\b(exec|eval|system|shell)\s*\(",
                    r"\b(rm\s+-rf|del\s+/[sf])\b",
                    r"\b(sudo|admin|root)\s+(access|login|password)\b",
                ],
                "severity": ViolationSeverity.HIGH,
                "action": "block",
            },
        }

        # Ethical constraints
        self.ethical_rules = {
            "no_discrimination": {
                "patterns": [
                    r"\b(inferior|superior|better|worse)\s+(race|gender|religion)\b",
                    r"\b(all|most)\s+(women|men|[race terms])\s+are\b",
                ],
                "severity": ViolationSeverity.HIGH,
                "action": "modify",
            },
            "no_deception": {
                "patterns": [
                    r"\b(i am (human|person|real user))\b",
                    r"\b(pretend|act like|roleplay as)\s+(human|person)\b",
                ],
                "severity": ViolationSeverity.MEDIUM,
                "action": "modify",
            },
        }

        # Operational constraints
        self.operational_rules = {
            "response_length_limit": {
                "max_length": self.config.get("max_response_length", 5000),
                "severity": ViolationSeverity.LOW,
                "action": "truncate",
            },
            "no_infinite_loops": {
                "patterns": [r"\b(while\s+true|for\s+\(\s*;\s*;\s*\))\b"],
                "severity": ViolationSeverity.MEDIUM,
                "action": "modify",
            },
        }

    def apply_constraints(self, content: str, constraint_types: list[str]) -> ConstraintResult:
        """
        Apply specified constraints to content.

        Args:
            content: The content to check and potentially modify
            constraint_types: List of constraint types to apply

        Returns:
            ConstraintResult with validated/modified content
        """
        original_content = content
        modified_content = content
        violations = []
        applied_constraints = []

        for constraint_type in constraint_types:
            if constraint_type == "basic_safety":
                result = self._apply_safety_constraints(modified_content)
                modified_content = result.content
                violations.extend(result.violations)
                applied_constraints.append("basic_safety")

            elif constraint_type == "security_review":
                result = self._apply_security_constraints(modified_content)
                modified_content = result.content
                violations.extend(result.violations)
                applied_constraints.append("security_review")

            elif constraint_type == "privacy_protection":
                result = self._apply_privacy_constraints(modified_content)
                modified_content = result.content
                violations.extend(result.violations)
                applied_constraints.append("privacy_protection")

            elif constraint_type == "code_safety":
                result = self._apply_code_safety_constraints(modified_content)
                modified_content = result.content
                violations.extend(result.violations)
                applied_constraints.append("code_safety")

        # Record violations for monitoring
        self.violation_history.extend(violations)

        return ConstraintResult(
            content=modified_content,
            modified=(modified_content != original_content),
            violations=violations,
            applied_constraints=applied_constraints,
            metadata={
                "original_length": len(original_content),
                "final_length": len(modified_content),
            },
        )

    def _apply_safety_constraints(self, content: str) -> ConstraintResult:
        """Apply basic safety constraints"""
        violations = []
        modified_content = content

        # Check safety rules
        for rule_id, rule in self.safety_rules.items():
            for pattern in rule["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    violation = Violation(
                        type=ViolationType.SAFETY,
                        severity=rule["severity"],
                        description=f"Safety violation: {rule_id}",
                        rule_id=rule_id,
                        content_snippet=match.group(0),
                    )
                    violations.append(violation)

                    # Apply action
                    if rule["action"] == "block":
                        modified_content = (
                            "I cannot provide information that could be harmful or dangerous."
                        )
                    elif rule["action"] == "modify":
                        modified_content = re.sub(
                            pattern, "[CONTENT_FILTERED]", modified_content, flags=re.IGNORECASE
                        )

        return ConstraintResult(
            content=modified_content,
            modified=(modified_content != content),
            violations=violations,
            applied_constraints=["safety"],
            metadata={},
        )

    def _apply_security_constraints(self, content: str) -> ConstraintResult:
        """Apply security constraints"""
        violations = []
        modified_content = content

        # Check security rules
        for rule_id, rule in self.security_rules.items():
            for pattern in rule["patterns"]:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    violation = Violation(
                        type=ViolationType.SECURITY,
                        severity=rule["severity"],
                        description=f"Security violation: {rule_id}",
                        rule_id=rule_id,
                        content_snippet=match.group(0),
                    )
                    violations.append(violation)

                    # Apply action
                    if rule["action"] == "block":
                        modified_content = (
                            "I cannot provide information that could compromise security."
                        )
                    elif rule["action"] == "redact":
                        modified_content = re.sub(
                            pattern, "[REDACTED]", modified_content, flags=re.IGNORECASE
                        )

        return ConstraintResult(
            content=modified_content,
            modified=(modified_content != content),
            violations=violations,
            applied_constraints=["security"],
            metadata={},
        )

    def _apply_privacy_constraints(self, content: str) -> ConstraintResult:
        """Apply privacy constraints"""
        violations = []
        modified_content = content

        # Check privacy rules
        for rule_id, rule in self.privacy_rules.items():
            for pattern in rule["patterns"]:
                matches = list(re.finditer(pattern, content))

                for match in matches:
                    violation = Violation(
                        type=ViolationType.PRIVACY,
                        severity=rule["severity"],
                        description=f"Privacy violation: {rule_id}",
                        rule_id=rule_id,
                        content_snippet=match.group(0)[:20] + "...",
                    )
                    violations.append(violation)

                    # Apply action
                    if rule["action"] == "redact":
                        modified_content = re.sub(
                            pattern, "[PERSONAL_INFO_REDACTED]", modified_content
                        )

        return ConstraintResult(
            content=modified_content,
            modified=(modified_content != content),
            violations=violations,
            applied_constraints=["privacy"],
            metadata={},
        )

    def _apply_code_safety_constraints(self, content: str) -> ConstraintResult:
        """Apply code safety constraints"""
        violations = []
        modified_content = content

        # Check for dangerous code patterns
        dangerous_patterns = [
            (r"\bos\.system\([^)]+\)", "Potentially dangerous system call"),
            (r"\beval\([^)]+\)", "Use of eval() can be dangerous"),
            (r"\bexec\([^)]+\)", "Use of exec() can be dangerous"),
            (r"\b__import__\([^)]+\)", "Dynamic imports can be risky"),
        ]

        for pattern, description in dangerous_patterns:
            matches = list(re.finditer(pattern, content))

            for match in matches:
                violation = Violation(
                    type=ViolationType.SECURITY,
                    severity=ViolationSeverity.MEDIUM,
                    description=description,
                    rule_id="code_safety",
                    content_snippet=match.group(0),
                )
                violations.append(violation)

                # Add warning comment
                warning = f"\n# WARNING: {description}\n"
                modified_content = modified_content.replace(
                    match.group(0), warning + match.group(0)
                )

        return ConstraintResult(
            content=modified_content,
            modified=(modified_content != content),
            violations=violations,
            applied_constraints=["code_safety"],
            metadata={},
        )

    def add_custom_rule(self, category: str, rule_id: str, rule_config: dict[str, Any]):
        """Add a custom constraint rule"""
        if category == "safety":
            self.safety_rules[rule_id] = rule_config
        elif category == "security":
            self.security_rules[rule_id] = rule_config
        elif category == "privacy":
            self.privacy_rules[rule_id] = rule_config
        elif category == "ethical":
            self.ethical_rules[rule_id] = rule_config

        logger.info(f"Added custom {category} rule: {rule_id}")

    def get_violation_stats(self) -> dict[str, Any]:
        """Get statistics about violations"""
        if not self.violation_history:
            return {"total_violations": 0}

        by_type = {}
        by_severity = {}

        for violation in self.violation_history:
            # Count by type
            type_key = violation.type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by severity
            severity_key = violation.severity.value
            by_severity[severity_key] = by_severity.get(severity_key, 0) + 1

        return {
            "total_violations": len(self.violation_history),
            "by_type": by_type,
            "by_severity": by_severity,
            "recent_violations": [
                {
                    "type": v.type.value,
                    "severity": v.severity.value,
                    "description": v.description,
                    "rule_id": v.rule_id,
                }
                for v in self.violation_history[-10:]  # Last 10 violations
            ],
        }

    def clear_violation_history(self):
        """Clear violation history (for privacy)"""
        self.violation_history.clear()
        logger.info("Violation history cleared")
