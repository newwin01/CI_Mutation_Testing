import os
import json
import requests
import yaml
import re
from typing import Dict, Any, List

def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

class OlamaExplainer:
    def __init__(self, config_path: str = "config.yaml"):
        cfg = load_config(config_path)
        self.olama_url = cfg.get("olama_url", "http://localhost:11434/api/generate")
        self.model = cfg.get("olama_model", "codellama:7b-instruct")
        self.headers = {"Content-Type": "application/json"}
        self._cache: Dict[str, Dict[str, str]] = {}

    def explain(self, rec: Dict[str, Any]) -> Dict[str, str]:
        key = rec["mutant_name"]
        if key in self._cache:
            return self._cache[key]

        # Construct prompt
        mutation_desc = rec.get("mutation_desc", "")[:500]
        prompt = (
            "You are a mutation testing expert. Analyze the mutation and suggest how to detect it with a test.\n"
            "Reply ONLY in valid JSON format using these keys:\n"
            "- why: explain why this mutant survived\n"
            "- how to kill: describe what kind of test or code change would kill this mutant\n"
            "- example_test: write a complete pytest-style test function that would kill this mutant\n\n"
            f"Mutation description:\n{mutation_desc}\n"
            f"File: {rec['source_file']}\n"
        )
        
        tests = rec.get("tests", [])
        if tests:
            prompt += "Existing tests that touch this code path:\n"
            for t in tests[:2]:
                line = t.get("test_code", "").splitlines()[0][:100]
                prompt += f"- {t['test_name']}: {line}...\n"
        else:
            prompt += "No existing tests cover this code path.\n"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        print(f"[Explaining] {key}")
        try:
            resp = requests.post(self.olama_url, headers=self.headers, json=payload, timeout=300)
            resp.raise_for_status()
            raw = resp.json().get("response", "").strip()

            # Optional debug
            print(f"[Raw LLM Response]\n{raw[:300]}...\n")

            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                print(f"[Warning] Malformed JSON. Attempting to recover.")
                s, e = raw.find("{"), raw.rfind("}")
                if s != -1 and e != -1:
                    try:
                        obj = json.loads(raw[s:e+1])
                    except Exception:
                        obj = {}
                else:
                    obj = {}

            out = {
                "why": obj.get("why", "").strip(),
                "how to kill": obj.get("how to kill", "").strip(),
                "example_test": obj.get("example_test", "").strip()
            }

        except Exception as e:
            print(f"[Error] {key}: {e}")
            out = {"why": "", "how to kill": "", "example_test": ""}

        self._cache[key] = out
        return out

def main(
    input_path: str = "mutants/survived_mutants.json",
    output_path: str = "mutants/survived_mutants_with_explanations.json"
) -> None:
    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    with open(input_path, 'r', encoding='utf-8') as f:
        records: List[Dict[str, Any]] = json.load(f)

    expl = OlamaExplainer()
    for rec in records:
        fb = expl.explain(rec)
        rec.update(fb)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Wrote feedback to {output_path}")

if __name__ == "__main__":
    main()
