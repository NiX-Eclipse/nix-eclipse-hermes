# Provider & auth strategy — nix-eclipse-hermes

## Scope

This document applies to the **nix-eclipse** / **nix-eclipse-test** / **nix-eclipse-ci** Hermes profiles only.

**Production profile `nix` is out of scope.** Never modify its `auth.json`, `.env`, `config.yaml` ops contour, or `jobs.json` as part of this package.

## Model routing (advisory)

Task-class model selection is defined in **`project/MODEL_ROUTING.md`**.

| Principle | Rule |
|---|---|
| Routing basis | Task risk and responsibility — not generic intelligence |
| Config mutation | **Never automatic.** Operator runs explicit `hermes config set` when adopting a chain |
| Installer | `install_profile.py` sets provider/model **only** when `--provider` / `--model` flags are passed |
| Production `nix` | Existing chain unchanged; routing doc does not override ops profile |
| Enforcement | Advisory until Hermes gains explicit task-class router support |

Example profile-local setup remains operator choice. Creative-primary example:

```bash
hermes -p $PROFILE config set model.default grok-4.3
```

Engineering-primary operators may prefer `gpt-5.5` as default; see `MODEL_ROUTING.md` for fallbacks and Stepfun boundaries.

## Forbidden (all environments)

| Action | Status |
|---|---|
| Silent `auth.json` copy in `install_profile.py` or wrappers | **Forbidden** |
| Installer mutating auth state | **Forbidden** |
| Copying production `nix` auth into another profile without explicit operator step | **Forbidden** |
| Committing tokens, `auth.json`, or `.env` into git | **Forbidden** |

Verified: `scripts/install_profile.py` contains no `auth.json` references.

## Recommended production auth setup (nix-eclipse profile)

When `nix-eclipse` is promoted beyond demo (post-RC, pre-integration):

### 1. Dedicated profile

```bash
hermes profile install ./build/nix-eclipse-package/profile \
  --name nix-eclipse --force --yes
```

### 2. Profile-local provider (explicit commands)

```bash
PROFILE=nix-eclipse
HERMES_HOME=~/.hermes/profiles/$PROFILE

hermes -p $PROFILE config set model.provider xai-oauth
hermes -p $PROFILE config set model.default grok-4.3
hermes -p $PROFILE config set model.base_url https://api.x.ai/v1
```

Or for Nous primary:

```bash
hermes -p $PROFILE config set model.provider nous
hermes -p $PROFILE config set model.default stepfun/step-3.7-flash:free
```

### 3. Secrets — profile `.env` only

```bash
# ~/.hermes/profiles/nix-eclipse/.env  (never commit)
XAI_API_KEY=...
OPENROUTER_API_KEY=...   # optional fallback
```

Or OAuth via documented CLI:

```bash
hermes -p nix-eclipse auth xai-oauth
```

### 4. Before profile update

```bash
hermes profile export nix-eclipse -o nix-eclipse-backup-$(date +%Y%m%d).tar.gz
hermes profile install <new-distribution> --name nix-eclipse --force --yes
# re-apply provider config + verify .env / auth intact
```

### 5. Grok Build (creative project dir)

```bash
cd <creative-project-root>
export XAI_API_KEY=...   # or browser login once
grok inspect
```

## Dev / CI smoke (acceptable)

| Context | Auth approach |
|---|---|
| Local `nix-eclipse-test` | `hermes config set` on test profile + `hermes auth` or `.env` |
| CI `nix-eclipse-ci` | Install smoke only (no live LLM unless manual workflow + secret) |
| Live LLM CI job | `workflow_dispatch` + `vars.RUN_LIVE_LLM=true` + `secrets.XAI_API_KEY` |

**Smoke-only note (not production):** manual one-off `auth.json` copy between dev profiles is documented as a shortcut only. It must never be scripted in the installer.

## Production `nix` — do not touch

The ops profile keeps its own auth and model chain:

```text
stepfun/step-3.7-flash:free → grok-4.3 → gpt-5.5
```

`nix-eclipse` auth setup is **independent**. No shared `auth.json` between profiles in automation.

`MODEL_ROUTING.md` describes a **target** routing policy for nix-eclipse creative work. It does not rewrite the production chain above.

## CI policy

- **Offline validate:** always runs (syntax, build, contracts)
- **Hermes install smoke:** runs on Ubuntu (profile install, metadata, blocker test)
- **Live LLM:** manual trigger only; requires `XAI_API_KEY` secret; no `auth.json` artifact reuse