"""Validation and normalization for generated test cases."""
import re

ALLOWED_SCENARIOS = {"Positive", "Negative", "Edge case"}
ALLOWED_PRIORITIES = {"High", "Medium", "Low"}
REQUIRED_FIELDS = ["title", "scenario_type", "preconditions", "steps", "test_data", "expected_result", "priority"]

def validate_generation(data, requested_count=8):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    summary = str(data.get("feature_summary", "")).strip()
    raw_cases = data.get("test_cases")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("No test_cases list was returned.")
    cases, seen = [], set()
    for idx, raw in enumerate(raw_cases[:requested_count], start=1):
        if not isinstance(raw, dict):
            continue
        missing = [field for field in REQUIRED_FIELDS if field not in raw]
        if missing:
            continue
        title = str(raw["title"]).strip()
        scenario = str(raw["scenario_type"]).strip().title()
        priority = str(raw["priority"]).strip().title()
        steps = raw["steps"]
        if isinstance(steps, str):
            steps = [s.strip() for s in steps.splitlines() if s.strip()]
        if not isinstance(steps, list):
            continue
        steps = [str(s).strip() for s in steps if str(s).strip()]
        expected = str(raw["expected_result"]).strip()
        test_data = str(raw["test_data"]).strip()
        preconditions = str(raw["preconditions"]).strip()
        if not title or not steps or not expected or not test_data:
            continue
        if scenario not in ALLOWED_SCENARIOS or priority not in ALLOWED_PRIORITIES:
            continue
        signature = title.lower()
        if signature in seen:
            continue
        seen.add(signature)
        cases.append({
            "test_case_id": f"TC-{len(cases)+1:03d}",
            "title": title,
            "scenario_type": scenario,
            "preconditions": preconditions,
            "steps": steps,
            "test_data": test_data,
            "expected_result": expected,
            "priority": priority,
            "assumptions": str(raw.get("assumptions", "")).strip()
        })
    if not cases:
        raise ValueError("No valid, non-duplicate test cases with all required fields.")
    assumptions = data.get("assumptions", [])
    if not isinstance(assumptions, list):
        assumptions = [str(assumptions)] if assumptions else []
    return {
        "feature_summary": summary or "Summary not provided by the model.",
        "assumptions": [str(x).strip() for x in assumptions if str(x).strip()],
        "test_cases": cases
    }
