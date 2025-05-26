import subprocess
import json
from explainer import main as explain_main

# def run_mutmut():
#     """Run MutMut to generate & test mutants (writes mutants/survived_mutants.json)."""
#     subprocess.run(
#         ["python", "-m", "mutmut", "run", "--lines"],
#         check=True
#     )

def collect_and_explain():
    """Read survivors JSON, call Olama, write mutants/survived_mutants_with_explanations.json."""
    explain_main(
        input_path="mutants/survived_mutants.json",
        output_path="mutants/survived_mutants_with_explanations.json"
    )

def load_records(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # run_mutmut()
    collect_and_explain()
    records = load_records("mutants/survived_mutants_with_explanations.json")

    # Emit one warning annotation per surviving mutant
    for m in records:
        file_path    = m["source_file"]
        line_number  = m.get("line", 1)
        mutant_name  = m["mutant_name"]
        why          = m["why"].replace("\n", " ")
        fix          = m["fix"].replace("\n", " ")
        example_test = m["example_test"].replace("\n", " ")

        msg = (
            f"[AI Mutant Explainer] `{mutant_name}`\n"
            f"Why it survived: {why}\n"
            f"Fix: {fix}\n"
            f"Example: `{example_test}`"
        ).replace("\n", " | ")

        # This line creates an inline annotation at file_path:line_number
        print(f"::warning file={file_path},line={line_number}::{msg}")

if __name__ == "__main__":
    main()
