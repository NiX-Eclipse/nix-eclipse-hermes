# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | v0.1-beta |
| **Next target** | v0.1-RC |
| **Production profile `nix`** | untouched |
| **Test profiles** | `nix-eclipse-test` (local), `nix-eclipse-ci` (CI) |

## v0.1-RC preparation (in progress)

- [x] Git repo initialized (`/home/user/nix/nix-eclipse-hermes`)
- [x] CI workflow (offline validate + hermes install smoke + gated live LLM)
- [x] Fixture: Пыльная клетка (`pylnaia_kletka`)
- [x] Fixture: No More Light (lightweight setting-exit)
- [x] `provider-auth-strategy.md` production section
- [x] `rfc/0008-mount-decision.md` (recommend dedicated repo)
- [x] Пыльная клетка PASS Grok + Hermes (local RC smoke 2026-06-26)
- [x] No More Light PASS Grok + Hermes (local RC smoke 2026-06-26)
- [ ] CI green on remote (after push)
- [ ] Mount decision accepted by team

## Release blockers (v0.1 — not declared)

| Blocker | Status |
|---|---|
| CI added | ✅ workflow committed |
| Пыльная клетка PASS (Grok + Hermes) | pending local/RC smoke |
| Third fixture smoke PASS | pending local/RC smoke |
| Provider/auth production strategy accepted | ✅ documented |
| Mount decision accepted | proposed — RFC 0008 |
| Production cron safety verified | ✅ unchanged at beta |

## v0.1-beta (accepted 2026-06-26)

- Rate Me Rotten v2: Grok + Hermes PASS
- `identity_invariants_preserved` contract field
- Production safety verified

## v0.1-alpha (accepted)

- Scaffold + initial smoke test

## Explicitly out of scope

- Replace production `nix` with `nix-eclipse`
- Edit production `system.md`, `jobs.json`, cron
- Mount into `archive-2026` (deferred until post-RC)
- `auth.json` copy as install mechanism
- Declare v0.1 release