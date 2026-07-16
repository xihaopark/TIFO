# TIFO KDD resubmit control plane

This directory connects the immutable review record, the executable experiment
repository and the Overleaf manuscript. It is the operational source of truth
for the resubmission; the paper may only claim work that is traceable here to
inspectable evidence.

## Start here

1. Read `reviews/transcribed/openreview_decision_and_reviews_verbatim.md` for
   the original decision and all five reviews.
2. Use `reviews/analysis/comment_inventory.md` for atomic concern IDs and
   current readiness.
3. Use `experiments/paper_code_evidence_matrix.md` for manuscript-to-code
   compatibility and missing experiments.
4. Use `experiments/table1_provenance_audit.md` before retaining any headline
   number from the previous manuscript.
5. Use `evidence_ledger.md` for concern → action → experiment → paper → evidence
   promotion state.
6. Use `baselines/THIRD_PARTY_SOURCES.md` for pinned upstream code.
7. Use `experiments/system/README.md` and its canonical JSON matrix for all new runs.
8. Follow the paper-side agent skill at
   `/home/park/TS/FredNormer_overleaf/.codex/skills/kdd27-tifo-resubmit/SKILL.md`.

## Source-of-truth chain

```text
official review / KDD rules
        ↓
atomic concern inventory
        ↓
frozen experiment protocol + run manifest
        ↓
raw metrics / logs / checkpoints
        ↓
mechanical aggregation and evidence ledger
        ↓
paper table / figure / claim
        ↓
one-page Summary of Changes
```

No downstream item may silently override an upstream source. A paper table is
not a result database, and a result directory name is not a complete config.

## Current state

| Layer | State | Main blocker |
|---|---|---|
| official reviews | verified transcription | OpenReview live text should still be compared if an export becomes available |
| reviewer triage | complete initial split | readiness must be updated as evidence arrives |
| historical result inventory | audited | most cells are single-run and Table 1 provenance does not match |
| protocol | representative gate frozen | full-table split and input-length contradictions remain |
| baseline sources | pinned, patched and smoke-tested | expand only after the representative gate is frozen |
| matched Ori/TIFO experiments | iTransformer H96 complete on all seven datasets, three seeds | PatchTST and additional horizons still required |
| recent baselines | TimeEmb and TFPS three-seed gate complete | broader dataset/horizon coverage remains |
| manuscript | highlighted draft with gaps | placeholders, unsupported claims and internal red markup |
| submission | not ready | scientific and formatting gates remain open |

Overall readiness: `itransformer_h96_coverage_complete; patchtst_and_horizon_coverage_open`.

## Operating rules

- Preserve `reviews/original/KDD2027resubmit.pdf` unchanged.
- Separate historical claims from verified regenerated evidence.
- Use stable comment IDs (`PC.1`, `R1.1`, and so on) and concern routes
  (`TH-1`, `EX-1`, and so on) in run manifests and change logs.
- Keep every run, including failures and losses; classify it instead of
  deleting inconvenient evidence.
- Label tuned evidence and supporting-only evidence. Do not silently promote
  them into a standard main table.
- Report strong matched wins positively and mixed results with explicit
  caveats, following the Fuji TKDE evidence policy.
- Reuse TKDE numbers only after the compatibility gate passes; otherwise reuse
  only its experiment design, scripts and reporting structure.

## Read-only audits

```bash
python project_management/scripts/audit_result_inventory.py --format summary
python project_management/scripts/audit_result_inventory.py --format csv
bash project_management/baselines/bootstrap_baselines.sh
bash /home/park/TS/FredNormer_overleaf/.codex/skills/kdd27-tifo-resubmit/scripts/check_submission_tex.sh \
  /home/park/TS/FredNormer_overleaf/sample-sigconf.tex
```

The bootstrap command changes only ignored `third_party/` checkouts and pins
them to documented commits. It does not integrate or run a baseline.

## Stage gates

1. **Protocol gate:** resolve split, lengths, seeds, scaler, metrics and budget.
2. **Implementation gate:** one runner supports Ori/TIFO and baseline adapters
   without method-specific changes to the task.
3. **Representative gate:** the three-cell matched rerun plan in
   `experiments/paper_code_evidence_matrix.md` passes artifact checks.
4. **Coverage gate:** full required matrix and recent baselines are complete.
5. **Claim gate:** every central claim points to verified evidence and mixed
   findings are caveated.
6. **Paper gate:** tables/figures are generated, references resolve and the
   internal highlight layer is removed from the clean submission.
7. **KDD gate:** Summary of Changes, anonymity, page limits, forum linkage and
   Overleaf compilation are verified.
