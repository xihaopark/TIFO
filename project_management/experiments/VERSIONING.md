# TIFO KDD resubmit version policy

## Official lines

- `main`: last verified historical-TIFO evidence base; do not run candidate
  operators here.
- `codex/kdd27-resubmit-baselines`: active resubmit experiment integration.
- `codex/yamabuki-candidates`: server-25 alpha/zero-padding candidates; these
  are excluded from official paper evidence unless explicitly promoted later.

The paper-facing method name is **TIFO**. Historical Fredformer/FredNormer
identifiers may remain inside legacy paths only to avoid a risky pre-deadline
refactor.

## Evidence freeze

Every launched run must record the orchestration repository state, the native
or third-party engine state, exact task parameters, dataset hash, seed, command,
log and final metric. External baselines may use a documented dirty upstream
tree only when the tracked diff hash and status are captured in `launch.json`.

Tag `kdd27-resubmit-exp-v1` only after the minimal baseline matrix and table
generators pass. The tag identifies the exact code used for all promoted paper
numbers; later candidate work must use a new tag.
