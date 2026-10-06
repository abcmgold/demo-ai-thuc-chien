# AGENTS.md

Repo of team **GenAI Nexus** (`AITC-418`) for the AI Thực Chiến competition. Topic not
assigned yet. Current round folder: `chung-khao/` (called `<round>` below).

## Organizer constraints (README wins over this file)

- All source, docs and demo live under `<round>/`. Work only in the open round folder.
- Do not modify or delete the organizers' folder structure.
- Never push secrets (API keys, `.env`, passwords).
- AI usage logging is automatic: see `.agents/rules/ai-log-hook.md`.

## §0. Plan before code

Before writing any code for a feature, enhancement or bugfix, create
`<round>/docs/YYYY-MM-DD/<feature-name>/plan.md` (start date, kebab-case name).
Optional siblings: `design.md`, `notes.md`. Required for new features: `test-plan.md` (§2).

Every doc starts with:

```markdown
---
author: <name or email>
date: YYYY-MM-DD
status: todo | in-progress | done
agents: <comma-separated agent IDs affected>
summary: <one line>
---
```

- A plan contains: problem statement, requirements, decisions made, implementation
  approach, and ends with a `## To-do` checklist (`- [ ] task`).
- Status: `todo` = not started, `in-progress` = implementation started, `done` =
  finished **and verified by a human**. Agents never set `done` on their own.
- To implement a plan, use the `implement-plan` skill (`.agents/skills/implement-plan/`):
  follow the design exactly, tick tasks as they finish, and report only when every task
  is checked (or when blocked).
- After every verified code change or fix, commit it with the `git-auto-commit` skill
  (`.agents/skills/git-auto-commit/`).
- Push only when a plan becomes `done`: `implement-plan` then pushes and runs
  `scripts/submit_log.py`. Never push at any other time.

## §1. No hardcoded values

Load API keys, URLs, model names, credentials and tunable parameters from `.env` or a
config file. Secrets go in `.env` only. Append every new key to `.env.example` without
removing the organizers' entries.

## §2. Tests

Every new feature has a `test-plan.md` covering unit tests and end-to-end tests. Unit
tests run in the sandbox. End-to-end tests run in the real environment and cost money, so
cover as much logic as possible with unit tests.

## §3. Log config — TODO (defined when the real project starts)

## §4. Source code structure — TODO (all source stays under `<round>/`)

## §5. Deployment — TODO (deployment and running steps)

## §6. Definition of Done — TODO
