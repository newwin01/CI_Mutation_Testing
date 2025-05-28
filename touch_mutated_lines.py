import json
import os
import re
from collections import defaultdict

EXPLANATION_PATH = "mutants/survived_mutants_with_explanations.json"

# Group all lines to touch by file path
edits = defaultdict(set)

with open(EXPLANATION_PATH, "r", encoding="utf-8") as f:
    records = json.load(f)

for record in records:
    path = record.get("source_file")
    mutation_desc = record.get("mutation_desc", "")

    # Extract the correct line number from mutation_desc like "Line 13:"
    match = re.search(r"Line (\d+):", mutation_desc)
    line = int(match.group(1)) if match else 1  # fallback to line 1

    if path:
        edits[path].add(line)

# Apply line modifications
for file_path, lines_to_touch in edits.items():
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        continue

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num in sorted(lines_to_touch):
            idx = line_num - 1
            if 0 <= idx < len(lines):
                if "# 👀 Reviewdog anchor" not in lines[idx]:
                    lines[idx] = lines[idx].rstrip("\n") + "  # 👀 Reviewdog anchor\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Touched {file_path} on line(s): {sorted(lines_to_touch)}")

    except Exception as e:
        print(f"❌ Error editing {file_path}: {e}")
