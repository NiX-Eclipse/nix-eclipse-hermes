# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | v0.1-rc2 |
| **Release candidate tags** | `v0.1-rc1` → `f4c4c0f`, `v0.1-rc2` → `2f30405` |
| **v0.1.0 release** | **not yet** |
| **Production profile `nix`** | untouched |

## Human review (2026-06-26)

**PARTIAL PASS** → blockers addressed:

| Item | Resolution |
|---|---|
| Rate Me Rotten artifacts | Committed evaluator-aligned `.v2.json` in `artifacts/human-review/` |
| No More Light naming | Renamed to `setting_exit_smoke` (not track canon; v0.2 for real canon) |
| Пыльная клетка | Human PASS — no RC changes |

## Review artifacts (use these files)

```text
artifacts/human-review/grok-rate-me-rotten.v2.json
artifacts/human-review/hermes-rate-me-rotten.v2.json
artifacts/human-review/grok-pylnaia-kletka.rc.json
artifacts/human-review/hermes-pylnaia-kletka.rc.json
artifacts/human-review/grok-setting-exit-smoke.rc.json
artifacts/human-review/hermes-setting-exit-smoke.rc.json
```

Legacy `demo-nix-project/grok-rate-me-rotten.json` (no contract field) — **do not use**.

## Remote CI

| Run | Tag / commit | Result |
|---|---|---|
| [#28246618662](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28246618662) | `v0.1-rc1` → `f4c4c0f` | **success** |
| [#28247531822](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28247531822) | `v0.1-rc2` → `2f30405` | **success** |

## Model routing (v0.1.0 planning)

Advisory task-class routing defined in **`project/MODEL_ROUTING.md`**:

| Task class | Primary | Fallback | Emergency |
|---|---|---|---|
| Creative NiX | `grok-4.3` | `gpt-5.5` | `stepfun/step-3.7-flash:free` |
| Engineering / build | `gpt-5.5` | `grok-4.3` | `stepfun/step-3.7-flash:free` (routine only) |
| Routine ops | `stepfun/step-3.7-flash:free` | `grok-4.3` | `gpt-5.5` if script/repo/debug needed |

Routing is **advisory** — no automatic provider config mutation. Production `nix` profile unchanged.

## Release blockers (v0.1.0)

- [ ] Human re-review of `artifacts/human-review/` (post-rc2)
- [ ] Model routing note accepted (`project/MODEL_ROUTING.md`)
- [ ] Final v0.1.0 tag decision

## Explicitly out of scope

- Production integration
- v0.1.0 tag
- `no_more_light_canon` fixture (v0.2)