# Main-owned SDD implementation and validation

The implemented surface is SKILL.md and phase references, one Reviewer profile, read-only cycle/state validators, state schema, exact installer migration and corresponding regression suites. No consumer/global install or remote release is part of a local code change.

## Verification strategy
1. Establish clean current repository baseline and authorized local feature branch.
2. Add meaningful failing JSON/Git/state/snapshot and migration cases before implementation; keep original identity/isolation CLI regressions.
3. Implement state and capture contracts using standard-library Python3.11+ and actual files/versions. Check nine risk categories, unknown/duplicate keys, phase nulls, history/crash consistency, coverage, independence, same-owner resolution and pairwise paths.
4. Rewrite runtime policy for Main ownership, official SpecKit and compatible Superpowers execution; adaptive dispatch remains optional.
5. Install only Reviewer in temporary destinations. Test known legacy layouts, exact backup/retirement, unrelated files, dry-run and rollback; validate distribution inventory/references/schema and portable content.
6. Run focused and whole suites, inspect real agent behavior, and obtain final independent integrated review. Main corrects verified findings and same Reviewer rechecks; retain exact commands/version/outputs as operational evidence outside frozen planning.

## Evidence limits
Unit fixtures exercise structural checks; hashes or source wording do not prove semantic intent, genuine runtime independence or token savings. Bounded behavior exercises record actual responses. Local checks, remote CI, global installation and publication must always be reported separately. New changes after review require affected evidence and review updates. Conditional verification is never completion.
