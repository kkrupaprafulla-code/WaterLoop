from .models import QualityRule, RuleType
TOILET_FLUSHING_RULES = [
    QualityRule(
        parameter="turbidity",
        rule_type=RuleType.MAX_STRICT,
        unit="NTU",
        maximum=2
    )
]