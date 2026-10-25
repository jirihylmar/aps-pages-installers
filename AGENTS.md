# aps-pages-installers — Codex entry

What this project is for: `description` in `progress.json` (kept true by its own sessions — PROJECT_CHARTER.md § 11).

Codex is an authorized executor for this orchestration repository. The detailed project rules live
in `CLAUDE.md`; read that file completely before acting. It is the single project-owned source for
architecture, repository identities, environment facts, workflow discipline and safety rules.
This file adapts entry and invocation for Codex and must not duplicate that prose.

Read `PROJECT_CHARTER.md` completely before acting. It is the centrally owned, executor-neutral
delivery contract and takes precedence over conflicting workflow prose.

An operation that outlives a turn is governed by that charter's section 11,
*Unattended operations*. Never describe an operation as watched or monitored unless the
charter's supervisor proof actually holds for it at that moment.


## Codex workflow

- `progress.json` is the source of truth for work state.
- Repository workflows are Codex skills under `.agents/skills/`; invoke them with `$skill-name`.
- Start with `$start-session` and close work with `$update-progress`.
- If an adapter instructs you to read a canonical file under `.claude/commands/`, follow the
  procedure body and translate Claude-only frontmatter or tool identifiers to equivalent available
  capabilities. The `.claude` path remains live because existing Claude executors use it.
- Every phase/task you add must carry `authored_by` and `assigned_to`. Record `Codex` when you wrote
  or own the work; do not infer that the operator owns execution merely because they approved it.
- Task 0.5 remains a blocking specification-approval checkpoint.
- A completed task, progress update, commit, push, or changed `current_task` is not a session
  boundary. During an authorized run, announce it briefly and continue into the next ready task in
  the same turn. Yield only for a declared approval checkpoint, genuine blocker, explicit stop
  request, or when no safe authorized work remains.

### Asynchronous work is still active work

- A queued or running build, deployment, migration, test, scan, or other job is ordinary ongoing
  work, not a blocker or session boundary. Keep the turn active and retain the job/session
  handle needed to inspect it again.
- Wait or poll in bounded intervals no longer than 60 seconds. Between intervals, use concise
  commentary updates when useful; commentary does not end execution. Do not send a final response
  while the job is non-terminal if its result is required to complete the authorized work.
- A final response ends active execution: never claim to be monitoring after sending one. Do not
  say that you will continue in the background. Continue polling until success or failure; on
  success inspect the resulting artifact or live system and proceed, and on failure collect the
  relevant evidence and either fix/retry in scope or report a genuine blocker.
- When the operator explicitly creates or requests a durable goal (for example with `/goal` or
  “create a persistent goal”), use Codex's goal mechanism so a clear long-running objective can
  continue across ordinary turn boundaries. Do not create a goal merely because one command is
  slow; bounded waiting in the current turn remains the default.

## Codex configuration boundary

Do not create or commit `.codex/`. Repository skills belong in `.agents/skills/`. Codex host
configuration, credentials and Model Context Protocol server commands are host-owned or injected
per invocation and never enter this repository.
