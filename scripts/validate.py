"""Run lint, typing and tests with coverage; write results/validation/{tests,coverage}.json."""
import json
import re
import subprocess
import sys
from pathlib import Path

out = Path("results/validation")
out.mkdir(parents=True, exist_ok=True)
ruff = subprocess.run([".venv/bin/ruff", "check", "src", "benchmark", "experiments", "scripts", "tests"],
                      capture_output=True, text=True)
mypy = subprocess.run([".venv/bin/mypy"], capture_output=True, text=True)
test = subprocess.run([sys.executable, "-m", "pytest", "-q", "--cov=heartness", "--cov-branch",
                       f"--cov-report=json:{out / 'coverage.json'}"], capture_output=True, text=True)
passed = int(re.search(r"(\d+) passed", test.stdout).group(1))
failed = re.search(r"(\d+) failed", test.stdout)
(out / "tests.json").write_text(json.dumps({
    "passed": passed, "failed": int(failed.group(1)) if failed else 0,
    "ruff_ok": ruff.returncode == 0, "mypy_ok": mypy.returncode == 0,
    "pytest_tail": test.stdout[-600:]}, indent=1) + "\n")
print(passed, "passed; ruff", ruff.returncode, "mypy", mypy.returncode)
