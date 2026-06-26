## File Contract
This file answers only: Where are the responsibility boundaries between project files?

This file must never:
- define NiX canon
- contain engine rules
- become runtime creative context

# NiX Eclipse Hermes v0.1 Architecture

Rule Zero:
Every file must answer exactly one question.
If it answers two, split the file.

Runtime exception:
`AGENTS.md` may contain a short runtime digest needed for Hermes/Grok operation.
The authoritative source still lives in `nix_context/`.

## Responsibility Map

`SOUL.md`
answers:
- Who is the agent?
- Why does it exist?
- What must never break?
- How does it work?

`AGENTS.md`
answers:
- How should Hermes use this project?

`intent.md`
answers:
- Why does NiX exist artistically?

`perception.md`
answers:
- What does NiX notice before interpretation?

`taste.md`
answers:
- How does NiX distinguish strong from weak decisions?

`identity.md`
answers:
- What must remain recognisably NiX?

`engines/*.md`
answer:
- How is the work executed in each medium?

`rfc/*.md`
answer:
- Which future ideas are not yet in product scope?

`MODEL_ROUTING.md`
answers:
- Which model should handle which task class by risk?

Advisory only for v0.1.0 planning. Does not auto-mutate provider config. See `provider-auth-strategy.md`.