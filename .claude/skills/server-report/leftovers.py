#!/usr/bin/env python3
"""leftovers.py - what is left on this member host, as one line for the session's report.

Called by /start-session Step 2.9a and /update-progress Step 9c (SESSION_CLOSE). On a member host it lists three things and
says nothing else: the non-dot entries at the top of the home folder that are not git repositories; this account's entries
directly under /tmp, each with a count and a few names; and this account's session scratchpads under /tmp/claude-<uid>, as
their size and how many old folders of other sessions sit there (below). It reports and nothing more: it deletes nothing,
it never fails a session (always exit 0, with stdout closed and with a setting that is not a number too), it prints nothing
when there is nothing, and it does not say whose an entry is.

ONLY ON A MEMBER HOST. A member host is the machine whose ~/.claude/CLAUDE.md or ~/.codex/AGENTS.md opens with the heading
config/member-host/claude-global.md gives it: the file member-host-prepare.sh installs, read here by its first line and
never by a host name. Everywhere else this is silent, including when it cannot tell.

WHAT IS NOT COUNTED in the /tmp list: what is there for every session, on every member host, whatever the work: this
account's claude-<uid> (the harness's scratchpad root, which has its own part below), tmux-<uid> (the socket of the tmux the
sessions run in) and cc-daemon-<uid> (the harness's daemon socket), and the two caches the tools themselves keep there
(node-compile-cache, aws_crt_cross_process_lock), which are named exactly and measured on the two member hosts on
2026-11-10. Without this every session on every member host would print the same line for ever, and a line that never
changes is read as noise. A new tool's own folder simply shows up in the list.

THE SESSION SCRATCHPADS. The harness gives each session a folder /tmp/claude-<uid>/<project folder>/<session id>/ (the
scratchpad and its tasks' output) and leaves it there when the session ends. nutritech-pdsm-orchestrator reported 9.5 GB of
old clones in such folders filling this account's /tmp quota (2026-11-10). This part gives the size of everything under
/tmp/claude-<uid> and, when the environment names this session (CLAUDE_CODE_SESSION_ID), how many folders of OTHER sessions
are old: holding over 1 MB, nothing in them changed for 24 hours, and that session's transcript not written for as long.
It appears only when the total is over 300 MB or such a folder exists. A normal session stays silent: the live sessions of
the other projects beside it are not old, and the empty folders every ended session leaves hold nothing. Without the
session id it gives the total only, and only over 300 MB. It names no folder, so it does not say whose one is.

Bounded: each find has a timeout, the whole run has an alarm, and a list it could not read says NOT CHECKED, never nothing
(unknown is not "none").

  python3 .claude/skills/server-report/leftovers.py            # from the project root
  python3 .claude/skills/server-report/leftovers.py --tmp DIR  # the test's fixture instead of /tmp
"""
import math
import os
import signal
import subprocess
import sys
import time

MEMBER_HOST_HEADING = "# Global conventions — a syndicate member host"
GLOBAL_FILES = (".claude/CLAUDE.md", ".codex/AGENTS.md")
NAMES_SHOWN = 5
NAME_MAX = 60
MB = 1024 * 1024
OLD_FOLDER_OVER = 1 * MB                     # an old folder holds more than this
OLD_AFTER = 24 * 3600                        # ...and nothing in it, nor its session's transcript, changed for this long


def number(name, default, most=float("inf")):
    """A positive number from the environment, at most `most`. Unset, empty, not a number, zero or less: the default."""
    try:
        value = float(os.environ.get(name, ""))
    except ValueError:
        return default
    return min(value, most) if 0 < value < float("inf") else default


FIND_TIMEOUT = number("LEFTOVERS_FIND_TIMEOUT", 8, 3600)      # a timeout over an hour is held at an hour: the
WHOLE_TIMEOUT = number("LEFTOVERS_WHOLE_TIMEOUT", 20, 3600)    # alarm and the find take no larger value
SCRATCH_SHOWN_OVER = number("LEFTOVERS_SCRATCH_MB", 300) * MB
RUNNING = []                                 # the find in progress, so the alarm can stop it too


def on_member_host(home):
    """The estate installed its member-host instructions here. Absent or unreadable: not a member host, so silent."""
    for rel in GLOBAL_FILES:
        try:
            with open(os.path.join(home, rel), encoding="utf-8", errors="replace") as handle:
                if handle.readline(400).strip() == MEMBER_HOST_HEADING:
                    return True
        except OSError:
            continue
    return False


def always_there(uid):
    """What is there for every session on these machines, whatever the work: the docstring's list, exact names only."""
    return {"claude-%d" % uid, "tmux-%d" % uid, "cc-daemon-%d" % uid, "node-compile-cache", "aws_crt_cross_process_lock"}


def bounded_find(args):
    """Run find with a timeout. Returns the NUL-separated names, or None if the list could not be read."""
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    except OSError:
        return None
    RUNNING[:] = [proc]
    try:
        out, _ = proc.communicate(timeout=FIND_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        return None
    finally:
        RUNNING[:] = []
    if proc.returncode != 0 and (proc.returncode != 1 or not out):      # 1 with names printed: one unreadable entry, the list stands
        return None
    return [n.decode("utf-8", errors="replace") for n in out.split(b"\0") if n]


def is_git_repository(path):
    """A checkout (.git directory or worktree file) or a bare repository."""
    return (os.path.lexists(os.path.join(path, ".git"))
            or (os.path.isfile(os.path.join(path, "HEAD")) and os.path.isdir(os.path.join(path, "objects"))))


def home_entries(home):
    names = bounded_find(["find", home, "-mindepth", "1", "-maxdepth", "1", "!", "-name", ".*", "-printf", "%f\\0"])
    if names is None:
        return None
    return sorted(n for n in names if not is_git_repository(os.path.join(home, n)))


def tmp_entries(tmp, uid):
    names = bounded_find(["find", tmp, "-mindepth", "1", "-maxdepth", "1", "-uid", str(uid), "-printf", "%f\\0"])
    if names is None:
        return None
    plumbing = always_there(uid)
    return sorted(n for n in names if n not in plumbing)


def scratch_walk(root):
    """Everything under root: (total bytes, {(project folder, session id): [bytes, newest mtime]}), or None if unread.

    Bytes are what the files occupy (blocks, as du counts them), a file with several hard links once. Only a directory
    one level inside a project folder (a name starting with "-", the harness's spelling of a path) is a session folder;
    the harness's own folders and anything put straight into root count toward the total only."""
    records = bounded_find(["find", root, "-mindepth", "1", "-printf", "%y\\t%b\\t%n\\t%i\\t%T@\\t%P\\0"])
    if records is None:
        return None
    total, seen, folders, is_dir = 0, set(), {}, set()
    for record in records:
        fields = record.split("\t", 5)
        if len(fields) != 6:
            continue
        kind, blocks, links, inode, mtime, rel = fields
        try:
            size, links, mtime = int(blocks) * 512, int(links), float(mtime)
        except ValueError:
            continue
        if kind != "d" and links > 1:
            if inode in seen:
                continue
            seen.add(inode)
        total += size
        parts = rel.split("/")
        if len(parts) < 2 or not parts[0].startswith("-"):
            continue
        key = (parts[0], parts[1])
        if len(parts) == 2 and kind == "d":
            is_dir.add(key)
        folder = folders.setdefault(key, [0, 0.0])
        folder[0] += size
        folder[1] = max(folder[1], mtime)
    return total, {k: v for k, v in folders.items() if k in is_dir}


def old_folders(folders, session, config, now):
    """Folders of other sessions holding over 1 MB, untouched for a day, whose session's transcript is as quiet."""
    count = 0
    for (project, sid), (size, newest) in folders.items():
        if sid == session or size <= OLD_FOLDER_OVER or now - newest < OLD_AFTER:
            continue
        try:
            if now - os.stat(os.path.join(config, "projects", project, sid + ".jsonl")).st_mtime < OLD_AFTER:
                continue                         # the session is still talking: alive, whatever its folder says
        except OSError:
            pass
        count += 1
    return count


def size_text(size):
    if size >= 1024 * MB:
        return "%.1f GB" % (size / (1024.0 * MB))
    return "%d MB" % max(1, int(round(size / float(MB))))


def scratch_part(tmp, uid, home):
    root = os.path.join(tmp, "claude-%d" % uid)
    if not os.path.isdir(root):                  # no Claude session has run here as this account: nothing is there
        return ""
    walked = scratch_walk(root)
    if walked is None:
        return "%s NOT CHECKED (it could not be read in time)" % root
    total, folders = walked
    session = os.environ.get("CLAUDE_CODE_SESSION_ID", "").strip()
    config = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(home, ".claude")
    old = old_folders(folders, session, config, time.time()) if session else 0
    if total <= SCRATCH_SHOWN_OVER and not old:
        return ""
    text = "%s session scratchpads: %s" % (root, size_text(total))
    if old == 1:
        text += ", 1 folder of another session over 1 MB untouched for a day"
    elif old:
        text += ", %d folders of other sessions over 1 MB untouched for a day" % old
    return text


def shown(names):
    """A count and a few names, every name on this one line whatever it holds."""
    clean = ["".join(c if c.isprintable() else "?" for c in n)[:NAME_MAX] for n in names]
    listing = ", ".join(clean[:NAMES_SHOWN])
    more = len(clean) - NAMES_SHOWN
    return "%d (%s%s)" % (len(clean), listing, " and %d more" % more if more > 0 else "")


def say(line):
    """Print the one line. A reader that has gone (stdout closed, a pipe shut early) is not a failure of the check."""
    try:
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
    except (AttributeError, OSError, ValueError):
        pass


def finish():
    """Exit 0 whatever became of stdout: nothing is left in a buffer for the interpreter to fail on at shutdown."""
    try:
        sys.stdout.flush()
    except (AttributeError, OSError, ValueError):
        pass
    os._exit(0)


def main(argv):
    tmp = "/tmp"
    if len(argv) >= 3 and argv[1] == "--tmp":
        tmp = argv[2]
    home = os.environ.get("HOME") or os.path.expanduser("~")
    if not on_member_host(home):
        return
    home, tmp = os.path.realpath(home), os.path.realpath(tmp)
    uid = os.getuid()
    parts = []
    entries = home_entries(home)
    if entries is None:
        parts.append("home folder top NOT CHECKED (it could not be read in time)")
    elif entries:
        parts.append("home folder top: %s not in git" % shown(entries))
    entries = tmp_entries(tmp, uid)
    if entries is None:
        parts.append("%s NOT CHECKED (it could not be read in time)" % tmp)
    elif entries:
        parts.append("%s: %s of this account" % (tmp, shown(entries)))
    scratch = scratch_part(tmp, uid, home)
    if scratch:
        parts.append(scratch)
    if parts:
        say("LEFTOVERS: " + "; ".join(parts))


def alarm(*_):
    for proc in RUNNING:                         # the find it was waiting on stops with it, never left walking
        try:
            proc.kill()
            proc.wait(timeout=2)
        except Exception:
            pass
    say("LEFTOVERS: NOT CHECKED (no answer within %d s)" % math.ceil(WHOLE_TIMEOUT))
    finish()


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(max(1, int(math.ceil(WHOLE_TIMEOUT))))
    try:
        main(sys.argv)
    except Exception as e:                       # never fails a session: a broken check is reported as a broken check
        say("LEFTOVERS: NOT CHECKED (%s)" % type(e).__name__)
    finish()
