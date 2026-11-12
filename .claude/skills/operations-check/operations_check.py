#!/usr/bin/env python3
"""operations-check: whether the entry document's Operate and Rebuild section says what is true.

WHY THIS EXISTS. On 2026-11-08 the operator asked that development may cost many tokens so that
running a system once it is up costs few, that every project be rebuildable from git on any host
given the credentials and access hyl-resources-manager issues, and that the rule arrive through new
work and new projects rather than a wave of refactors of what exists. The words are quoted once, in
PROJECT_CHARTER.md section 8, "Token-heavy development, token-light operation", which is the rule.
Every project's entry document (CLAUDE.md, or AGENTS.md where the project has no CLAUDE.md) carries
a section
"## Operate and Rebuild", the cheap starting point of a maintenance session, with six rows:
  Runs without a session    the committed timers, scheduled jobs or pipelines that do routine work
  Health                    one committed command that reads the running system, non-zero on a problem
  Operating notes           where what to do about each known problem is written
  Rebuild on another host   the documented path by which a clean clone builds and deploys it
  Builds and how long       where each build, test and deploy step is listed with where it runs, its
                            command, how long it takes as measured and the bound past which it is
                            stopped and investigated
  Where agents take part    where it is written which work an AI agent does, and how much
Each row names the committed file that does it, or says `not built yet` or `none: <reason>`.

WHAT IT REPORTS, per row of every entry document that has the section:
  NAMED          at least one path claim, and git holds every one this repository can check
  NONE           `none: <reason>`, with a reason
  NOT-BUILT-YET  `not built yet` (a trailing period allowed)
  UNVERIFIED     text with no path this checker can confirm (`make health`)
  EMPTY          nothing, a bare `none`, or `none:` with no reason
  MISSING-PATH   a path claim git does not hold                       (something written is false)
  HOST-PATH      a path claim starting with / or ~: one host's location (something written is false)
  ABSENT         the row is not there
A path claim is the first word of a backticked span, less a trailing #anchor or :<line>, when it
holds a / or ends in .<extension>. Identifiers are not path claims: a word starting with -, $, @ or
http, holding :// or another :, or @; a word starting with / whose first segment is not a host
directory (home, etc, var, ...): an SSM parameter name; one whose first segment holds a dot and is
not in the tree (ghcr.io/..., github.com/...); an image's :<tag> on a name with no extension; and
any span right after a kind word (the secret `x/y`, the parameter, image, key, ARN, role, bucket,
token, identifier, profile, registry). A claim under
a member directory progress.json declares (git_repos local or path, relations.members path, or a
submodule) that this repository does not hold is checked in that member's checkout when one is
here (working tree only), and is otherwise listed as `elsewhere`: neither confirmed nor false.
A held .md claim followed by `§ <heading>` (to the end of the cell, a backtick, ; or ,) must have
that heading, outside a fence, in the same tree; a missing heading is MISSING-PATH, listed as
`<file> § <heading>`. A reference that starts with a section number matches a heading that starts
with that number (`PROJECT_CHARTER.md` § 8). Section verdict: claims-missing (a MISSING-PATH or
HOST-PATH), complete (all six rows NAMED or NONE), otherwise partial. The run's verdict is
claims-missing when any section checked is, otherwise the entry document's section's: CLAUDE.md's,
or AGENTS.md's where CLAUDE.md has none (noted section-in-agents when a CLAUDE.md exists); a second
copy in AGENTS.md beside CLAUDE.md's is noted two-entry-sections. Notes never change the exit code; no-section when no entry document has the section. A heading inside a
fenced code block is not the section, so a document that quotes the format does not have it.

It also counts adoption in progress.json: phases, phases with an `operations` statement and how
many of those start `none:`, terminal tasks and how many record `ops:` in verify_result or notes,
and with --since the same for phases started or created, and tasks completed, at or after an
instant. An absent or unparseable progress.json is reported as that, never as zero.

It never judges prose, never proves a rebuild (a rebuild path is evidence once a clean clone has
followed it, charter section 10, "Verify reality"), never creates work, sends a notice or writes a
file. An existing project without the section is in a counted state, not in defect.

WHERE IT READS. The working tree and the index (default), or one commit's tree with --rev, in place,
in a bare repository or in a blobless clone: the blobs it needs and lacks are fetched in one fetch
for the entry documents and progress.json and, only when a row refers to a heading, one more for
the .md files named; no read fetches lazily.

EXIT. 0 complete and nothing false; 1 claims-missing; 3 not complete yet (no-section or partial),
nothing false; 2 could not check: not a git repository, an unknown revision, a blob that could not
be read, a defect in this checker (one line on stderr, never Python's exit 1). Stdlib only; runs
under python3 -I.
"""
import argparse
import fnmatch
import json
import os
import re
import signal
import subprocess
import sys
from datetime import datetime, timedelta

# --- the section, stated once -----------------------------------------------------------------
ENTRY_DOCS = ("CLAUDE.md", "AGENTS.md")
PROGRESS = "progress.json"
HEADING_RE = re.compile(r"^## Operate and Rebuild[ \t]*$")
END_RE = re.compile(r"^#{1,2}(?:[ \t]|$)")          # the next heading of level 1 or 2 ends it
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
ROWS = ("Runs without a session", "Health", "Operating notes", "Rebuild on another host",
        "Builds and how long", "Where agents take part")

NAMED, NONE, NOT_BUILT, UNVERIFIED = "NAMED", "NONE", "NOT-BUILT-YET", "UNVERIFIED"
EMPTY, MISSING, HOST, ABSENT = "EMPTY", "MISSING-PATH", "HOST-PATH", "ABSENT"
FALSE_STATUSES = (MISSING, HOST)
DONE_STATUSES = (NAMED, NONE)

NO_SECTION, CLAIMS_MISSING, COMPLETE, PARTIAL = "no-section", "claims-missing", "complete", "partial"
EXIT = {COMPLETE: 0, CLAIMS_MISSING: 1, PARTIAL: 3, NO_SECTION: 3}

NOT_BUILT_RE = re.compile(r"^not built yet\.?$", re.I)
NONE_RE = re.compile(r"^none\s*:(.*)$", re.I | re.S)
BARE_NONE_RE = re.compile(r"^none\.?$", re.I)
SPAN_RE = re.compile(r"(`+)(.+?)\1")
EXT_RE = re.compile(r"\.[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*$")   # .sh .md .timer; not 3.11
ANCHOR_RE = re.compile(r"#.*$")
LINE_RE = re.compile(r":\d+(?:-\d+)?$")
SEP_CELL_RE = re.compile(r"^:?-+:?$")
GLOB_CHARS = "*?["
HOST_ROOTS = {"home", "root", "Users", "etc", "usr", "var", "opt", "srv", "mnt", "media", "tmp", "run",
              "data", "bin", "sbin", "lib", "Library", "Volumes", "private", "snap"}
# A span right after one of these words names an identifier (the secret `myproject/prod/db`), which
# PROJECT_CHARTER.md section 8 asks a rebuild path to name, and is never a path claim.
KIND_BEFORE_RE = re.compile(r"(?i)\b(?:secret|parameter|image|key|arn|role|bucket|token|identifier|"
                            r"profile|registry)s?(?:[ \t]+(?:name|named|called|id))?[ \t]*:?[ \t]*$")
FETCH_TIMEOUT_ENV = "OPERATIONS_CHECK_FETCH_TIMEOUT"
FETCH_TIMEOUT_DEFAULT = 60.0
REF_RE = re.compile(r"[ \t]*\u00a7[ \t]*([^`;,]*)")      # `README.md` § Builds and how long
HEADING_LINE_RE = re.compile(r"^ {0,3}#{1,6}(?:[ \t]+(.*?))?[ \t]*$")
NUM_REF_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?(?:\s+(.*))?$")

# progress.json: the terminal vocabulary is progress-check's (TERMINAL_STATUSES there).
TERMINAL = {"complete", "completed", "superseded", "done", "closed", "dropped", "cancelled",
            "canceled", "resolved", "obsolete", "abandoned"}
OPS_RE = re.compile(r"\bops:", re.I)
OPS_NONE_RE = re.compile(r"none:", re.I)
STAMP_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2})(?:\.\d+)?)?"
                      r"\s*(Z|[+-]\d{2}:?\d{2})?)?$", re.I)
DAY_RE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

SYMLINK, GITLINK = "120000", "160000"

HOST_WHY = ("a location on one host, which a clean clone on another host does not have "
            "(PROJECT_CHARTER.md section 8: host-specific locations resolve at runtime); name the "
            "committed file instead")


class CannotCheck(Exception):
    """The check as a whole cannot run: exit 2."""


# --- the document -----------------------------------------------------------------------------
def closes(fence, m, line):
    """Whether this line, whose fence match is m, closes the open fence."""
    return bool(m) and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
        and not line[m.end():].strip()


def sections_of(text):
    """Each '## Operate and Rebuild' section outside a fence: a list of (line, fenced) pairs."""
    found, cur, fence = [], None, None
    for line in text.lstrip("\ufeff").splitlines():
        m = FENCE_RE.match(line)
        if fence:
            if closes(fence, m, line):
                fence = None
            if cur is not None:
                cur.append((line, True))
            continue
        if m:
            fence = m.group(1)
            if cur is not None:
                cur.append((line, True))
            continue
        if cur is not None and END_RE.match(line):
            found.append(cur)
            cur = None
        if HEADING_RE.match(line):
            cur = []
            continue
        if cur is not None:
            cur.append((line, False))
    if cur is not None:
        found.append(cur)
    return found


def norm_heading(text):
    """A heading's text, or a reference to one, as compared: trailing #s, blanks and a period
    dropped, * and backticks removed, blanks collapsed, no case."""
    t = (text or "").strip().rstrip("#").strip().rstrip(".").strip()
    return re.sub(r"\s+", " ", t.replace("*", "").replace("`", "")).strip().lower()


def headings_in(text):
    """The headings (# to ######) of a markdown text, outside fences, as norm_heading gives them."""
    out, fence = [], None
    for line in text.lstrip("\ufeff").splitlines():
        m = FENCE_RE.match(line)
        if fence:
            if closes(fence, m, line):
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        h = HEADING_LINE_RE.match(line)
        if h:
            out.append(norm_heading(h.group(1)))
    return out


def heading_matches(ref, headings):
    """Whether a reference names one of these headings. A reference that starts with a section
    number also matches a heading that starts with that number, or the text after the number."""
    r = norm_heading(ref)
    if r in headings:
        return True
    m = NUM_REF_RE.match(r)
    if m:
        num, rest = m.group(1), m.group(2)
        if any(h == num or h.startswith(num + ".") or h.startswith(num + " ") for h in headings):
            return True
        if rest and norm_heading(rest) in headings:
            return True
    return False


def refs_of(value):
    """[(path claim, heading reference or None)] for the backticked spans of a cell, in order."""
    out = []
    for sm in SPAN_RE.finditer(value):
        c = claim_of(sm.group(2))
        if not c or KIND_BEFORE_RE.search(value[:sm.start()]):
            continue
        ref = None
        rm = REF_RE.match(value, sm.end())
        if rm:
            # A trailing period is dropped on both sides of the emphasis: _Heading_. and *Heading.* alike.
            ref = rm.group(1).strip().rstrip(".").strip().strip("*_").strip().rstrip(".").strip() or None
        out.append((c, ref))
    return out


def wants_heading(claim, ref):
    return bool(ref) and claim.lower().endswith(".md") and not any(ch in claim for ch in GLOB_CHARS)


def split_cells(line):
    """A table row's cells. A | inside a code span or written \\| does not split."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    for aware in (True, False):
        cells, cur, i, tick = [], [], 0, 0
        while i < len(s):
            c = s[i]
            if c == "\\" and s[i + 1:i + 2] == "|":
                cur.append("|")
                i += 2
                continue
            if c == "`" and aware:
                j = i
                while j < len(s) and s[j] == "`":
                    j += 1
                run = j - i
                tick = run if tick == 0 else (0 if tick == run else tick)
                cur.append(s[i:j])
                i = j
                continue
            if c == "|" and tick == 0:
                cells.append("".join(cur))
                cur = []
                i += 1
                continue
            cur.append(c)
            i += 1
        if tick and aware:
            continue                            # an unclosed span is literal: split again plainly
        tail = "".join(cur)
        if tail.strip():
            cells.append(tail)                  # a row with no closing pipe
        return [x.strip() for x in cells]
    return []


def is_separator(cells):
    return bool(cells) and all(SEP_CELL_RE.match(c.replace(" ", "")) for c in cells)


def table_rows(section):
    """[(label cell, value cell)] for every data row of every table in the section."""
    rows, block = [], []

    def flush():
        if not block:
            return
        cells = [split_cells(l) for l in block]
        start = 2 if len(cells) >= 2 and is_separator(cells[1]) else 0
        for c in cells[start:]:
            if c and not is_separator(c):
                rows.append((c[0], c[1] if len(c) > 1 else ""))
        del block[:]

    for line, fenced in section:
        if not fenced and line.lstrip().startswith("|"):
            block.append(line)
        else:
            flush()
    flush()
    return rows


def norm_label(cell):
    return re.sub(r"\s+", " ", cell.replace("*", "").replace("`", "")).strip().lower()


LABELS = {r.lower(): r for r in ROWS}


def claim_of(span):
    """The path a backticked span claims, or None for no claim (a command, a URL, an identifier)."""
    words = span.split()
    if not words:
        return None
    w = ANCHOR_RE.sub("", words[0])
    bare = LINE_RE.sub("", w)
    if bare != w and not EXT_RE.search(bare.rsplit("/", 1)[-1]):
        return None                             # org/app:16 is an image and its tag, not a line
    w = bare
    if not w or w.startswith(("-", "$", "@", "http")) or ":" in w or "@" in w:
        return None                             # a flag, a variable, a URL, an ARN, git@host:repo
    if "/" not in w and not EXT_RE.search(w):
        return None
    while w.startswith("./"):
        w = w[2:]
    if w.startswith("/") and w.lstrip("/").split("/", 1)[0] not in HOST_ROOTS:
        return None                             # /myproject/prod/api-key: an SSM parameter name
    return w or None


def classify(value, where):
    """One row: {status, paths, missing, host_paths, elsewhere, notes}."""
    row = {"status": None, "paths": [], "missing": [], "host_paths": [], "elsewhere": [],
           "notes": []}
    core = value.strip().strip("*`").strip()
    if not core:
        row["status"] = EMPTY
        return row
    if NOT_BUILT_RE.match(core):
        row["status"] = NOT_BUILT
        return row
    m = NONE_RE.match(core)
    if m:
        row["status"] = NONE if m.group(1).strip().strip("*`").strip() else EMPTY
        return row
    if BARE_NONE_RE.match(core):
        row["status"] = EMPTY
        return row
    claims, refs = [], []
    for c, ref in refs_of(value):
        if where.identifier(c):
            continue                            # ghcr.io/org/app: a registry name, not a path
        if c not in claims:
            claims.append(c)
        if wants_heading(c, ref) and (c, ref) not in refs:
            refs.append((c, ref))
    row["paths"] = claims
    confirmed = untracked = 0
    for c in claims:
        if c.startswith(("/", "~")):
            row["host_paths"].append(c)
            row["missing"].append(c)
            row["notes"].append("%s: %s" % (c, HOST_WHY))
            continue
        verdict, note = where.judge(c)
        if verdict == "tracked":
            confirmed += 1
            for rc, ref in refs:
                if rc == c and where.has_heading(c, ref) is False:
                    untracked += 1
                    named = "%s \u00a7 %s" % (c, ref)
                    row["missing"].append(named)
                    row["notes"].append("%s: %s has no heading %r%s" % (
                        named, c, ref, "" if where.worktree else " in the tree of %s" % where.rev_label))
        elif verdict == "elsewhere":
            row["elsewhere"].append(c)
            row["notes"].append("%s: %s" % (c, note))
        else:
            untracked += 1
            row["missing"].append(c)
            row["notes"].append("%s: %s" % (c, note))
    if untracked:
        row["status"] = MISSING
    elif row["host_paths"]:
        row["status"] = HOST
    elif confirmed:
        row["status"] = NAMED
    else:
        row["status"] = UNVERIFIED
    return row


def check_section(section, where):
    """(rows in canonical order, extra labels, duplicate labels)."""
    seen, extra, dupes = {}, [], []
    for label_cell, value in table_rows(section):
        key = norm_label(label_cell)
        if key in LABELS:
            if LABELS[key] in seen:
                dupes.append(LABELS[key])
            else:
                seen[LABELS[key]] = value
        elif key and key not in extra:
            extra.append(label_cell.strip())
    rows = []
    for label in ROWS:
        if label not in seen:
            rows.append(dict(label=label, status=ABSENT, value=None, paths=[], missing=[],
                             host_paths=[], elsewhere=[], notes=[]))
            continue
        r = classify(seen[label], where)
        rows.append(dict([("label", label), ("status", r.pop("status")),
                          ("value", seen[label].strip())] + list(r.items())))
    return rows, extra, dupes


def section_verdict(rows):
    statuses = [r["status"] for r in rows]
    if any(s in FALSE_STATUSES for s in statuses):
        return CLAIMS_MISSING
    if all(s in DONE_STATUSES for s in statuses):
        return COMPLETE
    return PARTIAL


def run_verdict(sections, entry):
    """claims-missing when any section checked says something false; otherwise the entry
    document's section decides; no-section when there is none."""
    if entry is None:
        return NO_SECTION
    if any(s["verdict"] == CLAIMS_MISSING for s in sections):
        return CLAIMS_MISSING
    return entry["verdict"]


# --- what git holds ---------------------------------------------------------------------------
class Holdings(object):
    """The paths one tree holds, and the member directories beside it."""

    def __init__(self, files, gitlinks, members, rev_label, worktree=None, git=None, oids=None,
                 members_known=True, members_why=None):
        self.files = set(files)
        # False when progress.json, which declares the member directories, could not be read or
        # parsed: a claim git does not hold might be a member's, so it cannot be judged false.
        self.members_known = members_known
        self.members_why = members_why
        self.oids = oids or {}                  # --rev: path -> blob oid, regular files only
        self._text = {}                         # path -> text, or None when it cannot be read
        self.unreadable = []
        self.dirs = set()
        for p in self.files:
            parts = p.split("/")
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))
        self.members = sorted(set(members) | set(gitlinks), key=len, reverse=True)
        self.rev_label = rev_label
        self.worktree = worktree
        self.git = git
        self._member_files = {}
        self._by_name = None

    def holds(self, claim, files=None, dirs=None):
        files = self.files if files is None else files
        dirs = self.dirs if dirs is None else dirs
        c = claim.rstrip("/")
        if not c:
            return False
        if any(ch in c for ch in GLOB_CHARS):
            return any(fnmatch.fnmatchcase(p, c) for p in files) or \
                any(fnmatch.fnmatchcase(d, c) for d in dirs)
        if claim.endswith("/"):
            return c in dirs
        return c in files or c in dirs

    def identifier(self, claim):
        """A registry or host name (ghcr.io/org/app): a dotted first segment not in the tree."""
        c = claim.rstrip("/")
        if "/" not in c:
            return False
        top = c.split("/", 1)[0]
        return ("." in top and not top.startswith(".") and top not in self.files
                and top not in self.dirs and top not in self.members)

    def member_of(self, claim):
        c = claim.rstrip("/")
        for d in self.members:
            if c == d or c.startswith(d + "/"):
                return d
        return None

    def member_holdings(self, d):
        """(files, dirs) of the member checkout at d in this working tree, or None."""
        if d in self._member_files:
            return self._member_files[d]
        got = None
        path = os.path.join(self.worktree, d) if self.worktree else None
        if path and os.path.isdir(path):
            g = Git(path)
            try:
                top, _ = g.text(["rev-parse", "--show-toplevel"])
                if os.path.realpath(top) == os.path.realpath(path):
                    out, _ = g.run(["ls-files", "-z"])
                    files = {decode(p) for p in out.split(b"\0") if p}
                    dirs = set()
                    for p in files:
                        parts = p.split("/")
                        for i in range(1, len(parts)):
                            dirs.add("/".join(parts[:i]))
                    got = (files, dirs)
            except CannotCheck:
                got = None
        self._member_files[d] = got
        return got

    def prefetch(self, paths):
        """--rev: read these .md files' blobs at once, so a partial clone fetches them in one go."""
        if self.worktree:
            return
        want = {p: self.oids[p] for p in paths if p in self.oids and p not in self._text}
        if not want:
            return
        data, unread = read_blobs(self.git, want.values())
        for p, oid in want.items():
            if oid in unread:
                self._text[p] = None
                self.unreadable.append((p, "%s (a row refers to its headings)" % unread[oid]))
            else:
                self._text[p] = data[oid].decode("utf-8", "replace")

    def has_heading(self, path, ref):
        """True or False, or None when the file cannot be read (it is then named unreadable)."""
        if path not in self._text:
            if self.worktree:
                try:
                    with open(os.path.join(self.worktree, path), "rb") as fh:
                        self._text[path] = fh.read().decode("utf-8", "replace")
                except OSError as exc:
                    self._text[path] = None
                    self.unreadable.append((path, "%s (a row refers to its headings)" % exc))
            elif path in self.oids:
                self.prefetch([path])
            else:
                return None                     # a symlink or submodule in the tree: not read
        text = self._text.get(path)
        if text is None:
            return None
        return heading_matches(ref, headings_in(text))

    def suggest(self, claim):
        if self._by_name is None:
            self._by_name = {}
            for p in self.files:
                self._by_name.setdefault(p.rsplit("/", 1)[-1], []).append(p)
        name = claim.rstrip("/").rsplit("/", 1)[-1]
        hits = sorted(self._by_name.get(name, []))
        return ("; git holds %s" % " and ".join(hits[:2])) if hits else ""

    def judge(self, claim):
        """('tracked' | 'elsewhere' | 'missing', note)."""
        if self.holds(claim):
            return "tracked", ""
        d = self.member_of(claim)
        if d is not None:
            inner = claim[len(d):].lstrip("/")
            mh = self.member_holdings(d) if self.worktree else None
            if mh is not None:
                if not inner or self.holds(inner, *mh):
                    return "tracked", ""
                return "missing", ("not tracked by the member checkout %s/ either" % d)
            return "elsewhere", ("under the member directory %s/, whose own repository holds it; "
                                 "not checked from here" % d)
        if not self.members_known:
            why = self.members_why or "not read"
            self.unreadable.append((PROGRESS, "%s; it declares the member directories, so a claim "
                                    "git does not hold cannot be judged false" % why))
            return "elsewhere", ("not judged: progress.json declares the member directories, and it "
                                 "could not be used (%s)" % why)
        if self.worktree:
            here = os.path.lexists(os.path.join(self.worktree, claim.rstrip("/")))
            why = ("present in the working tree, but git does not hold it" if here
                   else "no such file, and git does not hold it")
        else:
            why = "not in the tree of %s" % self.rev_label
        return "missing", why + self.suggest(claim)


# --- progress.json ----------------------------------------------------------------------------
def iter_phases(doc):
    ph = doc.get("phases")
    if isinstance(ph, dict):
        return [v for v in ph.values() if isinstance(v, dict)]
    if isinstance(ph, list):
        return [v for v in ph if isinstance(v, dict)]
    return []


def iter_tasks(phase):
    ts = phase.get("tasks")
    items = ts.values() if isinstance(ts, dict) else ts if isinstance(ts, list) else []
    return [t for t in items if isinstance(t, dict)]


def norm_status(st):
    return re.sub(r"[\s\-]+", "_", str(st).strip().lower())


def as_text(v):
    if isinstance(v, str):
        return v
    if v is None:
        return ""
    return json.dumps(v, ensure_ascii=False)


def place(value):
    """-> (day 'YYYY-MM-DD' or None, UTC datetime or None when no zoned time is given)."""
    if not isinstance(value, str):
        return None, None
    v = value.strip()
    m = STAMP_RE.match(v)
    if not m:
        d = DAY_RE.match(v)                     # a date, then something that is no time
        if not d or not real_day(*d.groups()):
            return None, None
        return "%s-%s-%s" % d.groups(), None
    y, mo, d, hh, mi, ss, zone = m.groups()
    if not real_day(y, mo, d):
        return None, None                       # 2026-11-31: no such day
    day = "%s-%s-%s" % (y, mo, d)
    if hh is None:
        return day, None
    try:
        t = datetime(int(y), int(mo), int(d), int(hh), int(mi), int(ss or 0))
    except ValueError:
        return None, None
    if zone is None:
        return day, None
    if zone.upper() != "Z":
        z = zone.replace(":", "")
        off = timedelta(hours=int(z[1:3]), minutes=int(z[3:5]))
        t = t - off if z[0] == "+" else t + off
    return day, t


def real_day(y, mo, d):
    try:
        datetime(int(y), int(mo), int(d))
    except ValueError:
        return False
    return True


def since_of(value, since):
    """True at or after since; False before it, or no value at all; None when a value is there but
    cannot be placed either side of it: a date with no zoned time on its day, or a stamp that is
    malformed or impossible. A value that is there is never silently read as before."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return False
    day, at = place(value)
    if day is None:
        return None
    s_day, s_at = since
    if at is not None:
        return at >= s_at
    if day != s_day:
        return day > s_day
    return None


def parse_since(text):
    day, at = place(text)
    if at is None:
        raise argparse.ArgumentTypeError(
            "%r is not a zoned UTC instant such as 2026-11-08T12:00:00Z" % text)
    return (day, at, text)


def completed_of(task):
    """The completion stamp: completed_at, else completed (progress-check's COMPLETION_KEYS)."""
    for k in ("completed_at", "completed"):
        v = task.get(k)
        if v is not None and not (isinstance(v, str) and not v.strip()):
            return v
    return None


def counts(phases, tasks):
    with_ops = [p for p in phases if isinstance(p.get("operations"), str)
                and p["operations"].strip()]
    return {
        "phases": len(phases),
        "phases_with_operations": len(with_ops),
        "phases_operations_none": sum(1 for p in with_ops
                                      if OPS_NONE_RE.match(p["operations"].strip())),
        "terminal_tasks": len(tasks),
        "terminal_tasks_with_ops": sum(1 for t in tasks
                                       if OPS_RE.search(as_text(t.get("verify_result")))
                                       or OPS_RE.search(as_text(t.get("notes")))),
    }


def record_of(state, raw, since, error=None):
    rec = {"path": PROGRESS, "state": state, "error": error, "phases": None,
           "phases_with_operations": None, "phases_operations_none": None,
           "terminal_tasks": None, "terminal_tasks_with_ops": None, "since": None}
    if state != "read":
        return rec, None
    try:
        doc = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as exc:
        rec.update(state="unparseable", error="does not parse: %s" % one_line(exc))
        return rec, None
    if not isinstance(doc, dict):
        rec.update(state="unparseable", error="its root is %s, not an object" % type(doc).__name__)
        return rec, None
    phases = iter_phases(doc)
    terminal = [t for p in phases for t in iter_tasks(p)
                if norm_status(t.get("status") or "") in TERMINAL]
    rec.update(counts(phases, terminal))
    if since:
        s = (since[0], since[1])
        ph_in, ph_unplaced = [], 0
        for p in phases:
            marks = [since_of(p.get(k), s) for k in ("started_at", "created_at") if k in p]
            if True in marks:
                ph_in.append(p)
            elif None in marks:
                ph_unplaced += 1
        t_in, t_unplaced = [], 0
        for t in terminal:
            mark = since_of(completed_of(t), s)
            if mark:
                t_in.append(t)
            elif mark is None:
                t_unplaced += 1
        sc = counts(ph_in, t_in)
        sc.update(at=since[2], phases_unplaceable=ph_unplaced, tasks_unplaceable=t_unplaced)
        rec["since"] = sc
    return rec, doc


def member_dirs(doc):
    """Relative directories progress.json declares for other repositories."""
    found = []

    def add(p):
        if not isinstance(p, str):
            return
        p = p.strip()
        while p.startswith("./"):
            p = p[2:]
        p = p.rstrip("/")
        if not p or p == "." or p.startswith(("/", "~")) or ".." in p.split("/"):
            return
        found.append(p)

    if not isinstance(doc, dict):
        return found
    gr = doc.get("git_repos")
    if isinstance(gr, dict):
        for v in gr.values():
            if isinstance(v, dict):
                for k in ("local", "path", "local_path"):
                    add(v.get(k))
    rel = doc.get("relations")
    if isinstance(rel, dict) and isinstance(rel.get("members"), list):
        for m in rel["members"]:
            if isinstance(m, dict):
                add(m.get("path"))
    return found


# --- git --------------------------------------------------------------------------------------
class Git(object):
    def __init__(self, cwd):
        self.cwd = cwd
        self.env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
        # Reads never fetch: what is needed and lacking is fetched once, in read_blobs().
        self.read_env = dict(self.env, GIT_NO_LAZY_FETCH="1")

    def run(self, args, stdin=None, ok=(0,), env=None):
        try:
            p = subprocess.run(["git", "-C", self.cwd] + list(args), input=stdin,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               env=env or self.env)
        except OSError as exc:
            raise CannotCheck("cannot run git: %s" % exc)
        if p.returncode not in ok:
            err = p.stderr.decode("utf-8", "replace").strip().splitlines()
            raise CannotCheck("git %s failed (exit %d)%s" % (
                " ".join(args[:3]), p.returncode, ": " + err[-1] if err else ""))
        return p.stdout, p.returncode

    def text(self, args, ok=(0,)):
        out, rc = self.run(args, ok=ok)
        return out.decode("utf-8", "surrogateescape").strip(), rc


def decode(raw):
    return raw.decode("utf-8", "surrogateescape")


def locate(cwd, need_worktree):
    if not os.path.isdir(cwd):
        raise CannotCheck("no such directory: %s" % cwd)
    git = Git(cwd)
    try:
        inside, _ = git.text(["rev-parse", "--is-inside-work-tree"])
    except CannotCheck:
        raise CannotCheck("not a git repository: %s" % os.path.abspath(cwd))
    if inside == "true":
        top, _ = git.text(["rev-parse", "--show-toplevel"])
        return Git(top), top
    if need_worktree:
        raise CannotCheck("not a git work tree: %s" % os.path.abspath(cwd))
    return git, None                            # a bare repository, for --rev


def resolve(git, rev):
    if not rev or rev.startswith("-"):
        raise CannotCheck("unknown revision: %r" % rev)
    try:
        commit, _ = git.text(["rev-parse", "--verify", "--quiet", rev + "^{commit}"])
    except CannotCheck:
        raise CannotCheck("unknown revision: %s" % rev)
    return commit


def tree_entries(git, commit):
    """([(mode, type, oid, path)] for the whole tree of commit."""
    out, _ = git.run(["ls-tree", "-r", "-z", "--full-tree", commit], env=git.read_env)
    entries = []
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, otype, oid = meta.decode().split()
        entries.append((mode, otype, oid, decode(path)))
    return entries


def index_entries(git):
    out, _ = git.run(["ls-files", "-z", "-s"])
    entries, seen = [], set()
    for rec in out.split(b"\0"):
        if not rec:
            continue
        meta, _, path = rec.partition(b"\t")
        mode, oid, _stage = meta.decode().split()
        path = decode(path)
        if path in seen or mode == "040000":
            continue
        seen.add(path)
        entries.append((mode, "commit" if mode == GITLINK else "blob", oid, path))
    return entries


def present_objects(git, oids):
    """The subset of oids this repository holds, decided WITHOUT fetching anything."""
    if not oids:
        return set()
    out, _ = git.run(["rev-list", "--objects", "--no-walk", "--ignore-missing", "--missing=print",
                      "--stdin"], stdin=("\n".join(sorted(oids)) + "\n").encode(),
                     env=git.read_env)
    have = set()
    for line in out.decode("ascii", "replace").splitlines():
        if line and not line.startswith("?"):
            have.add(line.split()[0])
    return have & set(oids)


def promisor_remote(git):
    out, _ = git.text(["config", "--get-regexp", r"^remote\..*\.promisor$"], ok=(0, 1))
    remotes = [line.split()[0][len("remote."):-len(".promisor")] for line in out.splitlines()
               if line.split()[-1:] in (["true"], ["yes"], ["on"], ["1"])]
    if not remotes:
        old, _ = git.text(["config", "--get", "extensions.partialClone"], ok=(0, 1))
        remotes = [old] if old else []
    return remotes[0] if remotes else None


def fetch_timeout():
    """The fetch's bound in seconds: OPERATIONS_CHECK_FETCH_TIMEOUT, else 60."""
    try:
        v = float(os.environ.get(FETCH_TIMEOUT_ENV, "") or FETCH_TIMEOUT_DEFAULT)
    except ValueError:
        v = FETCH_TIMEOUT_DEFAULT
    return v if v > 0 else FETCH_TIMEOUT_DEFAULT


def _kill_group(p):
    try:
        os.killpg(p.pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass


def fetch_missing(git, remote, oids):
    """Fetch exactly these blobs from the promisor in ONE fetch; return None or why it failed.

    The fetch is the one call that goes over the network, so it runs in its own process group
    under fetch_timeout(), and the whole group (git and its transport helper) is killed when the
    bound fires: a stalled origin is a fetch that failed, never a run that hangs."""
    bound = fetch_timeout()
    try:
        p = subprocess.Popen(["git", "-C", git.cwd, "-c", "fetch.negotiationAlgorithm=noop",
                              "fetch", remote, "--no-tags", "--no-write-fetch-head",
                              "--recurse-submodules=no", "--filter=blob:none", "--stdin"],
                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             env=git.env, start_new_session=True)
    except OSError as exc:
        return "cannot run git fetch: %s" % exc
    try:
        _, err = p.communicate(("\n".join(sorted(oids)) + "\n").encode(), timeout=bound)
    except subprocess.TimeoutExpired:
        _kill_group(p)
        try:
            p.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        return ("git fetch from %s did not finish within %gs (%s) and was stopped"
                % (remote, bound, FETCH_TIMEOUT_ENV))
    except BaseException:
        _kill_group(p)
        raise
    if p.returncode == 0:
        return None
    lines = [l.strip() for l in err.decode("utf-8", "replace").splitlines() if l.strip()]
    said = [l for l in lines if l.startswith(("fatal:", "error:"))] or lines[-1:]
    return "git fetch exited %d%s" % (p.returncode, ": " + said[0] if said else "")


def read_blobs(git, oids):
    """({oid: bytes}, {oid: why unread}). One fetch for what is lacking; no lazy fetch."""
    oids = set(oids)
    have = present_objects(git, oids)
    missing = oids - have
    unread = {}
    if missing:
        remote = promisor_remote(git)
        why = "not in this repository"
        if remote:
            err = fetch_missing(git, remote, missing)
            have |= present_objects(git, missing)
            why = ("not in this clone, and the one fetch from %s failed: %s" % (remote, err)
                   if err else "not in this clone, and the fetch from %s did not bring it" % remote)
        for oid in missing - have:
            unread[oid] = "blob %s is %s" % (oid[:12], why)
    data = {}
    for oid in sorted(oids & have):
        out, _ = git.run(["cat-file", "blob", oid], env=git.read_env)
        data[oid] = out
    return data, unread


# --- the run ----------------------------------------------------------------------------------
def gather(args):
    """Everything the check reads: (sources {name: (state, bytes|None, note)}, Holdings, info)."""
    git, top = locate(args.cwd, need_worktree=args.rev is None)
    wanted = ENTRY_DOCS + (PROGRESS,)
    sources, unreadable = {}, []
    if args.rev is not None:
        commit = resolve(git, args.rev)
        entries = tree_entries(git, commit)
        root = {e[3]: e for e in entries if e[3] in wanted}
        blobs = {name: e[2] for name, e in root.items() if e[1] == "blob"}   # a symlink too
        data, unread = read_blobs(git, blobs.values())
        for name in wanted:
            if name not in root:
                sources[name] = ("absent", None, None)
            elif name not in blobs:
                sources[name] = ("absent", None, "tracked as a %s" % root[name][1])
            elif blobs[name] in unread:
                sources[name] = ("unreadable", None, unread[blobs[name]])
                unreadable.append((name, unread[blobs[name]]))
            elif root[name][0] == SYMLINK:
                sources[name] = ("link", None, decode(data[blobs[name]]))
            else:
                sources[name] = ("read", data[blobs[name]], None)
        files = [e[3] for e in entries]
        gitlinks = [e[3] for e in entries if e[0] == GITLINK]
        oids = {e[3]: e[2] for e in entries if e[1] == "blob" and e[0] != SYMLINK}
        label = args.rev
        info = {"rev": args.rev, "commit": commit, "source": "%s (%s)" % (args.rev, commit[:12]),
                "tracked": set(files)}
        worktree = None
    else:
        entries = index_entries(git)
        files = [e[3] for e in entries]
        gitlinks = [e[3] for e in entries if e[0] == GITLINK]
        for name in wanted:
            p = os.path.join(top, name)
            if os.path.islink(p):
                sources[name] = ("link", None, os.readlink(p))
            elif os.path.isfile(p):
                try:
                    with open(p, "rb") as fh:
                        sources[name] = ("read", fh.read(), None)
                except OSError as exc:
                    sources[name] = ("unreadable", None, str(exc))
                    unreadable.append((name, str(exc)))
            else:
                sources[name] = ("absent", None, None)
        label = "the index"
        oids = None
        info = {"rev": None, "commit": None, "source": "the working tree of %s" % top,
                "tracked": set(files)}
        worktree = top
    st, raw, note = sources[PROGRESS]
    if st == "link":
        record, doc = record_of("unparseable", None, args.since,
                                error="tracked as a symlink (to %s), not read" % note)
    elif st == "unreadable":
        record, doc = record_of("unreadable", None, args.since, error=note)
    else:
        record, doc = record_of(st, raw, args.since)
    holdings = Holdings(files, gitlinks, member_dirs(doc), label, worktree=worktree, git=git,
                        oids=oids, members_known=record["state"] in ("read", "absent"),
                        members_why=record["error"])
    return sources, holdings, record, info, unreadable


def check(args):
    sources, holdings, record, info, unreadable = gather(args)
    entry_docs, sections, findings = [], [], []
    # Every .md file a row refers to by heading, read in one go before any row is judged.
    parsed = {}
    for name in ENTRY_DOCS:
        st, raw, _ = sources[name]
        if st == "read":
            parsed[name] = sections_of(raw.decode("utf-8", "replace"))
    holdings.prefetch(sorted({c for found in parsed.values() for sec in found[:1]
                              for _, value in table_rows(sec)
                              for c, ref in refs_of(value) if wants_heading(c, ref)}))
    for name in ENTRY_DOCS:
        st, raw, note = sources[name]
        doc = {"doc": name, "present": st != "absent", "tracked": name in info["tracked"],
               "link": note if st == "link" else None, "has_section": None}
        entry_docs.append(doc)
        if st == "link":
            findings.append(dict(kind="symlink", doc=name, row=None, path=None, message=(
                "%s is a symlink (to %s): it is not read; the file it points to is checked when "
                "it is an entry document" % (name, note))))
            continue
        if st != "read":
            continue
        found = parsed[name]
        doc["has_section"] = bool(found)
        if not found:
            continue
        if args.rev is None and not doc["tracked"]:
            findings.append(dict(kind="untracked-doc", doc=name, row=None, path=None, message=(
                "%s is not tracked by git: a clean clone would not have this section" % name)))
        if len(found) > 1:
            findings.append(dict(kind="duplicate-section", doc=name, row=None, path=None, message=(
                "%s has %d '## Operate and Rebuild' sections; the first is checked"
                % (name, len(found)))))
        rows, extra, dupes = check_section(found[0], holdings)
        verdict = section_verdict(rows)
        for r in rows:
            for c in r["missing"]:
                kind = ("host-path" if c in r["host_paths"] else
                        "missing-heading" if " \u00a7 " in c else "missing-path")
                note = next((n for n in r["notes"] if n.startswith(c + ": ")), "")
                findings.append(dict(kind=kind, doc=name, row=r["label"], path=c,
                                     message=note[len(c) + 2:] if note else ""))
        for label in extra:
            findings.append(dict(kind="extra-row", doc=name, row=label, path=None, message=(
                "row %r is not one of the six; ignored" % label)))
        for label in dupes:
            findings.append(dict(kind="duplicate-row", doc=name, row=label, path=None, message=(
                "row %r appears more than once; the first is checked" % label)))
        sections.append({"doc": name, "verdict": verdict, "entry": False, "rows": rows,
                         "extra_rows": extra})
    by_doc = {s["doc"]: s for s in sections}
    entry = by_doc.get("CLAUDE.md") or by_doc.get("AGENTS.md")
    if entry is not None:
        entry["entry"] = True
    if "CLAUDE.md" in by_doc and "AGENTS.md" in by_doc:
        findings.append(dict(kind="two-entry-sections", doc="AGENTS.md", row=None, path=None, message=(
            "AGENTS.md carries the section as well; it belongs in CLAUDE.md, so AGENTS.md's is a "
            "second copy: its false claims count, its completeness does not")))
    elif "AGENTS.md" in by_doc and sources["CLAUDE.md"][0] == "read":
        findings.append(dict(kind="section-in-agents", doc="AGENTS.md", row=None, path=None, message=(
            "the section is in AGENTS.md, but this project has a CLAUDE.md, which is where it "
            "belongs (CLAUDE.md, or AGENTS.md where the project has no CLAUDE.md)")))
    verdict = run_verdict(sections, entry)
    listed = {p for p, _ in unreadable}
    for p, why in holdings.unreadable:
        if p not in listed:
            unreadable.append((p, why))
            listed.add(p)
    return {
        "complete_read": not unreadable,
        "rev": info["rev"],
        "commit": info["commit"],
        "source": info["source"],
        "entry_docs": entry_docs,
        "sections": sections,
        "verdict": verdict,
        "record": record,
        "findings": findings,
        "unreadable": [{"path": p, "reason": r} for p, r in unreadable],
    }


def summary_line(res):
    v = res["verdict"]
    if v == NO_SECTION:
        what = ("neither CLAUDE.md nor AGENTS.md has a '## Operate and Rebuild' section: a "
                "counted state, not a defect; a task that touches a running part adds it")
    else:
        parts = []
        for s in res["sections"]:
            done = sum(1 for r in s["rows"] if r["status"] in DONE_STATUSES)
            parts.append("%s %s, %d of %d rows named or none" % (s["doc"], s["verdict"], done,
                                                                  len(ROWS)))
        what = "; ".join(parts)
        if v == CLAIMS_MISSING:
            what += ("; a row names a file git does not hold, a heading that file lacks or a host "
                     "path: name the committed file, commit it, or say `not built yet`")
    return "operations-check: %s - %s; read from %s" % (v, what, res["source"])


def row_line(doc, r):
    detail = ""
    if r["status"] == NAMED:
        detail = ", ".join(r["paths"])
        if r["elsewhere"]:
            detail += "; not checked here: " + ", ".join(r["elsewhere"])
    elif r["status"] in FALSE_STATUSES or r["status"] == UNVERIFIED:
        detail = "; ".join(r["notes"]) if r["notes"] else ""
        if r["status"] == UNVERIFIED and not r["notes"]:
            detail = "no path in it that git can confirm: %s" % shorten(r["value"])
    elif r["status"] == NONE:
        detail = shorten(r["value"])
    return "  %s  %s  %s%s" % (doc, r["label"], r["status"], ("  " + detail) if detail else "")


def record_lines(rec):
    if rec["state"] != "read":
        return ["  record  progress.json %s%s" % (rec["state"],
                                                  (": " + rec["error"]) if rec["error"] else "")]
    out = ["  record  progress.json: %d phases, %d with operations (%d of them none:); "
           "%d terminal tasks, %d with ops:" % (
               rec["phases"], rec["phases_with_operations"], rec["phases_operations_none"],
               rec["terminal_tasks"], rec["terminal_tasks_with_ops"])]
    s = rec["since"]
    if s:
        out.append("  record  since %s: %d phases, %d with operations (%d of them none:), %d "
                   "unplaceable; %d terminal tasks, %d with ops:, %d unplaceable" % (
                       s["at"], s["phases"], s["phases_with_operations"],
                       s["phases_operations_none"], s["phases_unplaceable"], s["terminal_tasks"],
                       s["terminal_tasks_with_ops"], s["tasks_unplaceable"]))
    return out


def shorten(text, n=100):
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[:n - 3] + "..."


# --- output that cannot change the exit code (docs-check's discipline) ------------------------
def _quiet(name):
    try:
        target = getattr(sys, name).fileno()
        fd = os.open(os.devnull, os.O_WRONLY)
        if fd != target:
            os.dup2(fd, target)
            os.close(fd)
    except (OSError, ValueError, AttributeError):
        setattr(sys, name, None)


def _emit(name, text):
    stream = getattr(sys, name)
    if stream is None:
        return False
    try:
        stream.write(text)
        stream.flush()
    except (OSError, ValueError):
        _quiet(name)
        return False
    return True


def _say(text):
    _emit("stderr", text + "\n")


def one_line(exc):
    text = str(exc) if isinstance(exc, CannotCheck) else "%s: %s" % (type(exc).__name__, exc)
    return " ".join(text.split()) or type(exc).__name__


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="operations_check.py",
        description="Check the entry document's '## Operate and Rebuild' section against git, "
                    "and count adoption in progress.json.")
    ap.add_argument("--rev", metavar="REV", help="read one commit's tree, not the working tree")
    ap.add_argument("--since", metavar="INSTANT", type=parse_since,
                    help="also count phases started or created, and tasks completed, at or after "
                         "this UTC instant (2026-11-08T12:00:00Z)")
    ap.add_argument("--json", action="store_true", help="one JSON object on stdout")
    ap.add_argument("-C", metavar="DIR", default=".", dest="cwd", help="run in DIR")
    args = ap.parse_args(argv)
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    try:
        res = check(args)
    except Exception as exc:                    # CannotCheck, or a defect in this checker
        why = one_line(exc)
        if args.json:
            _emit("stdout", json.dumps({"error": why, "rev": args.rev,
                                        "complete_read": False}) + "\n")
        _say("operations-check: cannot check: %s" % why)
        return 2
    if args.json:
        for s in res["sections"]:
            for r in s["rows"]:
                r.pop("notes", None)
        _emit("stdout", json.dumps(res) + "\n")
    else:
        lines = [summary_line(res)]
        for s in res["sections"]:
            lines += [row_line(s["doc"], r) for r in s["rows"]]
        for f in res["findings"]:
            if f["kind"] not in ("missing-path", "missing-heading", "host-path"):  # on their rows
                lines.append("  note  %s  %s" % (f["doc"], f["message"]))
        lines += record_lines(res["record"])
        _emit("stdout", "\n".join(lines) + "\n")
    for u in res["unreadable"]:
        _say("operations-check: cannot read %s: %s" % (u["path"], u["reason"]))
    if res["unreadable"]:
        _say("operations-check: NOT CHECKED: %d file%s could not be read" % (
            len(res["unreadable"]), "" if len(res["unreadable"]) == 1 else "s"))
        return 2
    return EXIT[res["verdict"]]


def run(argv=None):
    """main(), with the exit code kept the check's: a defect anywhere is exit 2, in one line."""
    try:
        return main(argv)
    except SystemExit:
        raise
    except Exception as exc:
        _say("operations-check: cannot check: %s" % one_line(exc))
        return 2


if __name__ == "__main__":
    sys.exit(run())
