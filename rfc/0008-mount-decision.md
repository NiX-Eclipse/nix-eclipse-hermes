# RFC 0008 — Project bundle mount decision

**Status:** proposed (v0.1-RC)  
**Decision target:** before v0.1 release, not before RC pass  
**Production `nix` profile:** out of scope for this RFC

## Context

`nix-eclipse-hermes` ships two parts:

1. **Profile distribution** (`profile/`) — `SOUL.md`, `config.yaml`, Hermes defaults  
2. **Project bundle** (`project/` + `tests/`) — `AGENTS.md`, `nix_context/`, acceptance fixtures

The mount decision is: **where does the project bundle live at runtime** after install?

## Options compared

| Option | Description | Pros | Cons |
|---|---|---|---|
| **A. Dedicated repo** | `NiX-Eclipse/nix-eclipse-hermes` or `nix-eclipse-creative` holds `project/`; `terminal.cwd` points there | Clean separation from ops + production memory; independent CI/versioning; no cron collision | Extra repo to sync; operator must clone + install |
| **B. `archive-2026` creative subfolder** | e.g. `archive-2026/05_creative/nix_context/` | Near production canon; single sync script | Risks mixing read-only production memory with editable creative bundle; higher blast radius; cron/agent confusion |
| **C. Production profile attachment** | Copy `project/` into `~/.hermes/profiles/nix/` | One profile path | **Rejected for RC** — collides with ops `system.md`, cron, skills; violates production safety rules |

## Recommendation (v0.1-RC)

**Prefer Option A — dedicated repo** until RC passes all acceptance fixtures and CI is green.

```text
NiX-Eclipse/nix-eclipse-hermes   (this package)
  profile/  → hermes profile install
  project/  → copied to dedicated working clone (demo or team creative repo)
  tests/    → travels with project copy
```

Production contour remains:

```text
profile nix          → system.md, cron, 16 skills (ops)
archive-2026         → production memory (read-first)
nix-telegram-public  → trend_radar outputs only
```

## Install flow (recommended)

1. Clone `nix-eclipse-hermes` (or pull release tag)
2. `python scripts/build.py --project-root <creative-working-dir>`
3. `python scripts/install_profile.py --profile-name nix-eclipse --project-root <creative-working-dir>`
4. `hermes config set terminal.cwd <creative-working-dir>` on **nix-eclipse** profile only

Do **not** set production `nix` `terminal.cwd` to creative bundle without migration plan.

## Promotion criteria (RFC → accepted)

- [ ] CI validate + hermes-install-smoke green
- [ ] Rate Me Rotten PASS (Grok + Hermes)
- [ ] Пыльная клетка PASS (Grok + Hermes)
- [ ] No More Light lightweight PASS
- [ ] Mount decision reviewed by team
- [ ] Production cron smoke unchanged on `nix` profile

## Deferred

- Mount into `archive-2026` — revisit only after dedicated-repo RC pass
- Merging `nix-eclipse` profile with production `nix` — separate migration RFC