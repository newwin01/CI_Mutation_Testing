# CAMILLA: Commit-Aware Mutation testIng with LLM expLAnations

**CAMILLA** is a CI-integrated mutation testing framework that enhances traditional diff-based mutant detection by generating **LLM-powered explanations and test suggestions**. It uses GitHub Actions and Reviewdog to provide **inline pull request annotations** for surviving mutants.

---

## 🚀 Features

-  **Commit-aware mutant filtering**: Focuses only on newly changed or added code.
-  **Diff-based mutation testing** using `mutmut`.
-  **LLM feedback generation** with [Ollama](https://ollama.com/) and `codellama:7b-instruct`:
  - Explains why a mutant survived
  - Suggests how to kill it
  - Generates an example `pytest`-style test
-  **Inline pull request comments** via Reviewdog
-  **Reviewdog-compatible `.rdjson` report** for diagnostics
-  **LLM-generated test suggestions** for improving coverage
  
---

## 📦 Requirements

- Python <= 3.10, >=3.8
- `mutmut` (customized version in our repository). Refer to each README in the mutmut and mutmut_3.8 folders to get to know more.
- (Optional) Ollama installed
- (Optional) Self-hosted runner with GPU

---

## ⚙️ How to Run CAMILLA in Your Repository

1. **Create a new branch** from `main`: let's say new branch called 'test'
2. **Commit your target files (the code you want to test) to this branch.**
   → See the section below: "🛠️ How to Change Mutation Target Paths"
4. **Create a pull request from the new branch (e.g., test) to main.**
5. **Once the pull request is created, GitHub Actions will automatically trigger the CAMILLA pipeline.**
6. **In the pull request page, you will see inline annotations added by Reviewdog**:
Surviving mutant information
**🤖 LLM explanations:**
- why the mutant survived
- how to kill it
- a suggested pytest-style test to detect it
![image](https://github.com/user-attachments/assets/c0807e05-a7c1-4610-b141-924c034c9485)

---

## 🛠️ How to Change Mutation Target Paths

CAMILLA uses **mannual path** based on the specific buggy project being checked out by BugsInPy.  
To change the mutation target, you must **edit the source code in `run_bug_test.py`**:

1. **Set the Project and Bug ID** at the top of `run_bug_test.py`:
   ```python
   PROJECT = "PySnooper"  # Name of the BugsInPy project
   BUG_ID = 1             # Bug number to check out
   ```

2. **Update the mutation path** in the `setup.cfg` writing section:
   ```python
   with open("setup.cfg", "w") as f:
       f.write("[mutmut]\n")
       f.write("paths_to_mutate = pysnooper/\n")  # <--- Change this line to your target directory or file
       #so as you can see here, pysnooper should be located in root directory of test branch
       f.write("tests_dir = tests/\n\n")
       f.write("[tool:pytest]\n")
       f.write("testpaths = tests\n")
   ```
   - For example, if you want to target a specific file in Keras, change to:
     ```
     paths_to_mutate = keras/engine/base_layer.py
     ```
   - Or for an entire directory:
     ```
     paths_to_mutate = keras/
     ```
    
   
4. **(Optional) If the project uses a different structure** (e.g., files under `source/`), adjust the path accordingly:
   - Example:
     ```
     paths_to_mutate = source/keras/engine/base_layer.py
     ```
  Also please check .github/workflows/mutation_test.yml file and update necessarylines there. 
   
4. **Commit and push your changes** to `run_bug_test.py`, then open a pull request.  
   CAMILLA will automatically use the updated path for mutation testing in the next CI run.

---
## 💻 Running Ollama with Self-Hosted Runner (Optional)
If you want to run LLM models locally (faster and private):
**Requirements:**
- A machine with GPU and Linux/macOS
- Python 3.10+
- Installed Ollama

1. **Install Ollama**
   You can use any LLM model as you wish. In the Github CI pipeline we are using codellama:7b-instruct.
2. **Register GitHub Self-Hosted Runner**
- Go to your repo → Settings → Actions → Runners
- Click "New self-hosted runner"
- Follow setup instructions:
 <pre lang="markdown"> ```
  ./config.sh --url https://github.com/<user>/<repo> --token <token>
./run.sh
``` </pre>

**3.Modify workflow YAML in the .github workflow mutant-test.yaml:**
  <pre lang="markdown"> ``` runs-on: [self-hosted] ``` </pre>

**4.Ensure Ollama is running at http://localhost:11434 for `explainer.py` to use it.**
  
  **📖 For more help, refer to GitHub Docs**:
https://docs.github.com/en/actions/hosting-your-own-runners

