---
name: server-report
description: Report the capacity and usage of the host this session is running on, attributed per project and Claude/Codex executor session — CPU, RAM, swap, disk, OOM kills and MCP process sprawl — and name the binding constraint. Works on any host by probing rather than assuming. Invoke for machine usage, capacity, load, resource consumers, session headroom, or kill diagnosis.
---

# server-report

On-demand capacity report for **the host this session is running on** — whatever that host is.

## The design rule

> **Resolve by probing. Never identify the host and look up its rule.**

An `if-EC2-elif-WSL` branch is just a longer hardcoded list: silently wrong on the first host nobody
thought of. Where a probe genuinely cannot resolve a value, this skill says **"unknown"** rather than
guessing — because the failure class it exists to avoid is code that **succeeds wrongly and reports
success**. A wrong confident number is worse than no number.

Nothing about capacity is hardcoded. Every run reads the current host live, so it self-adjusts across
a resize, a move to a different machine, or a run inside a container, with no edits.

The unit of usage is **the work that generates it**: each Claude or Codex session, labelled by
executor and project/repo working directory, plus every process it spawns. Projects can span
multiple AWS accounts, so accounts are not the grouping key.

## Procedure

```
python3 ${CLAUDE_SKILL_DIR}/report.py            # capacity + per-project attribution
python3 ${CLAUDE_SKILL_DIR}/report.py --sample=5 # longer CPU window (default 2s)
python3 ${CLAUDE_SKILL_DIR}/report.py --az       # additionally resolve the cloud AZ (see below)
```

`${CLAUDE_SKILL_DIR}` resolves to this skill's own directory wherever it is installed — user-level,
project-level, or in a plugin. **Never hardcode a path to `report.py`**: an earlier version of this
file said `~/.claude/skills/server-report/report.py`, which breaks in a project checkout and, worse,
silently runs a *stale* copy on a host where that path happens to exist.

The script reads `/proc`, `/sys` and cgroup files directly — no sudo, no third-party dependencies.
It shells out only for the OOM detail sources (`dmesg`, `journalctl -k`), both local and both
optional. It touches the network in exactly one place: `imds_az()` under `--az`, which the code
labels *"the only probe permitted to touch the network"* — off by default, and gated on the firmware
declaring the vendor.

## What it reports

**Capacity** — CPU, RAM, swap, disk, each with `OK` / `WATCH` / `FULL` (CPU 70/90, RAM 75/90, disk
80/90 — the thresholds are the `flag()` calls in `main()`).

Two renderings carry the honesty:

| Rendering | Meaning |
|---|---|
| `= 8.00 cores` / `23G` | The ceiling is exact — this host's cgroup root is the kernel's true root |
| `<= 1.50 cores` / `<= 512M` | **An upper bound.** Ancestors above this cgroup namespace are invisible and may impose a lower limit |

**OOM kills** — two independent counters, then every readable detail source **merged** (never
ranked-and-stopped), each labelled with **its own** window. Sources disagree legitimately: a ring
buffer is wiped by a restart, a journal starts at boot, `kern.log` spans weeks. "No kills found" is
never printed as fact when a source was unreadable — `dmesg` restricted, or a counter absent, means
*unknown*, not zero.

**Usage by project and executor** — Claude/Codex, sessions, procs, MCP procs, CPU%, memory, %RAM. Below it, `unattributed
processes` (**measured**, not inferred), and a residual checked against independently measured kernel
accounting.

**Binding constraint** — which resource is closest to full, and the **heaviest** session. It does not
estimate "N more sessions fit": that divides free RAM by a *mean*, and the measured failures on this
estate were single sessions ~14× the mean. On a bounded or unverified ceiling it withholds the
estimate entirely rather than print a guess wearing a number.

## What this skill will not tell you, and why

Honest gaps are the point. Each is reported identically on **every** host, so none is a hidden host
check:

| Gap | Why |
|---|---|
| **Sustained CPU ceiling** on a burstable instance | The credit balance is not exposed to the guest. Only `steal` is observable, and only once you are already being throttled. |
| **Whether free disk is real** | Thin provisioning (vhdx, qcow2, VMDK thin, LVM thin, overlay) means the backing store may not honour reported free space, and no probe resolves the real ceiling from inside. So `free` carries provenance — `KNOWN THIN` / `UNKNOWN` — and **absence of the attribute is never read as "thick"**. The `used%` flag still fires: how full the filesystem is *is* measured. |
| **A kill enforced above the guest** | A hypervisor or host OS reclaim leaves no trace in `vmstat`, `memory.events`, `dmesg` or `kern.log`. So zero renders as **"none recorded by this kernel"**, never "you were not killed". |
| **The cloud AZ** | Requires the cloud's proprietary metadata endpoint. `--az` only, gated on the firmware declaring the vendor, and **off by default even then** — DMI already yields instance id and type without touching the network. |

## Corrections — claims this file used to make that were false

Recorded because they are instructive, and because the next reader deserves to know the
documentation was once wrong about its own code. Full evidence: `VERIFICATION-2026-07-16.md`.

- ~~*"mem sums EXACTLY to RAM used"*~~ / ~~*"the table never shows a contradicting number"*~~ —
  **a tautology.** `other` was defined as the remainder, so the rows reconciled *by construction* and
  the claim could not be false. Injecting a 500M error, or deleting every session root, still printed
  *"every row reconciles"*. The residual is now checked against independently measured kernel
  accounting, and a coverage check names any session the root-finder missed. Exactness is not
  achievable at all: `used` is `MemTotal − MemAvailable`, and **MemAvailable is a kernel heuristic**.
- ~~*"the 1-min load average is deliberately not shown, because utilization needs no
  interpretation"*~~ — the replacement was **3× worse in the opposite direction**. Summing per-pid
  deltas loses processes that exit mid-window (i.e. exactly what a Claude session does), reading
  3.375% against the `/proc/stat` aggregate's 10.130% — printing `OK` while the cores were busy. The
  host total now comes from the aggregate; per-pid rows are **attribution only**.
- ~~*"MCP procs"* counted by the substring `mcp`~~ — over-counted **2×** and false-positived bash
  wrappers and `ssh`. Now structural: an MCP server speaks JSON-RPC over stdio, so fd0 **and** fd1 are
  both a socket or a pipe.
- ~~*"the remote MCP dev access point"*~~ — a nickname true on one machine, in a file that ships to
  many. Identity is now a *rendering* of what the firmware declares, never a gate.

## Tuning notes

- **Thresholds:** the `flag()` calls in `main()`.
- **The visibility gate:** `visibility()` — one `stat()` of `/sys/fs/cgroup/cgroup.type`. This is the
  load-bearing probe. Test `cgroup.type`, **not** `memory.max`: `cgroup.type` is
  controller-independent, whereas an absent `memory.max` is ambiguous (true root vs. `memory` not in
  the parent's `subtree_control`).
- **Untested surfaces**, honestly: cgroup **v1** (the layout differs and is not exercised — the code
  says so and degrades to unverified), k8s pods, LXC/podman/nspawn, bare metal, non-AWS clouds.
  Measured on: WSL2, an EC2 `t3.large`, and Docker containers with both private and host cgroup
  namespaces.

## What is left on this machine (`leftovers.py`)

A second, separate helper in this directory, run by `/start-session` Step 2.9a and `/update-progress` Step 9c:
`python3 .claude/skills/server-report/leftovers.py`. On a member host (the machine whose `~/.claude/CLAUDE.md` or
`~/.codex/AGENTS.md` opens with the heading `config/member-host/claude-global.md` gives it; never by a host name) it prints
one `LEFTOVERS:` line: the non-dot entries at the top of the home folder that are not git repositories, and this account's
entries directly under `/tmp`, each with a count and a few names, bounded by timeouts. Everywhere else, and when there is
nothing, it prints nothing. It reports and nothing more: it deletes nothing, always exits 0 (with stdout closed, and with a
`LEFTOVERS_*` setting that is not a number, which falls back to its default), and does not say whose an entry is. The
harness's and tmux's own per-account folders and the two tool caches every session leaves there are not in that list (its
docstring names them, as measured on 2026-11-10), so the line means something when it appears.

The line also measures this account's session scratchpads, which the harness keeps under `/tmp/claude-<uid>` (one folder
per session, `<project folder>/<session id>/`) and leaves behind when a session ends; old clones there filled
nutritech-pdsm-orchestrator's `/tmp` quota with 9.5 GB. It reads, for example,
`/tmp/claude-1001 session scratchpads: 412 MB, 3 folders of other sessions over 1 MB untouched for a day`: the size of
everything under `/tmp/claude-<uid>`, and, when the environment names the session (`CLAUDE_CODE_SESSION_ID`), how many
folders of other sessions hold over 1 MB with nothing in them changed for 24 hours and their session's transcript as
quiet. It appears only when the total is over 300 MB or such a folder exists, so a normal session stays silent: the other
projects' live sessions are not old, and the empty folders ended sessions leave hold nothing. Without the session id (a
Codex session, for one) it gives the total alone, over 300 MB. It names no folder. Test:
`scripts/test-session-leftovers.sh`.

## Related

- **AWS account EC2 vCPU quotas** — a different question ("can this *account* launch another
  instance"): `list-service-quotas --service-code ec2` filtered to `L-1216C47A`, per account.
- **Scheduling:** `/schedule` for a persistent cron, or `/loop <interval> /server-report` in-session.
