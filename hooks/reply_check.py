#!/usr/bin/env python3
"""Crisp Stop hook: check the last answer with the Crisp checker.

Claude Code runs this hook when Claude finishes an answer. The hook reads
the event JSON from stdin and prints at most one JSON object to stdout.

Settings (plugin options in /config, or environment variables):
  mode         always | on-demand      CLAUDE_PLUGIN_OPTION_MODE or CRISP_MODE
  level        lite | strict | off     CLAUDE_PLUGIN_OPTION_LEVEL or CRISP_LEVEL
  reply_check  notify | fix | off      CLAUDE_PLUGIN_OPTION_REPLY_CHECK or CRISP_REPLY_CHECK

Behavior:
  - Does nothing when Crisp is not active for the session. The session level
    comes from the latest "/crisp:level X" or "crisp on|off|lite|strict" that
    the user typed. If there is none, it comes from the mode and level options.
  - Does nothing when the latest user message asks to skip the rules
    ("ignore the writing rules", "no crisp for this one").
  - Does nothing when the answer is short (fewer than MIN_WORDS words of prose)
    or when its score is SCORE_THRESHOLD or more.
  - notify: shows the user a one-line warning (systemMessage). Claude does not see it.
  - fix: asks Claude to rewrite the answer one time (decision "block").
    It never asks twice in a row, because it exits when stop_hook_active is true.
  - Always exits 0. It never breaks a session, even on bad input.
"""
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = pathlib.Path(os.environ.get("CLAUDE_PLUGIN_ROOT") or HERE.parent)
sys.path.insert(0, str(ROOT / "skills" / "crisp" / "scripts"))

MIN_WORDS = 25
SCORE_THRESHOLD = 85
TRANSCRIPT_TAIL_BYTES = 2_000_000

LABELS = {
    "B1": ("sentence over the word limit", "sentences over the word limit"),
    "B6": ("banned modal verb", "banned modal verbs"),
    "B11": ("contraction", "contractions"),
    "B12": ("semicolon or dash", "semicolons or dashes"),
    "B5": ("complex tense", "complex tenses"),
    "B14": ("Latin abbreviation", "Latin abbreviations"),
    "A1": ("preamble", "preambles"),
    "A8": ("bold label", "bold labels"),
    "A11": ("closer", "closers"),
    "A5": ("list problem", "list problems"),
    "C4": ("filler word", "filler words"),
    "C1": ("inflated word", "inflated words"),
}

TOGGLE_PATTERNS = [
    re.compile(r"crisp:level(?:</command-name>)?\s*(?:<command-message>[^<]*</command-message>\s*)?"
               r"(?:<command-args>)?\s*(lite|strict|off|on)\b", re.I),
    re.compile(r"\bcrisp\s+(on|off|lite|strict)\b", re.I),
]


def setting(name, default):
    value = os.environ.get("CLAUDE_PLUGIN_OPTION_" + name.upper()) or os.environ.get("CRISP_" + name.upper())
    return (value or default).strip().lower()


def user_texts(transcript_path):
    """Yield the text of each user message in the transcript, oldest first."""
    try:
        path = pathlib.Path(transcript_path)
        size = path.stat().st_size
        with path.open("rb") as fh:
            if size > TRANSCRIPT_TAIL_BYTES:
                fh.seek(size - TRANSCRIPT_TAIL_BYTES)
                fh.readline()
            data = fh.read().decode("utf-8", "replace")
    except (OSError, TypeError, ValueError):
        return
    for line in data.splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if entry.get("type") != "user":
            continue
        content = (entry.get("message") or {}).get("content")
        if isinstance(content, str):
            yield content
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    yield part.get("text") or ""


OPT_OUT = re.compile(r"\b(ignore|skip|without|no|break)\b[^.\n]{0,40}\b(crisp|writing rules|style rules|the rules|any rules|all rules)\b", re.I)


def session_state(transcript_path):
    """Return (latest level the user asked for or None, True if the latest message opts out)."""
    latest, last_text = None, ""
    for text in user_texts(transcript_path):
        if "<command-name>" not in text and "tool_result" not in text:
            last_text = text
        for pattern in TOGGLE_PATTERNS:
            for match in pattern.finditer(text):
                latest = match.group(1).lower()
    return latest, bool(OPT_OUT.search(last_text))


def session_toggle(transcript_path):
    return session_state(transcript_path)[0]


def crisp_active(mode, level, toggle):
    if toggle is not None:
        return toggle != "off"
    return mode == "always" and level != "off"


def summarize(issues):
    counts = {}
    for issue in issues:
        if issue["rule"] in LABELS and issue["severity"] != "info":
            counts[issue["rule"]] = counts.get(issue["rule"], 0) + 1
    parts = []
    for rule, n in sorted(counts.items(), key=lambda kv: -kv[1])[:3]:
        one, many = LABELS[rule]
        parts.append(f"{n} {one if n == 1 else many}")
    return ", ".join(parts)


def decide(event, env_mode=None, env_level=None, env_check=None):
    """Return the JSON object to print, or None. Pure function for tests."""
    check_mode = env_check or setting("reply_check", "notify")
    if check_mode not in ("notify", "fix"):
        return None
    if event.get("stop_hook_active"):
        return None
    mode = env_mode or setting("mode", "always")
    level = env_level or setting("level", "lite")
    toggle, opted_out = session_state(event.get("transcript_path"))
    if opted_out or not crisp_active(mode, level, toggle):
        return None
    reply = event.get("last_assistant_message") or ""
    if not isinstance(reply, str) or not reply.strip():
        return None

    import crisp_check  # imported late so that a missing file cannot break the hook

    report = crisp_check.check(reply)
    if report["words"] < MIN_WORDS or report["score"] >= SCORE_THRESHOLD:
        return None
    summary = summarize(report["issues"]) or "several rule problems"
    if check_mode == "notify":
        return {"systemMessage": f"Crisp check: {report['score']}/100 ({summary}). Run /crisp:check for details."}
    return {
        "decision": "block",
        "reason": (
            f"Crisp reply check: your last answer scored {report['score']}/100 ({summary}). "
            "Write the answer again with the Crisp rules. Keep every fact, number, caveat, "
            "step, and code block (completeness rules E1 to E8). Add no new content. "
            "Do not mention this check."
        ),
    }


def main():
    try:
        event = json.loads(sys.stdin.read() or "{}")
        result = decide(event)
        if result:
            print(json.dumps(result))
    except Exception as error:  # noqa: BLE001 - a hook must never break the session
        print(f"crisp reply check skipped: {error}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
