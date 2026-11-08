---
name: add-work
description: Add an explicitly authorized phase or task to a syndicate project's progress.json, including sizing, verification, authorship, assignment, task-file and session-note updates. Use when the operator asks to track or add work; do not use merely because an idea was discussed.
---

# Add tracked work

Read `.claude/commands/add-work.md` completely and execute it as the canonical procedure, translating
Claude tool names to available Codex capabilities. Preserve its approval gate and four-destination
routing contract. Every new phase/task must include non-empty `authored_by` and `assigned_to`; they
may differ. Every new phase also carries `operations`: how what it builds runs without a session,
is checked and is rebuilt from a clean clone on any host, or `none: <reason>` (`PROJECT_CHARTER.md` § 8, *Token-heavy development, token-light operation*).
Invoke named slash workflows as their corresponding `$skill-name` when available.
