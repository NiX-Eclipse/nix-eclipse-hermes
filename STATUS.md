# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | **v0.1.1** |
| **Release type** | Package release + production voice patch |
| **Production integration** | **Complete** (unified NiX, 2026-06-26) |
| **Canonical runtime** | **`nix`** profile (`~/.hermes/profiles/nix`) |
| **Staging profile** | `nix-eclipse-v010` — installed, **gateway stopped** |
| **Gateway policy** | **One gateway only** — `hermes-gateway-nix.service` → `hermes -p nix` |
| **Model routing** | Accepted (`project/MODEL_ROUTING.md`, advisory) |
| **Mount decision** | Dedicated repo by default (`rfc/0008-mount-decision.md`) |
| **Auth strategy** | Accepted (`provider-auth-strategy.md`) |
| **Release tags** | `v0.1-rc1` → `f4c4c0f`, `v0.1-rc2` → `2f30405`, `v0.1.0` → `6cf5e22`, **`v0.1.1` → `3df5e18`** |
| **v0.1.1 voice patch** | **Accepted in production** — Telegram production smoke **PASSED** |

## Unified NiX migration (2026-06-26)

Decision: stop two active Telegram personas. One NiX, one character, one Telegram surface.

| Item | State |
|---|---|
| Production `nix` | Canonical — Telegram, cron/jobs, ops skills, watchdog, gateway |
| `nix-eclipse-v010` | Staging only — no parallel gateway, no live Telegram agent |
| `system.md` | Additive merge (ops preserved + v0.1.1 voice/creative context) |
| `SOUL.md` | v0.1.1 feminine artist persona |
| `config.yaml` | `telegram.channel_prompts` for NiX PROJECT chat |
| Creative canon | Read-on-demand from `project/nix_context/` (package repo path) |
| Token | Unchanged (operator did not confirm replacement) |
| Cron / `jobs.json` | Unchanged (3 jobs) |
| Rollback | `/home/user/nix/migration-backup/2026-06-26-unified-nix/rollback.sh` |

**Do not:** run `nix` + `nix-eclipse-v010` gateways in parallel; move production token to v010 without explicit staging-bot intent.

## v0.1.1 production voice patch (accepted)

Imported into production `nix` from package `3df5e18`:

- Feminine Russian self-reference rules (`SOUL.md`, `identity.md`, `conversation.md` logic)
- NiX artist persona + anti-assistant bans (no `/help`, tool lists, profile offers, «готов работать»)
- Creative context routing (`AGENTS.md`, `nix_context/`)
- RFC 0009 awareness (future v0.2 formatter — not live publishing)
- MODEL_ROUTING advisory (production model chain unchanged)

**Verification:** Telegram production voice smoke **PASSED** (operator confirmed, 2026-06-26).

## v0.1.0 / v0.1.1 package scope

Hermes creative package: profile SOUL + project AGENTS/nix_context + acceptance fixtures + CI + conversation voice engine.

**v0.1.0:** package-only, no production touch.  
**v0.1.1:** voice hardening + bare_chat_voice evaluator; production merge completed separately.

## Human review (accepted)

Artifacts in `artifacts/human-review/` accepted for package release scope:

```text
artifacts/human-review/grok-rate-me-rotten.v2.json
artifacts/human-review/hermes-rate-me-rotten.v2.json
artifacts/human-review/grok-pylnaia-kletka.rc.json
artifacts/human-review/hermes-pylnaia-kletka.rc.json
artifacts/human-review/grok-setting-exit-smoke.rc.json
artifacts/human-review/hermes-setting-exit-smoke.rc.json
artifacts/human-review/grok-conversation-voice.rc.json
artifacts/human-review/hermes-conversation-voice.rc.json
```

## Model routing

Advisory task-class routing in **`project/MODEL_ROUTING.md`**. No automatic provider config mutation.

| Task class | Primary | Fallback | Emergency |
|---|---|---|---|
| Creative NiX | `grok-4.3` | `gpt-5.5` | `stepfun/step-3.7-flash:free` |
| Engineering / build | `gpt-5.5` | `grok-4.3` | `stepfun/step-3.7-flash:free` (routine only) |
| Routine ops | `stepfun/step-3.7-flash:free` | `grok-4.3` | `gpt-5.5` if script/repo/debug needed |

Production `nix` chain remains operator-owned: `stepfun/step-3.7-flash:free` → `grok-4.3` → `gpt-5.5`.

## Remote CI

| Run | Tag / commit | Result |
|---|---|---|
| [#28246618662](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28246618662) | `v0.1-rc1` → `f4c4c0f` | **success** |
| [#28247531822](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28247531822) | `v0.1-rc2` → `2f30405` | **success** |

## v0.2 scope (explicitly deferred)

- `no_more_light_canon` fixture (greenhouse, dead garden, genre anchors)
- Optional explicit Hermes task-class router support
- Richer engines derived from Grok creative references
- **Boosty/Patreon Content Formatter** from `Nix-project-content-working-solutions` (`rfc/0009-boosty-patreon-content-formatter.md`) — not active in production

## Explicitly out of scope (post-v0.1.1)

- Second live Telegram gateway (`nix-eclipse-v010`)
- Parallel production + staging bot on same token
- `archive-2026` mount
- Automatic token migration without operator confirm