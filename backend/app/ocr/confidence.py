from typing import Any, Dict, List


CRITICAL_FIELDS = {"survey_number", "area", "coordinates", "village", "taluk"}


def classify_confidence_tier(confidence: float) -> str:
    """
    Classifies field confidence into HIGH, MEDIUM, LOW tiers (Section 20).
    >= 0.90 -> HIGH
    0.70 - 0.89 -> MEDIUM
    < 0.70 -> LOW
    """
    if confidence >= 0.90:
        return "HIGH"
    elif confidence >= 0.70:
        return "MEDIUM"
    else:
        return "LOW"


def evaluate_confidence(fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluates field-level and document-level confidence and triggers Human Review when needed (Section 20 & 21).
    """
    confidences = []
    field_assessments = {}
    review_required = False
    review_reasons = []

    for name, data in fields.items():
        if isinstance(data, dict) and "confidence" in data:
            conf = float(data.get("confidence", 0.0))
            confidences.append(conf)
            tier = classify_confidence_tier(conf)
            is_critical = name in CRITICAL_FIELDS

            field_assessments[name] = {
                "confidence": conf,
                "tier": tier,
                "is_critical": is_critical,
                "needs_review": conf < 0.70,
            }

            if conf < 0.70 and is_critical:
                review_required = True
                review_reasons.append(f"Low confidence ({round(conf*100)}%) on critical field '{name}'")

    overall_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0

    return {
        "overall_confidence": overall_confidence,
        "overall_tier": classify_confidence_tier(overall_confidence),
        "review_required": review_required,
        "review_reasons": review_reasons,
        "fields": field_assessments,
    }
