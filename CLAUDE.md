# aps-pages-installers

What this project is for: `description` in `progress.json` (kept true by its own sessions — PROJECT_CHARTER.md § 11).

Read `PROJECT_CHARTER.md` completely before acting. It is the centrally owned, executor-neutral
delivery contract; this file adds project-specific facts and rules.

**This repository is the recoverable product definition and principal manager of the project.**
Application code, infrastructure, operations, schemas, tests, documentation and work state belong
here by default. Any separately declared repository answers to this product outcome and must have a
real independent lifecycle, as required by `PROJECT_CHARTER.md`.

## This Project

- **Windows-native build.** The checkout lives on the Windows drive (`C:\Users\jirih\aps-pages-installers`,
  `/mnt/c/Users/jirih/aps-pages-installers` from WSL) and stays there: `build.ps1`, `install.ps1` and
  `uninstall.ps1` are PowerShell, and the screensaver is a .NET 8 / WebView2 `.scr`. It is developed on
  this computer only. `/start-session` § 0.9 (from `.claude/local-overlays/start-session.md`) verifies
  the toolchain and skips unneeded rebuilds.
- **Session close is `/update-progress`.** `/end-session` is this project's own build-and-release
  checklist (rebuild if the source changed, optional GitHub release, which always needs the operator's
  yes). Run it before `/update-progress` when a session changed code; it does not replace it.
- **Build outputs are never committed:** `build/`, `src/ApsScreensaver/bin/`, `src/ApsScreensaver/obj/`
  and `*.scr` stay ignored. Releases carry the binary.
- **`.claude/settings.local.json` is the operator's** local file: listed in `.gitignore`, never staged
  by a session.

---

## Quick Reference

| Item | Value |
|------|-------|
| AWS Account | none — this project uses no AWS |
| AWS Region | none |
| GitHub Org | `jirihylmar` |
| Project prefix | `aps-pages-installers` — every repo and resource name derives from it |
| Repo naming | product: `aps-pages-installers` or the confirmed product name · justified separate repos: `aps-pages-installers-<part>` · **local folder = repo = origin name, always** |
| Resource naming | `aps-pages-installers-{component}-{service}{version}-{env}-{account}` — holds whether provisioned via CDK or individually |

## Commands

Your commands live in `.claude/commands/` — each `*.md` file is one slash command, with
a one-line `description:` in its frontmatter — and your skills in `.claude/skills/<name>/SKILL.md`
(Codex: `.agents/skills/<name>/SKILL.md`), each with the same `description:` line. **Do not
hardcode a list of commands here; a hand-maintained list goes stale and makes agents reinvent work
that already exists as a skill.** `/start-session` enumerates both live from those directories at
the start of every session, so the authoritative, current list is always the directories
themselves.

**Before building anything, check the live inventory for a command or skill that already
does it and prefer it over ad-hoc work.**

### Centrally distributed payloads — do NOT hand-edit

Five kinds of file arrive from `syndicate-playbooks-examples` via `/distribute-defaults`.
The authoritative set for this project is `.claude/distribution-manifest.json` — a list written
by hand anywhere else will drift. **That file is written by the first `/distribute-defaults` that
reaches this project and by nothing else**: a project bootstrapped by hand from the template has
no manifest until then, and that is expected, not a fault. Until it arrives, the table below is the
authority and `/start-session` § 0.7 reports "no manifest" and moves on.

| Payload | Where | Hand-editable? |
|---|---|---|
| **commands** | `.claude/commands/*.md` | no — extend via an overlay, below |
| **skills** | `.claude/skills/<name>/` (a directory: `SKILL.md` plus its files) | **no overlay mechanism** — single-owner, overwritten on difference |
| **Codex skills** | `.agents/skills/<name>/SKILL.md` | **no overlay mechanism** — single-owner, overwritten on difference; inert for Claude |
| **commit guard** | `.claude/hooks/pre-commit` | no — single-owner, overwritten on difference |
| **project charter** | `PROJECT_CHARTER.md` | no — single-owner, overwritten on difference |

Treat all five as build output.

**Skills (and commands) this project creates** are named `<name>-<code>`, where `<code>` is this project's code,
declared once in `.claude/project-code` (e.g. `corpus-doctor-mt`). The suffix is how a reader
tells this project's own skills from distributed ones; the commit guard refuses a new skill that
does not carry it. Existing skills are not renamed. Rule: `PROJECT_CHARTER.md` § 12.

To extend a default with project-specific behavior, add a splice overlay at:

```
.claude/local-overlays/<command>.md
```

Overlay syntax: a markdown file containing `<!-- splice-before: "ANCHOR" -->`,
`<!-- splice-after: "ANCHOR" -->`, or `<!-- splice-append -->` blocks. Anchors
are whole-line exact matches against the canonical. The overlay is replayed on
top of canonical on every distribution, so additions survive central updates.

To fork a default entirely (when additive splicing isn't enough), list the
filename in `.claude/local-overlays/.skip` — that file will then be owned by
the project and never overwritten.

Direct edits to a distributed default with no overlay or `.skip` entry will
be flagged as `divergent` on the next `/distribute-defaults` run and block
the distribution until resolved.

## Key Files
| File | Purpose | Updates |
|------|---------|---------|
| `progress.json` | Task state - **SINGLE SOURCE OF TRUTH** | Every session |
| `tasks/phase_*.md` | Task implementation details | When tasks added |
| `IMPLEMENTATION_PLAN.md` | Phase-0 origin record: what was intended and approved before implementation opened | Frozen at approval — amending it is an operator decision |
| `session_notes.md` | Session history log | Every session |
| `input/` | Original requirements and input materials | Read-only reference |
| `PROJECT_CHARTER.md` | Executor-neutral delivery contract | Centrally distributed |

`IMPLEMENTATION_PLAN.md` says what was agreed before the work started. `progress.json`, `tasks/`
and this file say what is true now. Where they disagree the tracked record governs and the
specification is not edited to match — the divergence is the history
(`PROJECT_CHARTER.md` § *The specification is an origin record*).

### Input Materials (`input/`)
The `input/` folder contains the original requirements and materials that informed `IMPLEMENTATION_PLAN.md`. During Phase 0, every file in `input/` must be read, every requirement extracted, and every spec section must trace back to input sources. The `input/` folder remains available as read-only reference throughout implementation.

---

## Working Style: Autonomous with Checkpoints

**Work continuously. Do not ask permission for every action.**

```
DO THE WORK → PRESENT RESULTS → GET APPROVAL → CONTINUE
```

### Approval checkpoints — where to pause

| Checkpoint | When | Example |
|------------|------|---------|
| Session start | After `/start-session` status | "Ready to start Task X.Y. Proceed?" |
| Spec approval | Task 0.5 | "Review IMPLEMENTATION_PLAN.md, approve to continue" |
| Major decisions | Architecture, scope, trade-offs | "I recommend approach A over B because…" |
| Irreversible / outward-facing | Deleting data, publishing, anything a third party sees | "This drops the table. Confirm." |

**Those four rows are the whole list.** If a pause is not architectural, not a scope change, and not
irreversible, it is not a checkpoint.

### NOT checkpoints — just do it

- Reading files · searching · inspecting state
- Writing and editing code
- Running builds, tests, linters
- **Git commits, and pushing them to origin**
- Creating directories · installing dependencies
- **Finishing a task and starting the next one.** Completion is *announced*, not asked about:
  "Task X.Y complete, verified. Continuing with X.Z." Then continue.
- **Being unsure about something you can find out.** Two workable approaches with no architectural
  difference is not an escalation — pick the one that fits the surrounding code, say which you
  picked and what you assumed, and keep going. Escalate uncertainty only when it is *architectural*
  (the row above), and then bring the recommendation, not the menu.

```
❌ WRONG — an interruption for each step:
   "Should I read the config file?"   "Can I create the component?"
   "Should I run the tests?"          "Can I commit?"
   "5 commits are unpushed. Want me to push them?"

✓ RIGHT — checkpoint at the boundary, autonomous in between:
   [reads files, writes code, runs tests, commits, pushes]
   "Task 2.3 complete. UserAuth component created, tests passing, pushed.
    Continuing with 2.4: session-token rotation."
```

**A task boundary is not a session boundary.** Updating progress, committing, pushing, or moving
`current_task` is internal bookkeeping during an already-authorized run. After publishing a task,
start the next ready task in the same response unless an approval checkpoint, genuine blocker,
explicit stop request, or exhausted safe work ends the run. Do not emit a turn-ending progress
summary merely because one task closed.

> **Why this section exists, measured.** Nine months of this estate's own conversation history
> (2025-10-21 → 2026-08-05, 14,967 operator prompts across 113 projects) contains **949 agent
> turn-endings across 43 projects that stop and ask permission for a mechanical action** — push
> these commits, deploy, proceed, *"say the word"*, *"still holding the commit and the 8 unpushed
> commits pending your word"*. The rate rose from 5.0 per 100 in 2026-01 to **28.8 in 2026-06**.
> The cause was structural: this template carried no working-style section at all, and across the
> ten distributed commands approval is mentioned 32 times — **every one of them telling the agent
> when to ask, not one saying what needs no asking.** A held commit is not caution; it is work
> that exists on one disk and nowhere else, and an operator interrupted to authorise it.

---

## Session Workflow

### Before Starting
1. Run `/start-session`
2. Verify AWS account matches
3. Check last completed task still works
4. Review context budget

### During Session
- Complete **AT LEAST ONE** task perfectly
- Leave codebase in **deployable state**
- Start every safe independent lane that can finish or reach a declared integration point

### Context Budget
Estimate it. The exact percentage is the operator's to read with `/context`, which no executor
tool can run; use a figure only if the harness shows you one, and say when yours is an estimate:
- **<40%**: Start any task
- **40-60%**: Small/medium tasks only
- **60-80%**: Finish current, then wrap up
- **>80%**: Start no new work — run `/update-progress` and end the session

---

## Progress Rules

**progress.json preserves terminal history.** Every non-terminal task is editable planning state;
terminal tasks are immutable references. Task ids and phase records remain append-only. The full
rule is `/update-progress` § *NEVER Do*, first row.

### ALLOWED:
- Change task `status`
- Add timestamps, artifacts, notes
- Add NEW tasks with sub-IDs (2.3a, 2.3b)
- Refine, combine, divide, reassign, re-scope or relocate any **non-terminal** task so the open-work
  landscape describes what is now required

### NEVER:
- Remove tasks (mark `superseded` instead)
- Rewrite a **terminal** task's scope, outcome, verification or evidence — it is immutable history
  and may be used only as a reference; represent later action in open work
- Change task IDs

### Tasks that arrive from the central estate survey

A task carrying **`estate_notice: <marker>`** was appended by
`syndicate-playbooks-examples` — it was **not** raised by this project. Treat it as follows:

- It is a **request to verify**, not a finding and not a fix. The central repo matched a pattern;
  it does not own these files and cannot know what each line is for. Check every item before
  changing anything — some will be correct exactly as they stand.
- **The body is in the task's `detail`.** `/open-work` renders `id`/`name`/`status` only, so read
  the task itself.
- **Do not remove the `estate_notice` key.** It is what makes re-notification a no-op; tidy it away
  and the next central run appends a second copy. The text may legitimately be **replaced in
  place** under the same task id if the central rule is corrected.
- **To decline** central changes for a given check, list its probe name (or `*`) in
  `.claude/estate-align.skip`, one per line. It must exist **before** delivery. A refusal is
  reported as REFUSED and is never overridden — but note that once a notice is committed here,
  this project's own `progress-check` will block removing the task, so decline up front rather
  than deleting after the fact.

---

## Git Discipline

**Commits**: After completing each task.

**Pushes**: At meaningful boundaries, not after every commit.
- After completing a phase
- Before ending a session
- When sharing/debugging

---

## Task Sizing

Before adding task to progress.json:
- [ ] Single deliverable (one sentence)?
- [ ] Verifiable (one command/action)?
- [ ] Does its boundary follow one verifiable outcome rather than an arbitrary file count?
- [ ] Deployable state after completion?

**If any NO → break it down further**

---

## Critical Rules

### 1. AWS Account Verification
This project uses no AWS today. If it ever needs AWS, record the account and region in Quick
Reference first; until then no AWS operation belongs to this project. Before any AWS operation,
resolve the AWS handle as `/check-aws` Step 2 does and verify the account number it returns.

The handle is not written here, and neither is a profile name: both are nicknames, true on one
machine only, and this file travels to every host (`/start-session` § Two Environments).

### 2. Use the AWS connection
```bash
# BEST - the MCP connection, called the way /check-aws Step 2 resolved it on this host
{handle} aws s3 ls

# OK - the local aws CLI, only where /check-aws Step 10 or /start-session § Two Environments says
# so, with a profile that `aws sts get-caller-identity --profile <p>` proves is this account
aws s3 ls --profile <p>

# WRONG - Never do
export AWS_PROFILE=...
```

### 3. Pre-Work Verification
Before starting NEW work:
1. Find last `complete` task in progress.json
2. Run its `verify` step
3. If FAILS → fix before proceeding

### 4. Context Management
Estimate context used before significant work (the exact percentage is the operator's to read with
`/context`). If it is running low:
1. Run `/update-progress`
2. Update `session_notes.md`
3. Commit all changes
4. End session

### 5. Verify Against Real Data
Before marking tasks complete:
- Run operations against **real data**, not just test fixtures
- When task involves multiple components, verify **each one**
- Don't mark phase complete until all components verified

### 6. Use Project Methods
```
❌ WRONG: Create ad-hoc files (like .claude/plans/) for planning
✓ RIGHT: Use established files: progress.json and tasks/ — planning done
         during implementation lands there, never back in the Phase-0 spec
```

### 7. No Virtual Environments
```bash
# WRONG - Breaks Lambda packaging
python -m venv venv

# RIGHT - Direct install
pip3 install package
```

### 8. Infrastructure Changes Through IaC Only
```bash
# WRONG - Direct AWS modifications cause drift
aws lambda update-function-code ...
aws s3api put-bucket-policy ...

# RIGHT - All changes through CDK/Terraform
npx cdk deploy
terraform apply
```

Never modify AWS resources directly via CLI/console - IaC is the only source of truth.

### 9. Content Discipline (Grounding + Naming)

**Grounding-at-touch**: when editing any skill or canonical doc, verify the operational claims in
the sections you touch against the actual implementation — cited paths resolve, CLI flags exist in
the tool's argument parser, deployed-resource names match a fresh inventory, documented commands
are runnable as written. An edit that leaves a touched claim unverified is incomplete work
(enforced at `/update-progress` Step 2a). In addition, EVERY session close grounds one rotating
file from the standing backlog (`/update-progress` Step 2b); `/repo-hygiene` is the periodic
consolidation pass (triggered by the hygiene clock — due at 30d, blocking at 60d), whose first run
manually baselines the rotation and which then catches up whatever the session cadence missed.

**Naming**: if the project has a terminology registry (commonly `docs/terminology.md`), use its
canonical names in all new/edited content — no new synonyms, no banned bare words; renames go
through the registry first. The test: one keyword must let a human's search and an agent's grep
land on ALL and ONLY the relevant places.

**De-phased canon**: phase/task/session numbers are process metadata — they belong in
progress.json, session notes, and archives, never as load-bearing content in canonical docs
or skills.

### 10. VPN and SSH Are Provided Centrally

Set by the operator, 2026-10-12. Private networks (VPN) and SSH hosts are provided machine-wide by
the operator. A project reaches them only through the host definitions the machine provides. It
never starts its own VPN client, never uses passwords or sshpass, never copies SSH or VPN keys
between machines, and never disables host-key checking. SSH logins use the keys the operator
provides. The operator places VPN and SSH credentials in the machine's own configuration; a project
never reads, copies or creates them. When a connection fails (a timeout, an unknown or changed host
key, a refused login, VPN down), that item waits for the operator and other work continues. This
rule does not bind the repository whose work is providing them.

**If this project reaches the VSB servers** (agreed 2026-10-16, replaced 2026-10-19 and 2026-10-21):
vsb-nutritech and vsb-rss (Ubuntu 26.04, 16 vCPU with AVX2/AVX-512, 64 GB RAM, user hylmarj) are the
operator's member hosts: projects may live and run there, in /home/hylmarj. Which project goes on
which VM is the operator's decision. They are operated from the operator's workstation over VSB's
school VPN, which the operator connects. Reach them with `ssh vsb-nutritech '<cmd>'` and
`ssh vsb-rss '<cmd>'`; scp and rsync use the same aliases. A project never connects that VPN or any
other VPN client, never runs any `hyl-vpn` command, and never uses another route or raw addresses.
On `connect ... timed out` the VPN is not connected: stop and tell the operator. sudo for host setup
is authorised (for example linger, git identity, Node 24, Docker, gh, AWS CLI, Claude Code, Codex).
VSB IT keeps the SSH daemon settings and its admin account: never change sshd, the firewall, user
accounts or VSB's automatic updates. /data is VSB's shared storage, used by others and writable by
every account: it is not a workspace and holds no secrets, so no project, .env, key or token goes
there. A project placed on a VM brings its own .env and only its own AWS profile. Never use sshpass,
stored passwords, `StrictHostKeyChecking=no` or other accounts. On `Host key verification failed` or
`Permission denied`, stop and tell the operator. Still gone: bessie, abbie, `ssh vsb-dbtstorage2`,
`ssh vsb-abbie` and the forwards 127.0.0.1:15432 and 127.0.0.1:8787. MITT is not available to
projects.

### 11. Sign-in Comes From Central Access

Agreed 2026-10-19; scope added 2026-10-21.

**Scope.** This rule is for the operator's internal apps: development tools, dashboards,
project-management and operations pages, apps whose users are the operator's own people. It does
not apply to customer-facing products with their own user ecosystem (their own customer accounts,
mobile apps, Sign in with Apple or other providers): those keep and build the sign-in they need,
and nothing here migrates them. An app without a login needs nothing from this rule until it gets
one. If an app with a login, or about to get one, is not clearly one kind or the other, ask the
operator once and record the answer next to this rule.

Every internal app with a login signs in the same way: Google and an emailed code, on the app's
own sign-in page ("Continue with Google" and an email field). Do not build anything else: no
password form, no user pool of its own, no shared or basic-auth password, no allow-list in code.

- To join, send the onboarding request to the operator in one line, or, when the central access
  session has already messaged this one, as a reply to it. Fields: app name and proposed app id;
  who uses it (the operator's own people); repo and the branch that deploys production; AWS
  account and Region; framework and rendering (single-page or server-rendered); pages and the roles
  each needs; who should sign in (or "the operator decides"); sender domain wanted (or "the
  default"); what guards the app today; this session's name.
- Register the owner-side tasks you receive through /add-work. Once the operator has scheduled the
  join (the owner-side tasks arrive from the central access session), these need no further word
  from the operator in this project: registering those tasks, merging the delivery pull request,
  integrating and deploying behind the old guard, the proof, and removing the old guard on
  central's go. Everything else follows this project's own checkpoints. The join package arrives
  as a pull request in this repository: merge it with a merge commit, record
  vendor/hyl-access-kit/, docs/central-access/ and .claude/skills/access-* as delivered and not
  hand-editable, and follow its guide and the skills /access-integrate and /access-maintain.
- Defaults, not questions: no support address; demo mode, if the app has one, comes before the
  session check and is guarded by a test that production never sets it.
- Keep the old guard until central access sends its go. Never record a listed address in tracked
  files.
- An internal app that already has its own login keeps it until the operator schedules the join;
  do not migrate it yourself.

### 12. No Credential in Served or Published Code

Agreed 2026-10-16. No credential in any file a browser can fetch or that gets published:
`public/`, static or docs site output, client bundles, committed docs or notes. This covers AWS
keys, API keys (Anthropic included), tokens, passwords, and connection strings that contain
passwords. Browser code gets no AWS credentials; it calls a backend or uses the app's sign-in.
Backends and scripts read AWS credentials from the default credential chain (the runtime's role, or
a profile chosen outside the code), never from literals or env files in the repository. A project
never creates, copies or rotates an API key; it asks the operator. If you find a credential in
tracked or served files, stop and tell the operator at once. Rotation comes first: deleting the
value alone fixes nothing, because it stays in git history and on the live site.

---

## Tool Preferences

| Task | Use | Not |
|------|-----|-----|
| Read files | `Read` | `cat` |
| Edit files | `Edit` | `sed` |
| Search files | `Glob`/`Grep` | `find`/`grep` |
| AWS operations | MCP tools | bash aws |
