# Recent baseline selection — 2026-07-16

## Selection rule

The resubmission is being prepared in July 2026. Recency is therefore the first
ranking key: formally accepted 2026/2025 papers, then task compatibility,
official runnable code, and only then citations/community uptake. Citation count
alone would systematically penalize the newest accepted work.

## Selected baselines

### TimeEmb — primary recent baseline

- Paper: *TimeEmb: A Lightweight Static-Dynamic Disentanglement Framework for
  Time Series Forecasting*.
- Venue: NeurIPS 2025 Main Conference Track.
- Official paper: <https://proceedings.neurips.cc/paper_files/paper/2025/hash/6e79ae23fe8a8bb15a2b2972053f4fc3-Abstract-Conference.html>.
- Official code: <https://github.com/showmeon/TimeEmb>.
- Why it belongs: explicitly targets temporal non-stationarity, separates
  time-invariant/time-varying components, and uses frequency-domain filtering.
  It is both recent and methodologically close enough to challenge TIFO's core
  empirical claim.
- Integration role: model-level recent baseline under the same dataset split,
  lengths, horizons and seeds; do not present it as a drop-in normalization.

### TFPS — second recent baseline

- Paper: *Learning Pattern-Specific Experts for Time Series Forecasting Under
  Patch-level Distribution Shift*.
- Venue: NeurIPS 2025 Main Conference Track.
- Official paper: <https://proceedings.neurips.cc/paper_files/paper/2025/file/8491a7fcc218946b471b600a915c8b02-Paper-Conference.pdf>.
- Official code: <https://github.com/syrGitHub/TFPS>.
- Why it belongs: explicitly studies patch-level distribution shift and combines
  time/frequency encoders with pattern-specific experts. It provides a modern
  distribution-shift-aware model rather than another older normalization layer.
- Integration role: model-level recent baseline under the same task protocol.

## Backups, not primary new baselines

| Method | Venue | Decision |
|---|---|---|
| PIR | NeurIPS 2025 | Keep pinned as a backup. It addresses instance-level failures and distribution shifts, but its post-hoc retrieval/revision stage makes the compute and information budget less directly comparable. |
| DDN | NeurIPS 2024 | Keep as a direct normalization backup. It is highly relevant but one year older than the selected methods. |
| FAN | NeurIPS 2024 | Already present in the manuscript; retain and rerun fairly rather than count it as a newly added baseline. |
| OnlineTSF/PROCEED | KDD 2025 | Exclude from the offline main table because it assumes online adaptation under concept drift. It can be cited or used in a separate online experiment only. |
| Fremen | ICLR 2026 submission | Exclude: OpenReview marks it withdrawn, so it is not a formally accepted conference baseline. |

## 2026 venue check

No suitable formally accepted, public, code-available KDD 2026 offline
non-stationary forecasting method was verified at this snapshot. KDD 2026 takes
place in August 2026 and the public research-paper surface is not yet suitable
for a reproducible baseline decision. ICLR 2026 search results contained related
forecasting papers, but no candidate was verified as both more directly matched
than TimeEmb/TFPS and accompanied by a suitable official implementation.

Re-run this search immediately before the experimental matrix is frozen; a 2026
accepted public codebase should supersede the 2025 candidate if it passes the
same compatibility gate.
