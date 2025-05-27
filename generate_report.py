import json
from explainer import main as explain_main

def collect_and_explain():
    explain_main(
        input_path="mutants/survived_mutants.json",
        output_path="mutants/survived_mutants_with_explanations.json"
    )

def load_records(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def to_rdjson(records):
    diagnostics = []

    for m in records:
        file_path    = m.get("source_file", "unknown")
        line_number  = m.get("line", 1)
        mutant_name  = m.get("mutant_name", "unknown")
        why          = str(m.get("why", "")).replace("\n", " ")
        fix          = str(m.get("fix", "")).replace("\n", " ")

        # Handle example_test being a dict or string
        example = m.get("example_test", "")
        if isinstance(example, dict):
            test_name = example.get("test_name", "")
            test_code = example.get("test_code", "").replace("\n", " ")
            example_test = f"{test_name}: {test_code}"
        else:
            example_test = str(example).replace("\n", " ")

        message = (
            f"[{mutant_name}] Survived mutant. "
            f"Why: {why} | Fix: {fix} | Test: {example_test}"
        )

        diagnostics.append({
            "message": message,
            "location": {
                "path": file_path,
                "range": {
                    "start": { "line": line_number, "column": 1 },
                    "end":   { "line": line_number, "column": 1 }
                }
            },
            "severity": "WARNING",
            "code": {
                "value": "survived-mutant"
            },
            "source": "mutmut-ai"
        })

    return {
    "diagnostics": diagnostics
}

def main():
    collect_and_explain()
    records = load_records("mutants/survived_mutants_with_explanations.json")
    rdjson = to_rdjson(records)

    with open("mutmut_report.rdjson", "w", encoding="utf-8") as f:
        json.dump(rdjson, f, indent=2)

if __name__ == "__main__":
    main()
