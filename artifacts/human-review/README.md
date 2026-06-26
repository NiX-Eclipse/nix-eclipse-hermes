# Human review artifacts

Committed smoke outputs for evaluator-aligned human review.

## Rate Me Rotten (v0.1-beta contract)

Use **only** the `.v2.json` files — they include mandatory `identity_invariants_preserved`:

- `grok-rate-me-rotten.v2.json`
- `hermes-rate-me-rotten.v2.json`

Do **not** use legacy `grok-rate-me-rotten.json` / `hermes-rate-me-rotten.json` (pre-beta, no contract field).

Regenerate: `./scripts/smoke_all_fixtures.sh` (writes here).

## Пыльная клетка

- `grok-pylnaia-kletka.rc.json` — stronger creative reference
- `hermes-pylnaia-kletka.rc.json` — acceptable smoke, not final canon

## setting_exit_smoke

Lightweight setting-shift smoke only — **not** No More Light track canon (deferred v0.2).

- `grok-setting-exit-smoke.rc.json`
- `hermes-setting-exit-smoke.rc.json`

## conversation_voice (v0.1.1)

Chat persona smoke — feminine NiX voice, no tool lists, RFC 0009 DRAFT awareness.

- `grok-conversation-voice.rc.json`
- `hermes-conversation-voice.rc.json`

Regenerate: `./scripts/smoke_conversation_voice.sh`