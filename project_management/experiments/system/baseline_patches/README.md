# Baseline protocol patches

The official baseline checkouts are pinned under `third_party/` and ignored by
the outer repository. Apply these patches inside each checkout before launching
the resubmission matrix. They remove per-epoch test-set evaluation; early
stopping remains validation-only and the test split is evaluated once after the
best validation checkpoint is restored.

- TimeEmb upstream: `9adf3fba801b34642e7191b45e08aff224b26e67`
- TFPS upstream: `83a11827e27e6617e8c8a8771f0a1dd7e10976a5`
- CN upstream: `2d6ce2f2c771fec5296870416844d995c23e31a2`
- WDAN upstream: `f01994ada4980729eb6af14c35778f480f9c0c47`

```bash
git -C third_party/TimeEmb-official/TimeEmb-main apply \
  ../../../project_management/experiments/system/baseline_patches/timeemb-validation-only.patch
git -C third_party/TFPS-official apply \
  ../../project_management/experiments/system/baseline_patches/tfps-validation-only.patch
git -C third_party/CN-official apply \
  ../../project_management/experiments/system/baseline_patches/cn-validation-seeds.patch
git -C third_party/WDAN-official apply \
  --ignore-space-change --ignore-whitespace \
  ../../project_management/experiments/system/baseline_patches/wdan-matched-runner.patch
```

The CN patch exposes the random seed, removes per-epoch test evaluation and
limits eager imports to the non-Mamba baselines used here. The WDAN patch uses
the canonical dataset root supplied through `TIFO_DATA_ROOT`, adds the Traffic
dataset configuration and logs final metrics at evidence-grade precision.
