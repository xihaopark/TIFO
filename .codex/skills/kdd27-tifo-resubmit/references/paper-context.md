# Paper context and paths

## Identity

- Title: **TIFO: Time-Invariant Frequency Operator for Stationarity-Aware Representation Learning in Time Series**
- Previous venue: KDD 2026 Research Track, Cycle 2
- Decision: **Resubmit**, issued 16 May 2026
- OpenReview forum: <https://openreview.net/forum?id=2b776YkXBX#discussion>
- Target: KDD 2027 Research Track, Cycle 1

## Workspaces

- Paper workspace: `/home/park/TS/FredNormer_overleaf`
- Manuscript entrypoint: `/home/park/TS/FredNormer_overleaf/sample-sigconf.tex`
- Overleaf project: <https://www.overleaf.com/project/6979c817055a778f22c72582>
- Overleaf Git remote: `https://git.overleaf.com/6979c817055a778f22c72582`
- Code/experiment workspace: `/home/park/TS/FredNormer`
- Immutable review export: `/home/park/TS/FredNormer/project_management/reviews/original/KDD2027resubmit.pdf`
- Workspace conventions: `/home/park/TS/FredNormer/PROJECT_WORKSPACE.md`

## Current manuscript state

The manuscript uses `\documentclass[sigconf,anonymous,review]{acmart}`. The command `\reviewhighlight{...}` marks passages implicated by reviewer concerns. These marks are internal annotations only and must disappear from the submission manuscript.

The source also contains provisional result prose and placeholder references such as `Table X`, `Table Y`, `Table Z`, `Table W`, and `Table V`. Treat all such content as unverified until connected to real experiment artifacts and final numbered LaTeX objects.

## Operational boundary

- Preserve the review PDF unchanged.
- Put code and experiment outputs in the code workspace.
- Put manuscript source, figures, bibliography, Summary of Changes, and this skill in the paper workspace.
- Before pushing, inspect both `git status` and the diff. Do not overwrite unrelated user changes.
- Overleaf is the live paper destination, but successful Git push does not prove successful LaTeX compilation.
