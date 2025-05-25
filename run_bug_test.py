import subprocess
import os
import re

# === CONFIGURATION ===
PROJECT = "keras"
BUG_ID = 1
BUGS_REPO_PATH = "BugsInPy"
WORK_DIR = "/tmp/bug-project"  # GitHub runner has access to this temp dir

BUGSINPY_BIN = f"{BUGS_REPO_PATH}/framework/bin"

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed:\n{result.stderr}")
        exit(1)
    return result.stdout.strip()

def extract_changed_lines_from_diff(diff_output):
    changed_lines = set()
    for line in diff_output.splitlines():
        match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if match:
            start = int(match.group(1))
            length = int(match.group(2) or 1)
            for i in range(start, start + length):
                changed_lines.add(i)
    return sorted(changed_lines)

def find_source_path(base_dir):
    for root, dirs, files in os.walk(base_dir):
        if ".git" in dirs and "setup.py" in files:
            return root
    return None

def main():
    os.environ["PATH"] += f":{os.path.abspath(BUGSINPY_BIN)}"

    print("📦 Checking out buggy version of keras...")
    run_cmd(f"bugsinpy-checkout -p {PROJECT} -v 0 -i {BUG_ID} -w {WORK_DIR}")

    print("📂 Directory structure after checkout:")
    print(run_cmd(f"find {WORK_DIR}"))

    source_path = find_source_path(WORK_DIR)
    if not source_path:
        print("❌ Could not find source folder after checkout.")
        exit(1)

    os.chdir(source_path)
    print(f"📂 Changed to source path: {source_path}")

    print("🔍 Getting diff...")
    diff_output = run_cmd("git diff HEAD HEAD~1")
    changed_lines = extract_changed_lines_from_diff(diff_output)
    print(f"📌 Changed lines: {changed_lines}")
    if not changed_lines:
        print("❌ No changed lines found. Skipping mutation.")
        return

    line_str = ",".join(map(str, changed_lines))

    print("🧪 Running mutmut...")
    run_cmd(f"python -m mutmut run --paths-to-mutate . --lines {line_str}")

    print("📤 Mutation testing completed. Check `mutants/survived_mutants.json` for survivors.")

if __name__ == "__main__":
    main()
