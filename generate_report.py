import json
import re
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
        mutant_name  = m.get("mutant_name", "unknown")
        why          = str(m.get("why", ""))
        fix          = str(m.get("fix", ""))
    
        # Extract line number from mutation_desc
        mutation_desc = m.get("mutation_desc", "")
        match = re.search(r"Line (\d+):", mutation_desc)
        line_number = int(match.group(1)) if match else 1  # fallback
    
        # Handle example_test
        example = m.get("example_test", "")
        if isinstance(example, dict):
            test_name = example.get("test_name", "")
            test_code = example.get("test_code", "")
            example_test = f"{test_name}:\n{test_code}"
        else:
            example_test = str(example)
    
        message = (
            f"[{mutant_name}] Survived mutant.\n"
            f"Why: {why}\n"
            f"Fix: {fix}\n"
            f"Test:\n```python\n{example_test}\n```"
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
            "source": {
                "name": "CAMILA"
            }
        })
    
    return {
        "diagnostics": diagnostics
    }

def main():
    collect_and_explain()
    records = load_records("mutants/survived_mutants_with_explanations.json")
    rdjson = to_rdjson(records)

    with open("mutmut_report.rdjson", "w", encoding="utf-8") as f:
        json.dump(rdjson, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
