import json
import re
from explainer import main as explain_main
import os


def collect_and_explain():
    explain_main(
        input_path="mutants/survived_mutants.json",
        output_path="mutants/survived_mutants_with_explanations.json"
    )

def load_records(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Generate short human-readable mutation summary
def summarize_mutation(mutation_desc: str) -> str:
    lines = mutation_desc.splitlines()
    original_line = ""
    mutated_line = ""

    for line in lines:
        if line.startswith('-') and not line.startswith('---'):
            original_line = line[1:].strip()
        elif line.startswith('+') and not line.startswith('+++'):
            mutated_line = line[1:].strip()

    if original_line and mutated_line:
        return f"Changed `{original_line}` to `{mutated_line}`"
    return "Mutation applied to unknown line"

def to_rdjson(records):
    diagnostics = []

    for m in records:
        file_path    = m.get("source_file", "unknown")
        mutant_name  = m.get("mutant_name", "unknown")
        why          = str(m.get("why", "")).strip()
        how_to_kill  = str(m.get("how to kill", "")).strip()

        # Extract line number from mutation_desc
        mutation_desc = m.get("mutation_desc", "")
        match = re.search(r"Line (\d+):", mutation_desc)
        line_number = int(match.group(1)) if match else 1

        # Mutation summary
        mutation_summary = summarize_mutation(mutation_desc)

        # Handle example_test
        example = m.get("example_test", "")
        if isinstance(example, dict):
            test_name = example.get("test_name", "")
            test_code = example.get("test_code", "")
            example_test = f"{test_name}:\n{test_code}"
        else:
            # Decode escaped \n to actual newlines
            example_test = str(example).encode('utf-8').decode('unicode_escape')

        # Build message
        message = (
            f"[{mutant_name}] Survived mutant. {mutation_summary}\n"
            f"Why: {why}\n"
            f"How to kill: {how_to_kill}\n"
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

def write_issue_body(records, output_file="issue_body.md"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("### 🧬 LLM Mutant Feedback Summary\n")
        for row in records:
            file = row.get("source_file", "unknown")
            mutant = row.get("mutant_name", "unknown")
            why = row.get("why", "").replace('\n', ' ').strip()
            fix = row.get("how to kill", "").replace('\n', ' ').strip()
            example = row.get("example_test", "")
            example = str(example).encode('utf-8').decode('unicode_escape')

            f.write(f"\n---\n🔬 `{mutant}` in `{file}`\n")
            f.write(f"- **Why**: {why}\n")
            f.write(f"- **How to kill**: {fix}\n")
            f.write(f"- **Test Suggestion**:\n```python\n{example}\n```\n")

def main():
    collect_and_explain()
    records = load_records("mutants/survived_mutants_with_explanations.json")

    # Generate rdjson for reviewdog
    rdjson = to_rdjson(records)
    with open("mutmut_report.rdjson", "w", encoding='utf-8') as f:
        json.dump(rdjson, f, indent=2, ensure_ascii=False)

    # Generate markdown issue body
    write_issue_body(records)

if __name__ == "__main__":
    main()
