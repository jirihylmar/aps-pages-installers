#!/usr/bin/env python3
"""leftovers.py - what is left on this member host, as one line for the session's report.

Called by /start-session Step 2.9a and /update-progress Step 9c (SESSION_CLOSE). On a member host it lists two things and
says nothing else: the non-dot entries at the top of the home folder that are not git repositories, and this account's
entries directly under /tmp, each with a count and a few names. It reports and nothing more: it deletes nothing, it never
fails a session (always exit 0), it prints nothing when there is nothing, and it does not say whose an entry is.

ONLY ON A MEMBER HOST. A member host is the machine whose ~/.claude/CLAUDE.md or ~/.codex/AGENTS.md opens with the heading
config/member-host/claude-global.md gives it: the file member-host-prepare.sh installs, read here by its first line and
never by a host name. Everywhere else this is silent, including when it cannot tell.

WHAT IS NOT COUNTED: what is there for every session, on every member host, whatever the work: this account's claude-<uid>
(the harness's scratchpad root), tmux-<uid> (the socket of the tmux the sessions run in) and cc-daemon-<uid> (the harness's
daemon socket), and the two caches the tools themselves keep there (node-compile-cache, aws_crt_cross_process_lock), which
are named exactly and measured on the two member hosts on 2026-11-10. Without this every session on every member host
would print the same line for ever, and a line that never changes is read as noise. A new tool's own folder simply shows up
in the list. What is inside the harness's scratchpad is not listed here; the host instructions keep it to a few MB.

Bounded: each find has a timeout, the whole run has an alarm, and a list it could not read says NOT CHECKED, never nothing
(unknown is not "none").

  python3 .claude/skills/server-report/leftovers.py            # from the project root
  python3 .claude/skills/server-report/leftovers.py --tmp DIR  # the test's fixture instead of /tmp
"""
import os
import signal
import subprocess
import sys

MEMBER_HOST_HEADING = "# Global conventions — a syndicate member host"
GLOBAL_FILES = (".claude/CLAUDE.md", ".codex/AGENTS.md")
NAMES_SHOWN = 5
NAME_MAX = 60
FIND_TIMEOUT = float(os.environ.get("LEFTOVERS_FIND_TIMEOUT", "8"))
WHOLE_TIMEOUT = float(os.environ.get("LEFTOVERS_WHOLE_TIMEOUT", "20"))


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
    try:
        out, _ = proc.communicate(timeout=FIND_TIMEOUT)
    except subprocess.TimeoutExpired:
        proc.kill()
        return None
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


def shown(names):
    """A count and a few names, every name on this one line whatever it holds."""
    clean = ["".join(c if c.isprintable() else "?" for c in n)[:NAME_MAX] for n in names]
    listing = ", ".join(clean[:NAMES_SHOWN])
    more = len(clean) - NAMES_SHOWN
    return "%d (%s%s)" % (len(clean), listing, " and %d more" % more if more > 0 else "")


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
    if parts:
        print("LEFTOVERS: " + "; ".join(parts))


def alarm(*_):
    print("LEFTOVERS: NOT CHECKED (no answer within %d s)" % WHOLE_TIMEOUT)
    sys.stdout.flush()
    os._exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(int(WHOLE_TIMEOUT))
    try:
        main(sys.argv)
    except Exception as e:                       # never fails a session: a broken check is reported as a broken check
        print("LEFTOVERS: NOT CHECKED (%s)" % type(e).__name__)
    sys.exit(0)
