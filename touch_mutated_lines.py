import os
import json
from collections import defaultdict

# CHANGE THIS: Path where the cloned/checked-out buggy project lives
PROJECT_ROOT = "/tmp/bug-project"

def full_path(path):
    return os.path.join(PROJECT_ROOT, path)

with open("mutmut_report.rdjson", "r", encoding="utf-8") as f:
    data = json.load(f)

edits = defaultdict(set)

for diag in data.get("diagnostics", []):
    path = diag["location"]["path"]
    line = diag["location"]["range"]["start"]["line"]
    edits[path].add(line)

for rel_path, lines_to_touch in edits.items():
    abs_path = full_path(rel_path)

    if not os.path.exists(abs_path):
        print(f"❌ File not found: {abs_path}")
        continue

    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num in sorted(lines_to_touch):
            idx = line_num - 1
            if 0 <= idx < len(lines):
                if "# 👀 Mutant tracked by Reviewdog" not in lines[idx]:
                    lines[idx] = lines[idx].rstrip("\n") + "  # 👀 Mutant tracked by Reviewdog\n"

        with open(abs_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Patched {abs_path} on line(s): {sorted(lines_to_touch)}")

    except Exception as e:
        print(f"❌ Error editing {abs_path}: {e}")
