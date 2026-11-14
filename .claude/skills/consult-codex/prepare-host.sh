#!/bin/bash
# prepare-host.sh — make THIS machine able to run the consult loop. Once per machine, like
# syndicate-connect: the material arrives by /distribute-defaults; the settings change happens
# HERE, run by this host's own session, proven before and after.
#
#   bash .claude/skills/consult-codex/prepare-host.sh                 # check only, exit 1 on any failure
#   bash .claude/skills/consult-codex/prepare-host.sh --apply         # write what is missing, then check
#   bash .claude/skills/consult-codex/prepare-host.sh --check-config  # the host-config predicate ALONE:
#                                                                     # reads, never writes, needs no Codex,
#                                                                     # exit 0 prepared / 1 with the reason
#   bash .claude/skills/consult-codex/prepare-host.sh --project <dir> # check C reads <dir>/CLAUDE.md
#   bash .claude/skills/consult-codex/prepare-host.sh --help          # usage; runs nothing, exit 0
# Every argument is read before anything runs: an unknown one is refused with exit 2 and runs
# nothing. Until 2026-11-14 any argument but --apply and --check-config was ignored, so --help ran
# every check, two Codex rounds included (orchestrator-classic's report from the box).
#
# What --apply writes, and nothing else:
#   ~/.codex/config.toml            two lines PREPENDED if absent (never appended — the file opens
#                                   with a [projects] table and an appended key nests into it silently)
#   $CODEX_HOME/skills/syndicate-consult-claude/SKILL.md
#                                   the Codex-side entry (Entry A), rendered from host-entry.SKILL.md
#                                   with the digest of THIS copy's procedure embedded — so a host
#                                   prepared against one version refuses a project carrying another
#
# Four checks, because each catches a failure the others cannot:
#   A  the config predicate (check_config below) — both keys TOP-LEVEL, right values, no nested copy
#   B  synthetic project, CLAUDE.md > 32 KiB, codeword on the LAST line: proves injection AND that
#      project_doc_max_bytes was really raised (the default truncates mid-line, silently)
#   C  a REAL CLAUDE.md: the one of the project this copy serves (the project it is installed in, or
#      --project <dir>), copied ALONE into scratch; Codex quotes its tail without a file read
#   D  the host entry exists and its embedded digest equals this copy's procedure digest
# Correct on ANY host: every path is resolved from $HOME / $CODEX_HOME / this copy's own location,
# and no path of any one host is written here.
#
# Why C reads the served project's file (2026-11-14). It used to take the largest CLAUDE.md one
# level under the home folder: a file of no project being served, chosen by whatever else the home
# folder held. On the box that was the frozen source of a migrated repository under an estate hold,
# which reads as a path fixed into a distributed script. With no project there is no real file, and
# C says so.
# Why a copy, alone: Codex injects ONE instruction file per directory and AGENTS.md wins over the
# CLAUDE.md fallback (measured, codex-cli 0.165.0, 2026-11-14: with both present only AGENTS.md
# arrived). Run in place in a project that carries both, C would test AGENTS.md and fail on a host
# that is prepared. What C proves is unchanged: a real file, at its real size, reaches Codex whole.
#
# Why B and C say when Codex gave NO answer (2026-11-14). On the box both printed "codeword absent:
# ''" and "token ... not in answer: ''" while Codex had failed every run with "Your access token
# could not be refreshed" and written no answer: the empty string was quoted as if Codex had
# answered without the token. `codex login status` said "Logged in" throughout: it reads auth.json
# and does not ask the server (reproduced with a refused refresh token). Absence and ignorance are
# different, and both look empty, so a run with no answer reports Codex's exit status and its own
# reason, and names the remedy when the reason is the sign-in.
#
# A is the ONLY one consult.sh runs (as --check-config). B, C and D stay PREPARATION-ONLY: B and C
# each cost a Codex round, and D belongs to the host-entry contract that consult.sh checks directly
# against the entry file. Task 31.4: consult.sh used to re-implement half of A inline — it asserted
# the fallback key and nothing else, and did it against a hardcoded ~/.codex path that ignored
# $CODEX_HOME — so a host with project_doc_max_bytes left at the 32 KiB default passed preflight and
# then silently truncated every CLAUDE.md the reviewer was given. One predicate, one definition.
set -u
usage(){ cat <<'USAGE'
usage: bash .claude/skills/consult-codex/prepare-host.sh [--apply | --check-config] [--project <dir>]

  (no flag)        check this host; exit 0 prepared, 1 on any failure
  --apply          write what is missing (two Codex config lines, the host entry), then check
  --check-config   check A alone: reads, never writes, needs no Codex; exit 0 prepared / 1 with the reason
  --project <dir>  check C reads <dir>/CLAUDE.md (default: the project this copy is installed in)
  -h, --help       this text; runs nothing

Checks: A the Codex config predicate; B a synthetic CLAUDE.md over 32 KiB reaches Codex whole;
C the served project's own CLAUDE.md reaches Codex whole; D the host entry carries this copy's
procedure digest. B and C each run Codex once. A usage error exits 2 and runs nothing.
USAGE
}
usage_error(){ echo "prepare-host.sh: $1 — nothing was run" >&2; usage >&2; exit 2; }
MODE=check; PROJECT=""
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help) usage; exit 0 ;;
    --apply|--check-config)
      [ "$MODE" = check ] || [ "$MODE" = "${1#--}" ] || usage_error "--apply and --check-config cannot be combined"
      MODE="${1#--}" ;;
    --project)
      { [ $# -ge 2 ] && [ -n "$2" ]; } || usage_error "--project needs a directory"
      PROJECT="$2"; shift ;;
    *) usage_error "unknown argument '$1'" ;;
  esac
  shift
done
if [ -n "$PROJECT" ]; then
  [ -d "$PROJECT" ] || usage_error "--project $PROJECT is not a directory"
  PROJECT="$(cd "$PROJECT" && pwd -P)"
fi
# The copy's own directory, through any symlink (this repository's scripts/prepare-host.sh is one):
# the digest, the host-entry template and the served project are all read from where the copy IS.
SK="$(cd "$(dirname "$(readlink -f "$0")")" && pwd -P)"
# The project this copy serves: --project, else the project it is installed in. A copy outside any
# project's .claude/skills/ serves none, and the engine's own template copy sits in _project-template/,
# which holds no CLAUDE.md: check C says so and names --project, never picks another file.
if [ -z "$PROJECT" ]; then
  case "$SK" in */.claude/skills/consult-codex) PROJECT="${SK%/.claude/skills/consult-codex}" ;; esac
fi
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
CFG="$CODEX_HOME/config.toml"
ENTRY_DIR="$CODEX_HOME/skills/syndicate-consult-claude"; ENTRY="$ENTRY_DIR/SKILL.md"
WANT_FALLBACK='project_doc_fallback_filenames = ["CLAUDE.md"]'
WANT_MAX='project_doc_max_bytes = 262144'

# ---- the host-config predicate: the ONE definition of "this host's Codex config is prepared" ----
# It READS and never writes, needs no Codex and no network, and is the whole of check A below.
# Four conditions, each a failure that really happened:
#   fallback == ["CLAUDE.md"]        without it Codex is never given the project's rules at all
#   max_bytes an int >= 262144       the 32 KiB default truncates MID-LINE, silently
#   both TOP-LEVEL                   a key appended after a [projects] table nests into it and is ignored
#   no nested copy under [projects]  that nesting is what an append produces — name it, so the
#                                    operator is told what happened rather than that "it is missing"
check_config(){
  python3 - "$CFG" <<'TOMLCHECK'
import sys, tomllib, os
cfg = sys.argv[1]
if not os.path.exists(cfg):
    print(f"config absent: {cfg}", file=sys.stderr); sys.exit(1)
try:
    t = tomllib.load(open(cfg, "rb"))
except Exception as e:
    print(f"config does not parse ({cfg}): {e}", file=sys.stderr); sys.exit(1)
fb = t.get("project_doc_fallback_filenames"); mx = t.get("project_doc_max_bytes")
bad = []
if fb != ["CLAUDE.md"]:
    bad.append(f"project_doc_fallback_filenames={fb!r}, want ['CLAUDE.md']")
if isinstance(mx, bool) or not isinstance(mx, int) or mx < 262144:
    bad.append(f"project_doc_max_bytes={mx!r}, want an integer >= 262144 "
               f"(the 32 KiB default truncates a long CLAUDE.md mid-line, silently)")
# BOTH shapes an append produces, and the first draft saw only the second (found by the reviewer,
# cycle 20260825-164306-1335b9f): a key written straight under [projects] is a SCALAR value in
# t["projects"], so a walk that inspects only dict values skips it entirely — and that is the shape
# you get when the file has no [projects."<path>"] sub-table yet, i.e. on a fresh host.
KEYS = {"project_doc_fallback_filenames", "project_doc_max_bytes"}
proj = t.get("projects")
if isinstance(proj, dict):
    direct = sorted(KEYS & set(proj))
    if direct:
        bad.append(f"a copy of {direct[0]} sits DIRECTLY under [projects] — it was appended, not "
                   f"prepended, and Codex ignores it there")
    for k, v in proj.items():
        if isinstance(v, dict) and (KEYS & set(v)):
            bad.append(f"a copy of the key nests inside [projects.{k!r}] — it was appended, not "
                       f"prepended, and Codex ignores it there")
            break
if bad:
    print("; ".join(bad), file=sys.stderr); sys.exit(1)
sys.exit(0)
TOMLCHECK
}

# --check-config: the predicate alone, before anything that writes, spawns Codex, or needs a login.
# consult.sh calls exactly this and quotes the message into its HOST-NOT-PREPARED refusal.
if [ "$MODE" = check-config ]; then
  if M="$(check_config 2>&1)"; then echo "host config ok: $CFG"; exit 0
  else echo "host config NOT prepared: ${M:-unknown}" >&2; exit 1; fi
fi
SCRATCH="${TMPDIR:-/tmp}/prepare-host.$$"
FAIL=0
say()  { printf '  %-46s %s\n' "$1" "$2"; }
fail() { say "$1" "FAIL — $2"; FAIL=1; }
ok()   { say "$1" "ok${2:+ — $2}"; }
trap 'rm -rf "$SCRATCH"' EXIT
mkdir -p "$SCRATCH"
digest(){ sed -n '/<!-- procedure:begin -->/,/<!-- procedure:end -->/p' "$SK/SKILL.md" | sha256sum | cut -c1-16; }

echo "prepare-host on $(hostname) as $USER · skill copy $SK"
command -v codex >/dev/null || { fail "codex on PATH" "not found (non-interactive ssh? use bash -lc)"; exit 1; }
say "codex" "$(codex --version 2>&1)"
# Necessary, not sufficient: this reads auth.json and asks no server, so a sign-in the server no
# longer accepts still says "Logged in". B's Codex run is the proof, and says so when it fails.
codex login status 2>&1 | grep -q 'Logged in' || { fail "codex login" "not logged in — phase 29 route: codex login / --device-auth"; exit 1; }
[ -f "$CFG" ] || { mkdir -p "$CODEX_HOME"; : > "$CFG"; chmod 600 "$CFG"; say "config" "created empty $CFG"; }
D="$(digest)"

# ---------- --apply ----------
if [ "$MODE" = apply ]; then
  python3 - "$CFG" "$WANT_FALLBACK" "$WANT_MAX" <<'PY'
import sys, tomllib, shutil, os, time
cfg, l1, l2 = sys.argv[1:4]
src = open(cfg).read()
top = tomllib.loads(src)               # raises if the file is broken — refuse to touch it then
need = [l for l, k in ((l1, "project_doc_fallback_filenames"), (l2, "project_doc_max_bytes")) if k not in top]
if not need:
    print("  apply: config keys already top-level — nothing to do"); sys.exit(0)
bak = f"{cfg}.bak.{time.strftime('%Y%m%d-%H%M%S')}"
shutil.copy2(cfg, bak)
new = "\n".join(need) + "\n\n" + src
tomllib.loads(new)                      # prove the result parses BEFORE writing it
with open(cfg, "w") as f: f.write(new)
os.chmod(cfg, 0o600)
print(f"  apply: prepended {len(need)} config line(s); backup {bak}")
PY
  [ $? -eq 0 ] || { fail "apply config" "refused (config did not parse?)"; exit 1; }
  if [ -f "$ENTRY" ] && grep -q "Expected procedure digest: \`$D\`" "$ENTRY"; then say "apply" "host entry already at digest $D — nothing to do"
  else mkdir -p "$ENTRY_DIR"; sed -e "s/{{DIGEST}}/$D/g" -e "s/{{INSTALLED_AT}}/$(date -u +%FT%TZ)/" "$SK/host-entry.SKILL.md" > "$ENTRY"; say "apply" "installed $ENTRY at digest $D"; fi
fi

# ---------- A: the config predicate (the same one consult.sh calls) ----------
if M="$(check_config 2>&1)"; then ok "A  config predicate (--check-config)"; else fail "A  config predicate (--check-config)" "$M"; fi

# run_codex <dir> <prompt>: one Codex run, read-only, no MCP, stdin closed. Sets ANS to its last
# message, and NOANS to why there is none (empty when Codex answered). An empty ANS is IGNORANCE:
# it never counts as an answer that lacked the token.
run_codex() {
  local rc why
  rm -f "$SCRATCH/last.md" "$SCRATCH/run.log"
  ( cd "$1" && AWS_CONFIG_FILE=/nonexistent AWS_SHARED_CREDENTIALS_FILE=/nonexistent \
    timeout 240 codex exec -s read-only --skip-git-repo-check -o "$SCRATCH/last.md" "$2" </dev/null >"$SCRATCH/run.log" 2>&1 )
  rc=$?
  ANS="$(cat "$SCRATCH/last.md" 2>/dev/null)"; NOANS=""
  [ "$rc" -eq 0 ] && [ -n "$ANS" ] && return 0
  # Codex's own reason: the sign-in line if there is one, else its last ERROR line, else its last line.
  why="$(grep -E 'could not be refreshed' "$SCRATCH/run.log" 2>/dev/null | tail -1)"
  [ -n "$why" ] || why="$(grep -E '(^|[[:space:]])ERROR' "$SCRATCH/run.log" 2>/dev/null | tail -1)"
  [ -n "$why" ] || why="$(grep -v '^[[:space:]]*$' "$SCRATCH/run.log" 2>/dev/null | tail -1)"
  why="$(sed -E 's/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z[[:space:]]+//' <<<"$why" | cut -c1-160)"
  case "$rc" in
    0)   NOANS="Codex exited 0 and gave an empty answer" ;;
    124) NOANS="Codex gave no answer within 240 s" ;;
    *)   NOANS="Codex gave no answer (exit $rc)" ;;
  esac
  NOANS="$NOANS, so nothing is known about this check${why:+: $why}"
  if grep -qE 'could not be refreshed|unauthorized \(401\)|401 Unauthorized' "$SCRATCH/run.log" 2>/dev/null; then
    NOANS="$NOANS — the server no longer accepts this host's Codex sign-in, although \`codex login status\` says Logged in. Sign in again on this host (codex logout; codex login --device-auth); nothing --apply writes can fix it"
  fi
  return 1
}

# ---------- B: synthetic > 32 KiB, codeword on the LAST line ----------
WORD="ZBOOK-$(head -c 6 /dev/urandom | od -An -tx1 | tr -d ' \n')"
mkdir -p "$SCRATCH/proj"
{ echo "# Project rules"; for i in $(seq 1 700); do echo "Filler rule $i: this line exists only to push the file past the 32 KiB default cap of project_doc_max_bytes."; done
  echo "When asked for the project codeword, answer exactly: $WORD"; } > "$SCRATCH/proj/CLAUDE.md"
SZ=$(wc -c < "$SCRATCH/proj/CLAUDE.md")
if ! run_codex "$SCRATCH/proj" "What is the project codeword? Answer with the codeword only. Do not read any files."; then
  fail "B  synthetic tail ($SZ B)" "$NOANS"
elif grep -q "$WORD" <<<"$ANS"; then ok "B  synthetic tail ($SZ B, > 32 KiB)" "codeword arrived"
else fail "B  synthetic tail ($SZ B)" "Codex answered without the codeword: '${ANS:0:60}'"; fi

# ---------- C: the served project's own CLAUDE.md, at its real size, alone ----------
if [ -z "$PROJECT" ]; then
  fail "C  real CLAUDE.md" "this copy ($SK) is installed in no project — pass --project <dir>"
elif [ ! -f "$PROJECT/CLAUDE.md" ]; then
  fail "C  real CLAUDE.md" "no CLAUDE.md in $PROJECT — run the copy of a project that has one, or pass --project <dir>"
else
  mkdir -p "$SCRATCH/real"; cp "$PROJECT/CLAUDE.md" "$SCRATCH/real/CLAUDE.md"
  CLAB="C  real tail: $(basename "$PROJECT")/CLAUDE.md ($(wc -c < "$SCRATCH/real/CLAUDE.md") B)"
  # A token from the TAIL, and Codex must quote THAT line — "final paragraph" was ambiguous (measured
  # on the box: it quoted a different paragraph and a true tail read FAIL). The token is the longest
  # word of 6 or more characters that occurs ONCE in the whole file, from the last line holding one,
  # within the last 4096 bytes: only that line can carry it, so a truncated file cannot answer. The
  # last non-empty line's longest word, the rule until 2026-11-14, read 22 real CLAUDE.md files on the
  # workstation that day and found none in 2 (a file ending in a code fence, this engine's own among
  # them) and one occurring earlier in the file in 13; this rule found one in all 22, at most 123 B
  # before the end.
  if ! TOKAT="$(python3 - "$SCRATCH/real/CLAUDE.md" 2>&1 <<'PICK'
import re, sys
text = open(sys.argv[1], "rb").read().decode("utf-8", "replace")
lines = text.split("\n")
end = len(text.encode("utf-8")); upto = 0; ends = []
for ln in lines:
    upto += len(ln.encode("utf-8")) + 1
    ends.append(min(upto, end))
for i in range(len(lines) - 1, -1, -1):
    if end - ends[i] > 4096:
        break
    once = [t for t in re.findall(r"[A-Za-z0-9_./-]{6,}", lines[i]) if text.count(t) == 1]
    if once:
        print(max(once, key=len), end - ends[i]); sys.exit(0)
print("no word of 6 or more characters that occurs only once in the file sits in its last 4096 bytes", file=sys.stderr)
sys.exit(1)
PICK
)"; then fail "$CLAB" "${TOKAT:-could not choose a token from its tail}"
  else
    TOK="${TOKAT% *}"; AFTER="${TOKAT##* }"
    if ! run_codex "$SCRATCH/real" "In the project instructions you were given, find the line that contains the exact text \`$TOK\` and quote that whole line verbatim. Do not read any files."; then
      fail "$CLAB" "$NOANS"
    elif grep -qF "$TOK" <<<"$ANS"; then ok "$CLAB" "its tail arrived: '$TOK', once in the file, $AFTER B before its end"
    else fail "$CLAB" "Codex answered without the tail's token '$TOK' ($AFTER B before the end): '${ANS:0:80}'"; fi
  fi
fi

# ---------- D: host entry present, digest matches THIS copy ----------
if [ ! -f "$ENTRY" ]; then fail "D  host entry $ENTRY" "absent — run with --apply"
elif ! grep -q "Expected procedure digest: \`$D\`" "$ENTRY"; then fail "D  host entry digest" "entry carries $(sed -n 's/.*Expected procedure digest: `\([0-9a-f]*\)`.*/\1/p' "$ENTRY" | head -1), this copy is $D — PROCEDURE-DRIFT; run --apply"
else ok "D  host entry syndicate-consult-claude" "digest $D"; fi

[ $FAIL -eq 0 ] && echo "RESULT: host prepared" || echo "RESULT: NOT prepared"
exit $FAIL
