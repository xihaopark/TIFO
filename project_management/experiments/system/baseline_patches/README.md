# Baseline protocol patches

The official baseline checkouts are pinned under `third_party/` and ignored by
the outer repository. Apply these patches inside each checkout before launching
the resubmission matrix. They remove per-epoch test-set evaluation; early
stopping remains validation-only and the test split is evaluated once after the
best validation checkpoint is restored.

- TimeEmb upstream: `9adf3fba801b34642e7191b45e08aff224b26e67`
- TFPS upstream: `83a11827e27e6617e8c8a8771f0a1dd7e10976a5`

```bash
git -C third_party/TimeEmb-official/TimeEmb-main apply \
  ../../../project_management/experiments/system/baseline_patches/timeemb-validation-only.patch
git -C third_party/TFPS-official apply \
  ../../project_management/experiments/system/baseline_patches/tfps-validation-only.patch
```
