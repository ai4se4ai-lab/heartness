import json
import shutil
from pathlib import Path

totals = json.loads(Path("build/coverage.json").read_text())["totals"]
assert totals["percent_statements_covered"] >= 90, totals
assert totals["percent_branches_covered"] >= 90, totals
Path("results/validation").mkdir(parents=True, exist_ok=True)
shutil.copyfile("build/coverage.json", "results/validation/coverage.json")
print("Statement and branch coverage both meet 90%.")
