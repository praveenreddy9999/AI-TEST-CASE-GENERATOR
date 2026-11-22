import pandas as pd

EXPORT_COLUMNS = [
    "test_case_id", "scenario_type", "title", "preconditions",
    "steps", "test_data", "expected_result", "priority", "assumptions"
]

def cases_to_dataframe(test_cases):
    rows = []
    for case in test_cases:
        row = {key: case.get(key, "") for key in EXPORT_COLUMNS}
        steps = row.get("steps", [])
        row["steps"] = "\n".join(str(x) for x in steps) if isinstance(steps, list) else str(steps)
        rows.append(row)
    return pd.DataFrame(rows, columns=EXPORT_COLUMNS)

def to_csv_bytes(test_cases):
    return cases_to_dataframe(test_cases).to_csv(index=False).encode("utf-8-sig")
