# Mrliou Closure Sync Actions Wiring v1

origin_signature: MrLiouWord

## Verified failure and scope

- Repository: `Mrliou/mrliouword-system` (preserve this exact owner; do not substitute another MRL repository).
- Run: https://github.com/Mrliou/mrliouword-system/actions/runs/36214116486 (schedule, attempt 1, 2026-09-26T03:13:04Z).
- Source: `37e6c8b4a439ccebdac127fccd21e6da3ab5ecac`; workflow `.github/workflows/closure-sync.yml`.
- First failing step: `Validate authority and routes`. `TARGET_REPOSITORY_1` was empty, sourced from `vars.MRL_SYNC_TARGET_1`. `SYNC_TOKEN` was also empty, but the original early exit prevented its diagnostic from running.
- All source/target checkout and Python setup steps were skipped. `Generate report with actual targets` nevertheless ran under `always()` and failed because `source/tools/generate_sync_report.py` had never been checked out. The script exists at this exact source SHA; its absence in the runner was secondary, not a missing source file or common runtime startup defect.
- Upload reported success as an Actions step but warned that no files were uploaded. This is not evidence delivery PASS.

## Exact configuration contract

| GitHub configuration | Kind | Workflow destination / meaning |
|---|---|---|
| `MRL_SYNC_TARGET_1` | Actions variable, required | `TARGET_REPOSITORY_1`; explicitly approved `owner/repository` |
| `MRL_SYNC_TARGET_2` | Actions variable, optional | `TARGET_REPOSITORY_2`; optional second approved target |
| `MRL_SYNC_ALLOWED_OWNER` | Actions variable | `ALLOWED_OWNER`; defaults to `github.repository_owner` (here `Mrliou`) |
| `SYNC_TOKEN` | Actions secret, required | Validator environment plus the token input of all three checkout steps |
| `github.repository` | GitHub context | `SOURCE_REPOSITORY`; the repository actually running the workflow |
| `mode`, `dry_run` | workflow_dispatch inputs | Test with `observe` / `true`; writes require explicit `full` / `false` |

`MRL_SYNC_TARGET_1` stored as a **secret** will not satisfy `vars.MRL_SYNC_TARGET_1`. A variable named `TARGET_REPOSITORY_1` also will not satisfy it: that is the process destination, not the settings key. Likewise a variable named `SYNC_TOKEN` does not satisfy `secrets.SYNC_TOKEN`. `.mrliou/sync.config.json` defines synchronization rules and paths, not repository targets, and does not populate Actions settings. A local `.env` is not loaded by this workflow.

Targets and owner are non-secret routing/authorization configuration and belong in variables or reviewed explicit YAML, not guessed defaults. The token belongs in secrets and must authorize source and approved targets. Read access suffices for checkout in observe/dry-run; any later approved `full` write needs the corresponding repository permissions. Never grant access to unrelated repositories to fix a name/scope issue.

The current `ALLOWED_OWNER` is `Mrliou`. If an approved target uses another owner string, the existing gate will reject it unless `MRL_SYNC_ALLOWED_OWNER` is explicitly aligned. This is a repository route check, not a reclassification of MRL system ownership or provenance. No target or additional owner is selected by this repair. Both declared targets must satisfy the same existing owner check.

## Scope and visibility

The job has no `environment:` selection. Repository-scoped settings must be on **`Mrliou/mrliouword-system`**; identically named settings in `dofaromg/mrliouword-system` do not flow here. Environment-only settings require the exact Environment to be selected by the job; do not invent one. Organization settings, where applicable, must grant the running repository access.

Authenticated, read-only inspection of this exact repository's Actions settings on 2026-09-26 confirmed: no Repository secrets, no Environment secrets, and no Organization secrets available to the repository; the Variables tab likewise reports no Repository variables, no Environment variables, and no Organization variables available. Thus `SYNC_TOKEN` and the route variables are absent from the visible execution scope. No spelling mismatch was found in the YAML references. Settings in other repositories were not inspected or assumed to exist. Only configuration names and empty-state notices were inspected; no secret value was requested or read.

Settings: [Secrets](https://github.com/Mrliou/mrliouword-system/settings/secrets/actions), [Variables](https://github.com/Mrliou/mrliouword-system/settings/variables/actions).

## Minimal branch repair

- Aggregate both missing target and token errors before exiting; remain fail-closed before checkout.
- Preserve source authority, owner gate, variable/secret names, schedule, modes, and candidate-branch-only writes.
- Give prerequisite steps stable IDs and allow the final report only when source and every declared target checkout, plus Python setup, succeeded. Subsequent sync/verification failures can still produce a diagnostic report; cancellation or incomplete prerequisites cannot.
- Include the configuration validation outcome in the summary. The original failure is not changed into success.

## Validation

Run `python -m pytest -q tests/test_closure_workflow_wiring.py tests/test_closure_sync_safety.py` with PyYAML and test dependencies. New tests execute the Bash validator with synthetic values, check missing target/token together, reject mismatched source/owner, ensure no token output, and exercise all 64 boolean combinations of the report guard. These tests do not clone or write any remote repository.

For live branch validation, choose the reviewed branch in workflow_dispatch, `mode=observe`, `dry_run=true`, and confirm its `head_sha`. Without settings, expect both configuration diagnostics, skipped checkout/Python/report, and a failed run with no verification claim. After the explicitly approved target and source-repository secret scope are supplied, repeat on the branch and inspect checkout, sync, consistency verification and actual report artifacts. A green configuration gate alone is not consistency PASS. No main push or target sync write is authorized by this validation procedure.

References: [GitHub secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [GitHub variables](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-variables).
