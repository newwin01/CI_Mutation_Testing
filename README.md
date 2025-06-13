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

- Python <= 3.10
- `mutmut` (customized version in our repository)
- (Optional) Ollama installed
- (Optional) Self-hosted runner with GPU

---

## ⚙️ How to Run CAMILLA in Your Repository

1. **Create a new branch** from `main`: let's say new branch called 'test'
2. **Commit your target files (the code you want to test) to this branch.**
3. **Create a pull request from the new branch (e.g., test) to main.**
4. **Once the pull request is created, GitHub Actions will automatically trigger the CAMILLA pipeline.**
5. **In the pull request page, you will see inline annotations added by Reviewdog**:
Surviving mutant information
**🤖 LLM explanations:**
- why the mutant survived
- how to kill it
- a suggested pytest-style test to detect it
![image](https://github.com/user-attachments/assets/c0807e05-a7c1-4610-b141-924c034c9485)

---
##💻 Running Ollama with Self-Hosted Runner (Optional)
If you want to run LLM models locally (faster and private):
**Requirements:**
A machine with GPU and Linux/macOS
Python 3.10+
Installed Ollama

1. Install Ollama
   You can use any LLM model as you wish. In the Github CI pipeline we are using codellama:7b-instruct.
3. Register GitHub Self-Hosted Runner
- Go to your repo → Settings → Actions → Runners
- Click "New self-hosted runner"
- Follow setup instructions:
 <pre lang="markdown"> ```bash
  ./config.sh --url https://github.com/<user>/<repo> --token <token>
./run.sh
``` </pre>

3.Modify workflow YAML in the .github workflow mutant-test.yaml:
  <pre lang="markdown"> ```bash runs-on: [self-hosted] ``` </pre>
4.Ensure Ollama is running at http://localhost:11434 for explainer.py to use it.
  📖 For more help, refer to GitHub Docs:
https://docs.github.com/en/actions/hosting-your-own-runners

