"""
Data models for the broken access control scanner.
"""
from dataclasses import dataclass
from enum import Enum


class Severity(str, Enum):
    """Severity levels for access control vulnerabilities."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class VulnerabilityResult:
    """Result of an access control vulnerability analysis."""
    endpoint: str
    severity: Severity
    description: str
