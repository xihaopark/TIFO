---
name: kdd27-tifo-resubmit
description: "Manage the paper-specific KDD 2027 Research Track Cycle 1 resubmission of TIFO: Time-Invariant Frequency Operator for Stationarity-Aware Representation Learning in Time Series (OpenReview forum 2b776YkXBX). Use whenever an agent works on this paper's reviewer triage, manuscript revision, new experiments, Summary of Changes, rebuttal-derived claims, anonymous submission PDF, Overleaf synchronization, or KDD submission preflight in the FredNormer paper workspace."
---

# KDD 2027 TIFO resubmission

Treat this as an official **Resubmit**, not a rejected-paper fresh submission.

## Start here

1. Read [references/paper-context.md](references/paper-context.md).
2. Read [references/reviewer-map.md](references/reviewer-map.md) before planning or editing any response-driven change.
3. Read [references/submission-rules.md](references/submission-rules.md) before changing submission structure or declaring readiness.
4. Read [references/tkde-reuse.md](references/tkde-reuse.md) before planning experiments, importing evidence, or revising claims that overlap FredNormer/Fredformer work.
5. Read the live resubmit control plane at `/home/park/TS/FredNormer/project_management/README.md` and follow its links to the atomic reviewer inventory, paper–code–evidence matrix, Table 1 provenance audit, proposed protocol, and pinned baseline manifest.
6. Inspect the live manuscript and both workspaces' current git status. Do not rely on an earlier report when the files can be checked.
7. Preserve the immutable review PDF. Never edit or overwrite it.

## Source-of-truth order

Use sources in this order when they disagree:

1. Current official KDD 2027 CFP and FAQ.
2. Original OpenReview forum and decision for `2b776YkXBX`.
3. Immutable local review export.
4. Current Overleaf-linked manuscript.
5. Verified TIFO experiment artifacts.
6. Compatible, matched evidence from the Fuji TKDE/Fredformer workspace.
7. Derived trackers, notes, summaries, and prior Codex discussions.

Flag inconsistencies instead of silently choosing a convenient version.

## Working modes

Identify the mode before editing.

- **Highlight mode:** Mark reviewer-targeted passages only. Do not rewrite them unless explicitly asked. `\reviewhighlight{...}` is internal annotation.
- **Revision mode:** Revise claims, theory, method, experiments, figures, or prose against stable concern IDs in the reviewer map.
- **Summary mode:** Draft the one-page Summary of Changes from verified completed changes only. Start from [assets/summary-of-changes-template.tex](assets/summary-of-changes-template.tex).
- **Submission mode:** Produce a clean anonymous manuscript. Remove all review colors and internal notes. Run the preflight script.

Never treat the highlighted manuscript as submission-ready.

## Revision workflow

### 0. Use the project control plane

Do not reconstruct reviewer or experiment state from memory. The current files are:

- verbatim reviews: `/home/park/TS/FredNormer/project_management/reviews/transcribed/openreview_decision_and_reviews_verbatim.md`;
- atomic review tracker: `/home/park/TS/FredNormer/project_management/reviews/analysis/comment_inventory.md`;
- experiment compatibility and gap matrix: `/home/park/TS/FredNormer/project_management/experiments/paper_code_evidence_matrix.md`;
- main-table provenance audit: `/home/park/TS/FredNormer/project_management/experiments/table1_provenance_audit.md`;
- cross-workspace evidence ledger: `/home/park/TS/FredNormer/project_management/evidence_ledger.md`;
- proposed matched protocol: `/home/park/TS/FredNormer/project_management/experiments/protocol_contract.md`;
- pinned baseline sources: `/home/park/TS/FredNormer/project_management/baselines/THIRD_PARTY_SOURCES.md`.

Update these ledgers before promoting a result or marking a concern resolved.

### 1. Build an evidence ledger

For every proposed change, record:

- concern ID from the reviewer map;
- exact manuscript section, figure, table, equation, or experiment;
- evidence available now;
- action taken;
- remaining gap;
- readiness: `verified`, `draft`, `needs_experiment`, or `blocked`.

Do not say an experiment was run, a result improved, or a concern was resolved unless the corresponding artifact exists and is inspectable.

When TKDE evidence looks reusable, first record a compatibility check covering dataset, split, horizon, seed, input length, model/backbone, patch/stride, optimization, early stopping, metric implementation, and code revision. Reuse prose or experimental design freely; reuse numeric evidence only after this check passes.

### 2. Prioritize the decision-driving issues

Work in this order unless the user directs otherwise:

1. Close the theory–algorithm gap.
2. Justify and validate the stationarity score `S = mu/sigma`.
3. Explain TIFO’s relationship to normalization, filtering, and the cited closest methods.
4. Strengthen baselines and fairness evidence, especially recent methods and original-backbone comparisons.
5. Validate distribution-shift and stationarity-aware representation claims.
6. Reconcile the diagram, algorithm, equations, and implementation.
7. Repair tables, cross-references, inconsistent highlighting, grammar, and reproducibility details.

Do not polish an unsupported central claim before resolving its evidence gap.

### 3. Calibrate claims

- Preserve strong claims only when the manuscript contains direct evidence.
- Label interpretations as interpretations.
- Replace universal language such as “all possible time structures” when the evidence only supports training-distribution coverage.
- Do not claim that an MLP output is a rigorous eigendecomposition without a proved correspondence.
- Distinguish empirical robustness from theoretical guarantees.
- State limitations when distribution drift may leave the support represented by training data.

### 4. Keep artifacts separated

- Internal highlight/revision artifacts may contain colors and reviewer IDs.
- The submission PDF may contain only the permitted one-page Summary of Changes followed by a normal anonymous manuscript.
- Do not append the old review PDF to the submission PDF.
- Link the old forum through the OpenReview submission form as required.

### 5. Verify

From the paper-workspace root, run:

```bash
bash .codex/skills/kdd27-tifo-resubmit/scripts/check_submission_tex.sh sample-sigconf.tex
```

Pass the compiled PDF as a second argument when available:

```bash
bash .codex/skills/kdd27-tifo-resubmit/scripts/check_submission_tex.sh sample-sigconf.tex sample-sigconf.pdf
```

Treat failures as blockers. Review warnings manually.

## Summary of Changes rules

- Keep it to exactly one first page; it is outside the eight content pages.
- Organize it by decision-driving concern clusters, not reviewer-by-reviewer repetition.
- Mention only completed and verifiable changes.
- Point to concrete sections, equations, tables, figures, or appendices.
- Do not use colored changes elsewhere in the PDF.
- Do not paste the full old reviews into the PDF.

## Readiness gate

Use `ready_to_submit` only when all of the following hold:

- the OpenReview submission is marked as a resubmission;
- the previous forum URL is entered;
- author list/order and profiles satisfy the deadline rules;
- Summary of Changes is one page;
- eight-page main content is self-contained;
- manuscript is anonymous and uses the required ACM review format;
- no red/highlight markup or internal notes remain after the summary page;
- no placeholder tables, figures, citations, or result values remain;
- every claimed revision is traceable to evidence;
- the project compiles and the PDF has been visually inspected.

Otherwise report `draft_with_gaps`, `needs_experiment`, or `blocked`, and name the exact blockers.
