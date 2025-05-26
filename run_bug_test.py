import subprocess
import os
import re

# === CONFIGURATION ===
PROJECT = "PySnooper"
BUG_ID = 1
BUGS_REPO_PATH = "BugsInPy"
WORK_DIR = "/tmp/bug-project"  # GitHub runner has access to this temp dir

BUGSINPY_BIN = f"{BUGS_REPO_PATH}/framework/bin"

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
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

    print(f"📦 Checking out buggy version of {PROJECT}...")
    run_cmd(f"bugsinpy-checkout -p {PROJECT} -v 0 -i {BUG_ID} -w {WORK_DIR}")

    print("📂 Directory structure after checkout:")
    print(run_cmd(f"find {WORK_DIR}"))

    print("📄 Python files under checkout:")
    print(run_cmd(f"find {WORK_DIR} -name '*.py'"))

    source_path = find_source_path(WORK_DIR)
    if not source_path:
        print("❌ Could not find source folder after checkout.")
        exit(1)

    os.chdir(source_path)
    print(f"📂 Changed to source path: {source_path}")
    
    # Fix Python 3.10 compatibility: Mapping moved to collections.abc
    variables_path = os.path.join("pysnooper", "variables.py")
    if os.path.exists(variables_path):
        with open(variables_path, "r") as f:
            content = f.read()
        fixed = content.replace("from collections import Mapping, Sequence",
                                "from collections.abc import Mapping, Sequence")
        with open(variables_path, "w") as f:
            f.write(fixed)
        print("✅ Patched variables.py for Python 3.10 compatibility.")


    print("🔍 Getting diff...")
    diff_output = run_cmd("git diff HEAD HEAD~1")
    changed_lines = extract_changed_lines_from_diff(diff_output)
    print(f"📌 Changed lines: {changed_lines}")
    if not changed_lines:
        print("❌ No changed lines found. Skipping mutation.")
        return

    line_str = ",".join(map(str, changed_lines))

    # Make sure we can import `pysnooper`
    os.environ["PYTHONPATH"] = os.getcwd()

    print("🧪 Running mutmut...")
    with open("setup.cfg", "w") as f:
        f.write("[mutmut]\n")
        f.write("paths_to_mutate = pysnooper/\n")
        f.write("tests_dir = tests/\n\n")
        f.write("[tool:pytest]\n")
        f.write("testpaths = tests\n")

    run_cmd("python -m mutmut run")

    print("📤 Mutation testing completed. Check `mutants/survived_mutants.json` for survivors.")

if __name__ == "__main__":
    main()
