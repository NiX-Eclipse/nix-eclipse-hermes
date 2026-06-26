# nix-eclipse-hermes — status

| Field | Value |
|---|---|
| **Current version** | v0.1-RC |
| **Release candidate tag** | `v0.1-rc1` (CI-green on `f4c4c0f`) |
| **v0.1 release** | **not yet** |
| **Production profile `nix`** | untouched |
| **Test profiles** | `nix-eclipse-test` (local), `nix-eclipse-ci` (CI) |

## v0.1-RC (accepted 2026-06-26)

Remote CI run [#1](https://github.com/NiX-Eclipse/nix-eclipse-hermes/actions/runs/28246618662): **success**

- validate (ubuntu-latest): success
- validate (windows-latest): success
- hermes-install-smoke: success
- live-llm: skipped (push event; manual gate only)

GitHub repo: https://github.com/NiX-Eclipse/nix-eclipse-hermes

## Release blockers (v0.1 — not declared)

| Blocker | Status |
|---|---|
| Human review of smoke JSON artifacts | pending |
| Final release tag decision | pending |

## v0.1-beta (accepted)

- Rate Me Rotten v2: Grok + Hermes PASS
- Fixtures: pylnaia_kletka, no_more_light (local smoke PASS)
- provider-auth-strategy documented

## v0.1-alpha (accepted)

- Scaffold + initial smoke test

## Explicitly out of scope

- Production integration (`nix` profile, `system.md`, cron, `archive-2026`)
- v0.1 release declaration