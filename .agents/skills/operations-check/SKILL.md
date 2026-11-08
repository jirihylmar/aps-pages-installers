---
name: operations-check
description: Check the entry document's Operate and Rebuild section (CLAUDE.md, or AGENTS.md where there is no CLAUDE.md) against git - each of its six rows (runs without a session, health, operating notes, rebuild on another host, builds and how long, where agents take part) names a file git holds, and any heading it cites in that file, or says not built yet, or none with a reason, and none names a host path - and count how far progress.json has adopted the phase operations statement and the ops record. Use after a task that touched something that runs, when writing or changing the Operate and Rebuild section, and when repo-hygiene names it.
---

# Check Operate and Rebuild

Read `.claude/skills/operations-check/SKILL.md` completely and apply its canonical rules. Run the
shared checker from the project root:

```bash
python3 .claude/skills/operations-check/operations_check.py                   # the working tree and the index
python3 .claude/skills/operations-check/operations_check.py --rev origin/main  # one commit's tree
python3 .claude/skills/operations-check/operations_check.py --since 2026-11-08T12:00:00Z --json
```

Exit `0` every checked section complete and nothing false, `1` a row names a file git does not
hold, a heading that file does not have, or a host path (something written is false), `3` not
complete yet with nothing false (no section, or a row not built yet, unverified, empty or absent),
`2` could not check. On exit `2` nothing is clean; with `--json`, `complete_read` is then `false`.

The entry document is `CLAUDE.md`, or `AGENTS.md` where the project has no `CLAUDE.md`; a section in
`AGENTS.md` beside a `CLAUDE.md` is noted, never moved by the checker. The rule is stated once, in
`PROJECT_CHARTER.md` section 8, *Token-heavy development, token-light operation*. The checker reads the section's rows and what git holds, never prose, and it never
proves a rebuild. An existing project without the section is in a counted state, not in defect.
Do not reproduce or weaken the checks in Codex prose; this adapter and Claude run the same
executable checker.
