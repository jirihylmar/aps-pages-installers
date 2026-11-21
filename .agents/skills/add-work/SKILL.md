---
name: add-work
description: Add an explicitly authorized phase or task to a syndicate project's progress.json, including sizing, verification, authorship, assignment, task-file and session-note updates. Use when the operator asks to track or add work; do not use merely because an idea was discussed.
---

# Add tracked work

Read `.claude/commands/add-work.md` completely and execute it as the canonical procedure, translating
Claude tool names to available Codex capabilities. Preserve its approval gate and four-destination
routing contract. Every new phase/task must include non-empty `authored_by` and `assigned_to`; they
may differ. Every new phase also carries `operations`: how what it builds runs without a session,
which command will say whether it is healthy, and how a clean clone on another host rebuilds it,
given only the credentials and access hyl-resources-manager issues, or `none: <reason>` when it
builds nothing that keeps running. A phase that builds something that runs also has a task whose
verify makes its rows in the entry document's `## Operate and Rebuild` section true
(`PROJECT_CHARTER.md` § 8, *Token-heavy development, token-light operation*).
Invoke named slash workflows as their corresponding `$skill-name` when available.
Where the procedure's commit messages end with `Assisted-by: Claude Code`, write `Assisted-by: Codex`
instead (`PROJECT_CHARTER.md` § 8, *AI assistance is disclosed, not credited as authorship*).
