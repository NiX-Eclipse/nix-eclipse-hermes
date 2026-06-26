# RFC 0009 — Boosty/Patreon Content Formatter

**Status:** proposed (v0.2 backlog)  
**Not a v0.1.0 blocker**  
**Production `nix` profile:** out of scope

## Context

Earlier planning notes referred to “removing/updating `nix-boosty-patreon` topic 1490 reference.” That wording was misleading.

The real future task is not a Telegram topic cleanup. NiX needs a **content formatter workflow** that reads working-process material from the dedicated solutions repo and produces Boosty/Patreon-ready publication packages — with correct structure, tone, and tier framing.

This RFC replaces topic-1490 housekeeping as a release concern. v0.1.0 ships without this workflow.

## Source repo

```text
git@github.com:NiX-Eclipse/Nix-project-content-working-solutions.git
```

**Role of source material:**

- Human work logs (`logs/anya/`, `logs/sasha/`)
- Weekly digests (`digest/`)
- Process notes, honest fails, decision trails
- Fragments explicitly marked safe for public translation

NiX must treat this repo as **working memory**, not public voice or production canon. Formatter output is a translation layer, not a copy-paste pass.

## Target platforms

| Platform | Purpose |
|---|---|
| **Boosty** | Tiered access posts, archive drops, production notes for subscribers |
| **Patreon** | Paid post body, early/exclusive framing, CTA to support |

Outputs are **human-review packages** for manual paste/publish. No automatic posting in v0.2 initial scope unless explicitly added in a later RFC.

## Expected outputs (per run)

Each formatter run should produce a structured package containing:

| Output | Description |
|---|---|
| **Preview teaser** | Short public-facing hook; no internal jargon |
| **Paid post body** | Full subscriber post: context, value, access framing |
| **Archive drop note** | When material is early version / unreleased cut / inner file |
| **Production notes** | Process, decisions, constraints — NiX voice, not raw log voice |
| **Visual/music context summary** | Linked creative context without inventing assets |
| **CTA** | Clear support action aligned to platform norms |
| **Tier/access note** | Which tier sees what; no false exclusive claims |

Platform variants may differ in length and CTA style while sharing the same factual core.

## Formatter behaviour (proposed)

1. **Ingest** — select input from working-solutions (log entry, digest section, or marked fragment).
2. **Classify** — identify content type: process snapshot, honest fail, archive drop, production case, etc.
3. **Translate** — apply NiX public voice per `nix_context/taste.md` and platform strategy; strip internal routing, topic ids, auth paths.
4. **Package** — emit Boosty and Patreon variants with required fields above.
5. **Gate** — flag claims that need human confirmation (tier promises, exclusive artifacts, unreleased material).

Model routing for formatter work: creative-primary per `project/MODEL_ROUTING.md` (`grok-4.3` primary). Stepfun only for draft scaffolding marked `DRAFT`.

## Non-goals for v0.1 (and initial v0.2 RFC scope)

| Non-goal | Reason |
|---|---|
| Production integration | Package release only; ops `nix` untouched |
| Cron changes | No new scheduled jobs on production profile |
| Telegram topic mutation | Topic 1490 reference cleanup is not the deliverable |
| Automatic publishing | Human paste/review required |
| Auth changes | No `auth.json`, `.env`, or provider mutation |
| Tier promise invention | T1–T5 mapping waits until real tier content is defined |

## Future tests (v0.2+)

| Test | Intent |
|---|---|
| Sample working-solutions input | Fixed fixture from `logs/` or `digest/` (sanitized public-safe excerpt) |
| Expected Boosty output | JSON or markdown package with all required fields |
| Expected Patreon output | Same core facts, platform-appropriate CTA/length |
| Evaluator | Structure check (required fields present), tone check (no raw log voice, no forbidden claims), identity contract where applicable |

Example evaluator checks:

- Required keys: `preview_teaser`, `paid_post_body`, `archive_drop_note`, `production_notes`, `visual_music_context`, `cta`, `tier_access_note`
- No internal paths, topic ids, or auth references in output
- No exclusive/unreleased claims without `needs_human_confirmation: true`
- NiX taste: no victim posing, no decorative darkness, no shame-language for demos

## Relationship to existing assets

| Asset | Relationship |
|---|---|
| `nix-boosty-patreon-content-planning` skill (production) | Legacy cron/topic 1490 context; formatter RFC does not require reactivating that cron |
| `archive-2026` | Canon for what was made; working-solutions for how it was made |
| `nix-eclipse-hermes` | Hosts RFC, future evaluator fixtures, and NiX voice constraints |

## Recommendation

Track as **v0.2 backlog**. Do not block v0.1.0 package release.

Implementation order (suggested):

1. Define input/output fixtures under `tests/` or `fixtures/boosty-patreon/`
2. Add formatter prompt + schema in `project/` or dedicated skill draft (non-production)
3. Evaluator pass on sample working-solutions input
4. Human review gate before any live platform use

## Open questions

- Single formatter prompt vs separate Boosty/Patreon engine files?
- Whether weekly digest or daily log is the default input unit?
- How tier/access notes reference real T1–T5 when defined?