---
name: generate-phases
description: Convert an approved IMPLEMENTATION_PLAN.md into session-sized implementation phases and tasks in progress.json and tasks/. Use after the Phase 0 specification is explicitly approved, never before task 0.5 closes.
---

# Generate implementation phases

Read `.claude/commands/generate-phases.md` completely and execute it as the canonical procedure,
translating Claude tool names to available Codex capabilities. The implementation specification must
already be explicitly approved. Every generated phase/task records `authored_by` and `assigned_to`;
use the selected project executor unless the operator assigns work elsewhere. Every generated phase
also records `operations`, and the first phase that builds something that keeps running carries the
task that fills the entry document's `## Operate and Rebuild` rows and proves the rebuild from a
clean clone on another host (`PROJECT_CHARTER.md` § 8, *Token-heavy development, token-light operation*).
