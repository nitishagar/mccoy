"""Stable data contracts shared by scanning, reporting, and fixing."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AdvisoryNote(BaseModel):
    severity: Severity | None = None
    confidence: float = 0.0
    message: str


class Finding(BaseModel):
    rule_id: str
    tool: str
    severity: Severity
    message: str
    fix_hint: str
    location: str = "tool definition"
    advisory: AdvisoryNote | None = None
    fix_attempted: bool = False
    resolved: bool = False


class ScanResult(BaseModel):
    findings: list[Finding] = Field(default_factory=list)
    tools_scanned: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not self.findings

    @property
    def score(self) -> int:
        weights = {Severity.CRITICAL: 25, Severity.HIGH: 15, Severity.MEDIUM: 8, Severity.LOW: 3}
        return max(0, 100 - sum(weights.get(item.severity, 0) for item in self.findings))
