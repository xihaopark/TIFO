#!/usr/bin/env bash
# Continue the verified main-table coverage only after the active PatchTST queue
# has completed without a failed or missing record.  This is intentionally a
# fail-closed scheduler: do not launch iTransformer coverage after partial data.
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
py="/mnt/data1/park/Time Series/Forecasting/TKDE/envs/fredformer-cu128/bin/python"
patch_matrix="$repo_root/project_management/experiments/system/coverage_patchtst_custom_all_horizons.json"
itr_matrix="$repo_root/project_management/experiments/system/coverage_itransformer_remaining_horizons.json"
records="$repo_root/experiment_records"

active_pid=${1:?usage: continue_after_patchtst_custom.sh RUNNER_PID}
while kill -0 "$active_pid" 2>/dev/null; do
  printf '%s waiting for PatchTST runner %s\n' "$(date -Is)" "$active_pid"
  sleep 60
done

"$py" - "$patch_matrix" "$records" <<'PY'
import json
import sys
from pathlib import Path

matrix = json.loads(Path(sys.argv[1]).read_text())
records = Path(sys.argv[2])
problems = []
for run in matrix["runs"]:
    run_id = run["run_id"]
    record_path = records / run_id / "launch.json"
    if not record_path.exists():
        problems.append(f"missing record: {run_id}")
        continue
    record = json.loads(record_path.read_text())
    if record.get("status") != "completed" or record.get("returncode") != 0:
        problems.append(f"unsuccessful record: {run_id} ({record.get('status')}, {record.get('returncode')})")
if problems:
    raise SystemExit("PatchTST coverage gate failed:\n" + "\n".join(problems))
print(f"PatchTST coverage gate passed: {len(matrix['runs'])} successful records")
PY

cd "$repo_root"
"$py" project_management/experiments/system/collect_results.py \
  --protocol kdd_resubmit_patchtst_custom_coverage_v1 \
  --name kdd_resubmit_patchtst_custom_all_horizons
"$py" project_management/experiments/system/run_matrix.py "$itr_matrix" \
  --execute --gpus 0,1,2,3,4,5,6,7 --max-parallel 8
