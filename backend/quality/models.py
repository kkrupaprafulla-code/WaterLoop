from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RuleType(Enum):
    MAX = "max"
    MAX_STRICT = "max_strict"
    MIN = "min"
    MIN_STRICT = "min_strict"
    RANGE = "range"
    DESCRIPTIVE = "descriptive"
    AA = "aa"
    NIL = "nil"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class QualityMeasurement:
    parameter: str
    value: float | str
    unit: Optional[str] = None


@dataclass
class QualityRule:
    parameter: str
    rule_type: RuleType
    unit: Optional[str] = None
    maximum: Optional[float] = None
    minimum: Optional[float] = None
    expected: Optional[str] = None
