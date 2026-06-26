# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | v0.1-RC |
| **Release candidate tags** | `v0.1-rc1` (CI), `v0.1-rc2` (human-review fix, pending CI) |
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

Run #1: [#28246618662](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28246618662) — success (`v0.1-rc1`)

## Release blockers (v0.1.0)

- [ ] Human review of committed artifacts (post-rc2)
- [ ] Final release tag decision
- [ ] Remote CI green on rc2 commit

## Explicitly out of scope

- Production integration
- v0.1.0 tag
- `no_more_light_canon` fixture (v0.2)