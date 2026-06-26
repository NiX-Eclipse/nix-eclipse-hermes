## File Contract
This file answers only: Which model should handle which task class by risk?

This file must never:
- define NiX artistic canon
- replace `nix_context/` or engine rules
- auto-mutate Hermes provider config or production `nix` profile settings
- become runtime creative context loaded into every session

# Model routing — nix-eclipse-hermes

## Purpose

Route models by **task risk and responsibility**, not by generic intelligence scores.

Creative canon, engineering correctness, and routine ops have different failure modes. A model that is fine for log cleanup may be unsafe for final lyrics or CI patches.

**Status:** v0.1.0 planning note. **Advisory** unless explicit router support exists in Hermes config.

## Model identifiers

| Label | Hermes / provider id |
|---|---|
| Grok 4.3 | `grok-4.3` |
| Codex GPT-5.5 | `gpt-5.5` |
| Stepfun (free) | `stepfun/step-3.7-flash:free` |

## Routing by task class

### Creative NiX tasks

Examples: track canon, visual packs, lyrics drafts for review, taste arbitration, identity-sensitive frames, release-facing social copy.

| Priority | Model |
|---|---|
| Primary | `grok-4.3` |
| Fallback | `gpt-5.5` |
| Emergency / draft fallback | `stepfun/step-3.7-flash:free` |

### Engineering / build tasks

Examples: repo structure, evaluators, CI workflows, install scripts, contract checks, RFC implementation, debug of build failures.

| Priority | Model |
|---|---|
| Primary | `gpt-5.5` |
| Fallback | `grok-4.3` |
| Routine explanation / check fallback | `stepfun/step-3.7-flash:free` |

### Routine ops

Examples: summaries, STATUS drafts, log triage, markdown cleanup, JSON field presence checks, low-risk extraction, working-notes hygiene.

| Priority | Model |
|---|---|
| Primary | `stepfun/step-3.7-flash:free` |
| Fallback | `grok-4.3` |
| Codex | Only when script, repo, or debug work is required |

## Stepfun rules

### Allowed

- Summaries and working-note compression
- Log triage and markdown cleanup
- JSON field presence / shape checks (non-authoritative)
- Low-risk extraction from already-approved sources
- Draft scaffolding explicitly marked for upgrade

### Forbidden

Stepfun must **not** be used for:

- Final NiX canon
- Final visual packs
- Final lyrics
- Taste review or creative arbitration
- Release-critical social copy
- CI patches or workflow fixes
- Production migration steps
- Cron, auth, or jobs contour changes

### Limit-exhaustion fallback

If Stepfun is used because primary or fallback limits are exhausted:

1. Mark output **`DRAFT`** or **`EMERGENCY FALLBACK`** in the deliverable header or commit message.
2. Do not treat the output as evaluator-passing or human-review-ready without upgrade to the primary model for that task class.
3. Log which model produced the artifact (working notes or PR description).

## Enforcement

| Layer | Behaviour |
|---|---|
| This document | Advisory routing policy for operators and agents |
| Hermes `config.yaml` / CLI | Explicit operator commands only; no installer auto-mutation |
| Production `nix` profile | **Unchanged** by this package; existing chain remains operator-owned |
| Future router | May enforce routing when Hermes gains task-class router support |

See also: `provider-auth-strategy.md` (auth and profile-local setup), `ARCHITECTURE.md` (file boundaries).

## v0.1.0 gate

Model routing acceptance is a **release planning input**, not a substitute for human review of creative artifacts.

Do not tag `v0.1.0` until:

- Human re-review of `artifacts/human-review/` passes, **and**
- This routing note is accepted by the operator / team.