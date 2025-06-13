import os
import subprocess
import yaml
import re

CONFIG_FILE = "mutation_config.yml"
WORK_DIR = os.getcwd()

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Command failed:\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}")
        raise RuntimeError(f"Command failed: {cmd}")
    return result.stdout.strip()

def extract_changed_lines_from_diff(path):
    diff_output = run_cmd(f"git diff HEAD~1 HEAD -- {path}")
    changed_lines = set()
    for line in diff_output.splitlines():
        match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
        if match:
            start = int(match.group(1))
            length = int(match.group(2) or 1)
            for i in range(start, start + length):
                changed_lines.add(i)
    return sorted(changed_lines)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"❌ Config file {CONFIG_FILE} not found.")
    with open(CONFIG_FILE) as f:
        cfg = yaml.safe_load(f)
    return cfg.get("target_paths", [])

def main():
    target_paths = load_config()
    if not target_paths:
        print("❌ No target paths found in config.")
        return

    os.environ["PYTHONPATH"] = os.getcwd()
    mutants_dir = os.path.join(os.getcwd(), "mutants")
    os.makedirs(mutants_dir, exist_ok=True)

    for path in target_paths:
        if not os.path.exists(path):
            print(f"⚠️ Path does not exist: {path}")
            continue

        print(f"🔍 Analyzing: {path}")
        changed_lines = extract_changed_lines_from_diff(path)
        if not changed_lines:
            print(f"⚠️ No changed lines in {path}. Skipping.")
            continue

        line_str = ",".join(map(str, changed_lines))
        top_folder = path.split("/")[0]
        test_dir = "tests"  # Assumes tests are in ./tests/

        print(f"🧪 Mutating: {path} @ lines {line_str}")

        # Write setup.cfg
        with open("setup.cfg", "w") as f:
            f.write("[mutmut]\n")
            f.write(f"paths_to_mutate = {path}\n")
            f.write(f"tests_dir = {test_dir}\n\n")
            f.write("[tool:pytest]\n")
            f.write(f"testpaths = {test_dir}\n")

        run_cmd(f"python -m mutmut run --paths_to_mutate {path} --lines {line_str}")

    # Check for survivors
    survived_path = os.path.join(mutants_dir, "survived_mutants.json")
    if os.path.exists(survived_path):
        print(f"📤 Mutation testing completed. Survivors: {survived_path}")
    else:
        print("⚠️ No survived_mutants.json found after mutation testing.")

if __name__ == "__main__":
    main()
