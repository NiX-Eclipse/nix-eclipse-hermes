# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | **v0.1.0** |
| **Release type** | Package release only |
| **Production integration** | Not performed |
| **Production profile `nix`** | Untouched |
| **Model routing** | Accepted (`project/MODEL_ROUTING.md`) |
| **Mount decision** | Dedicated repo by default (`rfc/0008-mount-decision.md`) |
| **Auth strategy** | Accepted (`provider-auth-strategy.md`) |
| **Release tags** | `v0.1-rc1` → `f4c4c0f`, `v0.1-rc2` → `2f30405`, `v0.1.0` → `6cf5e22` |
| **v0.1.1 candidate** | Feminine bare-chat voice hardened; bare_chat_voice evaluator PASS — Telegram route pending test topic |

## v0.1.0 package scope

Hermes creative package: profile SOUL + project AGENTS/nix_context + acceptance fixtures + CI.

**Not included:** production `nix` install, cron/auth/jobs mutation, `archive-2026` mount.

## Human review (accepted for v0.1.0 package)

Artifacts in `artifacts/human-review/` accepted for package release scope:

```text
artifacts/human-review/grok-rate-me-rotten.v2.json
artifacts/human-review/hermes-rate-me-rotten.v2.json
artifacts/human-review/grok-pylnaia-kletka.rc.json
artifacts/human-review/hermes-pylnaia-kletka.rc.json
artifacts/human-review/grok-setting-exit-smoke.rc.json
artifacts/human-review/hermes-setting-exit-smoke.rc.json
```

Legacy `demo-nix-project/grok-rate-me-rotten.json` (no contract field) — **do not use**.

## Model routing

Advisory task-class routing in **`project/MODEL_ROUTING.md`**. No automatic provider config mutation.

| Task class | Primary | Fallback | Emergency |
|---|---|---|---|
| Creative NiX | `grok-4.3` | `gpt-5.5` | `stepfun/step-3.7-flash:free` |
| Engineering / build | `gpt-5.5` | `grok-4.3` | `stepfun/step-3.7-flash:free` (routine only) |
| Routine ops | `stepfun/step-3.7-flash:free` | `grok-4.3` | `gpt-5.5` if script/repo/debug needed |

## Remote CI

| Run | Tag / commit | Result |
|---|---|---|
| [#28246618662](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28246618662) | `v0.1-rc1` → `f4c4c0f` | **success** |
| [#28247531822](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28247531822) | `v0.1-rc2` → `2f30405` | **success** |

## v0.1.1 candidate (in progress)

- Feminine voice hardened: `SOUL.md`, `identity.md`, `conversation.md`
- Bare chat fixture: `bare_chat_voice` + `evaluate_bare_chat_voice.py` — **PASS** on v010
- Telegram preamble: `telegram-v010-chat-preamble.txt` + `channel_prompts` in apply-test-route
- **Blocked until operator:** test topic id + dedicated test bot → then apply route + start v010 gateway only

## v0.2 scope (explicitly deferred)

- `no_more_light_canon` fixture (greenhouse, dead garden, genre anchors)
- Optional explicit Hermes task-class router support
- Richer engines derived from Grok creative references
- **Boosty/Patreon Content Formatter** from `Nix-project-content-working-solutions` (`rfc/0009-boosty-patreon-content-formatter.md`) — not a v0.1.0 blocker

## Explicitly out of scope (v0.1.0)

- Production integration
- Production `nix` profile mutation (`system.md`, cron, `jobs.json`, auth, gateway, `terminal.cwd`)
- `archive-2026` mount