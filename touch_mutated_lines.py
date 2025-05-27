import json
from collections import defaultdict

# Load survived mutants
with open("mutmut_report.rdjson", "r", encoding="utf-8") as f:
    data = json.load(f)

# Track all edits to avoid duplicate changes
edits = defaultdict(set)

for diag in data.get("diagnostics", []):
    path = diag["location"]["path"]
    line = diag["location"]["range"]["start"]["line"]

    edits[path].add(line)

# Edit each file at the specified lines
for path, lines_to_touch in edits.items():
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num in sorted(lines_to_touch):
            idx = line_num - 1
            if 0 <= idx < len(lines):
                if "# 👀 Mutant tracked by Reviewdog" not in lines[idx]:
                    lines[idx] = lines[idx].rstrip("\n") + "  # 👀 Mutant tracked by Reviewdog\n"

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        print(f"✅ Touched {path} on line(s): {sorted(lines_to_touch)}")

    except FileNotFoundError:
        print(f"❌ File not found: {path}")
    except Exception as e:
        print(f"❌ Error editing {path}: {e}")
