---
name: operations-check
description: Check the entry document's Operate and Rebuild section (CLAUDE.md, or AGENTS.md where there is no CLAUDE.md) against git - each of its six rows (runs without a session, health, operating notes, rebuild on another host, builds and how long, where agents take part) names a file git holds, and any heading it cites in that file, or says not built yet, or none with a reason, and none names a host path - and count how far progress.json has adopted the phase operations statement and the ops record. Invoke after a task that touched something that runs, when writing or changing the Operate and Rebuild section, and when /repo-hygiene names it.
---

# operations-check

What a project runs should be kept going with few tokens and rebuilt from git on any host. The rule
has one home, `PROJECT_CHARTER.md` § 8, *Token-heavy development, token-light operation*, and this
skill does not restate it. It reads the section of the entry document where a maintenance session
starts, `## Operate and Rebuild`, checks each row against what git holds, and counts how far
`progress.json` has taken the rule up.

## Why it exists

The operator asked on 2026-11-08 that what a project runs cost few tokens to keep going and be
rebuildable from git on any host, and that the rule arrive by new work rather than by refactoring
what exists; the words are quoted beside the rule in the charter. The same day the operator asked
that each project also write down what it builds, where, and how long each step takes, because
shells were seen running for a long time with no one knowing why, and where AI agents take part and
how much. A section that names files is only a cheap starting point while the files, and the
headings it cites in them, exist, so the one thing a checker can hold is that every file a row
names is one git has and every heading it cites is one that file has.

## The section

A new project's entry document carries it from the template, exactly this:

```markdown
## Operate and Rebuild

How what this project runs is kept going with few tokens, and rebuilt from git on any host
(`PROJECT_CHARTER.md` § 8, *Token-heavy development, token-light operation*). Each row names the
committed file that does it, or says `not built yet` or `none: <reason>`.

| What | Where |
|---|---|
| Runs without a session | not built yet |
| Health | not built yet |
| Operating notes | not built yet |
| Rebuild on another host | not built yet |
| Builds and how long | not built yet |
| Where agents take part | not built yet |
```

| Row | What it names |
|---|---|
| Runs without a session | The committed timers, scheduled jobs or pipelines that do the routine work, so no recurring agent session does it. |
| Health | One committed command that reads the running system and exits non-zero on a problem. |
| Operating notes | Where what to do about each problem met so far is written. |
| Rebuild on another host | The documented path by which a clean clone on a new host, given only the credentials and access hyl-resources-manager issues, builds and deploys it. |
| Builds and how long | Where each build, test and deploy step is listed with where it runs, its command, how long it takes as measured, and the bound past which it is stopped and investigated. Typically `README.md` § Builds and how long. |
| Where agents take part | Where it is written which work an AI agent does (development sessions, operation on demand, any model call in the product itself) and how much. Typically `README.md` § Where agents take part. |

The entry document is `CLAUDE.md`, or `AGENTS.md` where the project has no `CLAUDE.md`, and its
section is the one that decides whether the run is complete. Either file that has the section is
checked, and the report says which (`entry` marks the one that decides). Two cases are noted and
never change the exit code: `section-in-agents`, when the section is only in `AGENTS.md` although
the project has a `CLAUDE.md` (the `AGENTS.md` section decides until it is moved), and
`two-entry-sections`, when both have it (`CLAUDE.md`'s decides; a false claim in the second copy
still counts, its completeness does not). A part that keeps running, and
that a task touched, gets its rows filled by that task (`/update-progress` Step 7a).

## Run it

```bash
python3 .claude/skills/operations-check/operations_check.py                  # the working tree and the index
python3 .claude/skills/operations-check/operations_check.py --rev origin/main # one commit's tree
python3 .claude/skills/operations-check/operations_check.py --since 2026-11-08T12:00:00Z
python3 .claude/skills/operations-check/operations_check.py --json -C <dir>   # one JSON object, another checkout
```

The text output is one summary line, one line per row (`<doc>  <row>  <STATUS>  <detail>`), a
`note` line for anything else it noticed, and `record` lines for the counts.

| Exit | Meaning |
|---|---|
| `0` | Every checked section is complete (all six rows `NAMED` or `NONE`), and nothing written is false. |
| `1` | **claims-missing**: a row names a file git does not hold, a heading that file does not have, or a host path. Something written is false. |
| `3` | Not complete yet, nothing false: no entry document has the section (`no-section`), or a row is `NOT-BUILT-YET`, `UNVERIFIED`, `EMPTY` or `ABSENT` (`partial`). |
| `2` | Could not check: not a git repository, an unknown revision, a file that could not be read (a blob a partial clone could not fetch, or a fetch stopped at its bound), a defect in the checker (one line, `operations-check: cannot check: <error>`). **Never read as clean.** |

`1` wins over `3`. An unreadable or unparseable `progress.json`, or one tracked as a symlink, is exit
`2` when a claim's verdict depends on the member directories it declares: a claim git does not hold
might be a member's, so it is not judged false but listed as `elsewhere` (the row reads
`UNVERIFIED`), and `progress.json` is named as unread. A `.md` file a row refers to by heading that
cannot be read is exit `2` as well.

## Row statuses, and what to do about each

| Status | What it found | What to do |
|---|---|---|
| `NAMED` | At least one path claim, and git holds every one this repository can check. | Nothing. |
| `NONE` | `none: <reason>`, with a reason. | Nothing. The reason is the record that the project has no such part. |
| `NOT-BUILT-YET` | `not built yet`, with a trailing period or without. | Nothing now. The task that builds the part names its file. |
| `UNVERIFIED` | Text with no path this checker can confirm: `make health`, a sentence, or only claims inside a member repository. | Name the committed file in its own backticks, for example `scripts/health.sh`. |
| `EMPTY` | An empty cell, a bare `none`, or `none:` with no reason. | Name the file, or say `not built yet`, or give the reason after `none:`. |
| `MISSING-PATH` | A path claim git does not hold: a typo, a file never committed, a gitignored file, a file at another path. The detail says whether the file is in the working tree, and names a tracked file of the same name when there is one. Also a `<file>.md` § `<heading>` reference whose file has no such heading, listed as `README.md § Builds and how long`. | Commit the file, correct the path (from the repository root) or the heading, write the heading into the file, or say `not built yet`. |
| `HOST-PATH` | A path claim starting with `/` or `~`: a location on one host, which a clean clone on another host does not have (`PROJECT_CHARTER.md` § 8). | Name the committed file that puts it there, and let the host location resolve at runtime. |
| `ABSENT` | The row is not in the section. | Add the row, with `not built yet` if nothing is built. |

**The section verdict** is `claims-missing` when any row is `MISSING-PATH` or `HOST-PATH`,
`complete` when all six rows are `NAMED` or `NONE`, and `partial` otherwise. The run's verdict is
`claims-missing` when any section checked says something false, otherwise the entry document's
section's, and `no-section` when there is none.

## What counts as a path claim

Only backticked spans are read. For each one:

1. its first whitespace-separated word is taken, and a trailing `#anchor` or `:<line>` is dropped
   (`ops/runbook.md#disk-full`, `scripts/health.sh:12`);
2. it is a claim when it holds a `/` or ends in an extension that has a letter in it (`.sh`, `.md`,
   `.timer`, `.env`, but not the `.11` of `python3.11`), and it is not an identifier (below);
3. a leading `./` is dropped. A claim starting with `~`, or with `/` and a host directory (`/home`,
   `/etc`, `/var`, `/opt`, `/srv`, `/usr`, `/tmp`, `/mnt`, `/Users` and the like), is a host path;
4. any other claim must be held by git: a tracked file, a tracked directory (`infra/systemd/`), or a
   glob that matches at least one tracked path (`infra/systemd/*.timer`). With `--rev` the commit's
   tree is read; otherwise the index (`git ls-files`), so a staged file counts;
5. a claim git holds that ends in `.md` and is followed, after optional blanks, by `§ <heading>`
   is a **heading reference**. The heading runs to the end of the cell, the next backtick, `;` or
   `,`, and its surrounding `*` or `_` and a trailing period are dropped. The file, in the same
   tree (the commit with `--rev`, otherwise the working tree), must have a heading of any level
   (`#` to `######`, outside a fenced block) whose text equals it without case, once trailing `#`s,
   blanks, `*` and backticks are dropped. A reference that starts with a section number (`§ 8`,
   `§ 11 *Unattended operations*`) also matches a heading that starts with that number (`## 8. ...`)
   or whose text is what follows the number, so a citation of the charter by its section holds. A
   file that is not `.md`, a directory or a glob is never read for headings.

**Identifiers are not path claims.** The rebuild path names secrets by their stable identifier
(`PROJECT_CHARTER.md` § 8), and identifiers look like paths, so none of these is read as one, and
none is ever false:
- a word that starts with `-`, `$`, `@` or `http`, or holds `://`, any other `:`, or `@`: a flag, a
  variable, a URL, an ARN (`arn:aws:secretsmanager:<region>:<account>:secret:<name>`),
  `git@<host>:<org>/<repo>`, an image and its tag (`ghcr.io/<org>/<app>:1.4`), a scoped package;
- a `:<digits>` after a name with no extension, which is an image's tag, not a line (`<org>/<app>:16`);
- a word starting with `/` whose first segment is not a host directory: an SSM parameter name
  (`/<project>/prod/api-key`);
- a word whose first segment holds a dot, does not start with one, and is not in the tree: a
  registry or host name (`ghcr.io/...`, `docker.io/...`, `github.com/...`);
- any span written right after a kind word: *secret*, *parameter*, *image*, *key*, *ARN*, *role*,
  *bucket*, *token*, *identifier*, *profile* or *registry*, optionally followed by *name*, *named*,
  *called* or *id* (``the secret `<project>/prod/db` ``). A secret name with no dot, colon or leading
  slash needs that word, or it is read as a repository path.

Because only the first word is read, `` `bash scripts/health.sh` `` is `UNVERIFIED`: the claim is
`bash`. Write the file in its own span. A span that starts with a command is how a row says how to
run something, and the words after the command are often a unit name or an argument that is no
file in the repository, so they are never read as claims.

**Member repositories.** A claim under a directory `progress.json` declares for another repository
(a `git_repos` entry's `local`, `path` or `local_path`, a `relations` member's `path`, or a tracked
submodule) that this repository does not hold is not false. Without `--rev`, when that member's
checkout is in the working tree, the claim is checked in the member's own `git ls-files`, and is
`MISSING-PATH` if the member does not hold it either. Otherwise it is listed as `elsewhere`, not
checked from here, and counts toward neither `NAMED` nor `MISSING-PATH`. When `progress.json` cannot
be read or parsed, or is a symlink, the member directories are unknown: every claim git does not
hold is then `elsewhere` as well, and the run is exit `2`.

**Where the section is.** It starts at the line `## Operate and Rebuild` (trailing blanks allowed)
and runs to the next heading of level 1 or 2, or the end. A heading inside a fenced code block is
not the section, so a document that quotes the format, as this one does, does not have it. A second
section in one document is a `note`; the first is checked. Rows are the data rows of the tables in
the section; labels are matched without case, `*`, backticks and extra blanks; a row that is not one
of the six is a `note` and ignored. A `|` inside a code span does not split a cell. An entry
document that is a symlink is not read (the file it points to is, if it is the other entry
document), and one that git does not track is a `note`, because a clean clone would not have it.

## The adoption record

From `progress.json` (the same commit with `--rev`, otherwise the working tree):

| Count | What it is |
|---|---|
| `phases` | Every phase, whether `phases` is an object or a list. |
| `phases_with_operations` | Phases whose `operations` is a non-empty string. |
| `phases_operations_none` | Of those, the ones that start with `none:`. |
| `terminal_tasks` | Tasks whose status is terminal, in the vocabulary `progress-check` uses (complete, closed, superseded, dropped, cancelled and their spellings). |
| `terminal_tasks_with_ops` | Of those, the ones whose `verify_result` or `notes` holds the word `ops:`, the record `/update-progress` Step 7a leaves. |

With `--since <instant>` (a zoned UTC instant, `2026-11-08T12:00:00Z`) the same counts are given
again for phases whose `started_at` or `created_at` is at or after it, and for terminal tasks whose
`completed_at` is (or `completed`, where there is no `completed_at`, as `progress-check` reads it). A
value that cannot be placed either side of the instant is counted apart as `phases_unplaceable` or
`tasks_unplaceable`, never read as earlier: a date, or a time with no zone, on the instant's own day,
and a stamp that is malformed (`TBD`, `unknown`) or impossible (`2026-11-31`). A field that is
absent or `null` is nothing to place. An absent `progress.json` is `state: absent` and an unparseable one is
`state: unparseable`, with every count `null`: never zero. The counts are a rate to read over time,
never a verdict on one project, and they never change the exit code.

## JSON

`--json` gives one object: `complete_read` (false whenever something could not be read), `rev`,
`commit`, `source`, `entry_docs` (each with `doc`, `present`, `tracked`, `link`, `has_section`),
`sections` (each with `doc`, `verdict`, `entry`, `extra_rows` and `rows`, each row with `label`, `status`,
`value`, `paths`, `missing`, `host_paths`, `elsewhere`), `verdict`, `record` (`state`, `error`, the
counts, and `since`), `findings` (each with `kind`, one of `missing-path`, `missing-heading`,
`host-path`, `extra-row`, `duplicate-row`, `duplicate-section`, `symlink`, `untracked-doc`,
`section-in-agents`, `two-entry-sections`, and `doc`, `row`, `path`, `message`) and `unreadable`. On exit `2` before anything was read it is `{"error", "rev",
"complete_read": false}`.

## Who runs it

- **`/update-progress` Step 7a**, after a task that touched something that runs: the task fills
  that part's rows with what it established, then runs the checker and corrects any row it reports
  `MISSING-PATH` or `HOST-PATH`.
- **`/repo-hygiene`** runs it once and gives the verdict in its pass report. It corrects a row the
  checker reports `MISSING-PATH` or `HOST-PATH`, and never opens work for the rest.
- **The estate baseline** reads every project's origin `HEAD`, not the checkouts on the hosts:

  ```bash
  git clone --filter=blob:none --no-checkout --depth 1 <origin> <dir>
  python3 -I .claude/skills/operations-check/operations_check.py -C <dir> --rev HEAD --json --since <instant>
  ```

  Only `CLAUDE.md`, `AGENTS.md` and `progress.json` are read, and the ones the clone lacks are
  fetched in **one** fetch, then the `.md` files the rows refer to by heading in **one** more,
  only when there are any; nothing is fetched lazily. Each fetch runs in its own process group
  under a bound, `OPERATIONS_CHECK_FETCH_TIMEOUT` seconds (60 by default), and the whole group is
  killed when it fires. An unreachable or stalled origin is exit `2`, with the files named.

## What it never does

- **It never judges prose**: whether the operating notes are good, or the health command checks the
  right thing.
- **It never proves a rebuild.** A rebuild path is evidence only once a clean clone has followed
  it (`PROJECT_CHARTER.md` § 10, *Verify reality*). A row that names `REBUILD.md` says the
  document exists, nothing more.
- **It never creates work, sends a notice or writes a file.** It reads git: the entry documents,
  `progress.json`, and the `.md` files a row cites by heading.
- **An existing project without the section is in a counted state, not in defect.** An existing
  system is not refactored to comply; a task that touches a running part fills that part's rows.
  `no-section` and `partial` are exit `3` for that reason, and only a false claim is exit `1`.

## Related skills

- `/progress-check`: refuses a new phase without its `operations` statement at commit time.
- `/docs-check`: the same idea for `docs/`, where the operating notes usually live.
- `/unattended-check`: whether an operation is actually being watched, which is what the *Runs
  without a session* row promises.
