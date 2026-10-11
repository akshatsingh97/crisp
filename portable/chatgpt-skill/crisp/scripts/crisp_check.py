#!/usr/bin/env python3
"""Crisp checker: find readability-rule violations in a text.

Rules are adapted from ASD-STE100 Simplified Technical English.
The checker is heuristic. It finds likely problems; a person decides.

Usage:
    python3 crisp_check.py FILE [--type reply|doc] [--max-words 20] [--json] [--fail-under SCORE]
    cat answer.md | python3 crisp_check.py -

Python 3.8+, standard library only.
"""
import argparse
import json
import re
import sys

__version__ = "1.1.0"

# ---------------------------------------------------------------- word lists

MODALS = ["should", "would", "may", "might", "could"]

FILLER = [
    "simply", "just", "basically", "actually", "really", "very", "quite",
    "essentially", "literally", "obviously", "clearly", "seamless", "seamlessly",
    "effortless", "effortlessly", "robust", "powerful", "comprehensive",
    "cutting-edge", "state-of-the-art", "crucial", "crucially", "vital",
    "game-changer", "game-changing", "blazingly",
]

FILLER_PHRASES = [
    "it is worth noting that", "it's worth noting that", "it is important to note that",
    "it's important to note that", "needless to say", "at the end of the day",
    "in today's world", "it goes without saying", "as a matter of fact",
]

SUBSTITUTIONS = {
    "leverage": "use", "leverages": "use", "leveraging": "using", "utilize": "use",
    "utilizes": "use", "utilizing": "using", "utilise": "use", "in order to": "to",
    "prior to": "before", "subsequent to": "after", "ensure": "make sure that",
    "ensures": "makes sure that", "commence": "start", "initiate": "start",
    "terminate": "stop", "obtain": "get", "acquire": "get", "demonstrate": "show",
    "showcase": "show", "facilitate": "help", "facilitates": "helps",
    "numerous": "many", "plethora": "many", "myriad": "many",
    "approximately": "about", "functionality": "function, feature",
    "methodology": "method", "in the event that": "if",
    "due to the fact that": "because", "with regard to": "about",
    "when it comes to": "for", "at this point in time": "now",
    "is able to": "can", "are able to": "can", "has the ability to": "can",
    "enables you to": "you can", "allows you to": "you can",
    "delve into": "examine", "dive into": "examine", "delve": "examine",
    "streamline": "make simpler / faster", "optimize": "make faster (give the number)",
    "a wide range of": "many (or name them)", "out of the box": "by default",
    "under the hood": "internally", "tackle": "fix", "landscape": "area (or name it)",
    "ecosystem": "name the parts", "and/or": "X, Y, or both",
    "set up": "install / configure", "figure out": "find", "find out": "learn",
    "get rid of": "remove", "carry out": "do", "come up with": "make",
}

PREAMBLES = [
    "great question", "good question", "sure", "certainly", "absolutely",
    "of course", "i'd be happy", "i would be happy", "happy to help",
    "let's dive", "let us dive", "let's break", "in this answer", "here's a",
    "here is a", "that's a great", "what a great",
]

CLOSERS = [
    "hope this helps", "i hope this helps", "let me know if", "feel free to",
    "happy to help", "in summary", "in conclusion", "to sum up", "to summarize",
    "happy coding", "good luck",
]

ROTATIONS = [
    ["check", "verify", "confirm", "validate", "ensure"],
    ["config", "configuration", "settings", "options"],
    ["run", "execute", "invoke", "launch"],
    ["error", "issue", "problem", "bug"],
    ["show", "display", "render", "present"],
    ["delete", "remove", "drop", "destroy"],
]

ABBREVIATIONS = ["e.g.", "i.e.", "etc.", "vs.", "viz.", "cf."]

ING_OK = {
    "including", "according", "during", "something", "nothing", "anything",
    "everything", "bring", "string", "thing", "things", "morning", "evening",
    "following", "remaining", "existing", "pending", "using", "king", "ring",
    "spring", "ceiling", "building", "meaning", "warning", "setting", "settings",
}

PASSIVE_SKIP = {
    "need", "needed", "indeed", "red", "bed", "speed", "seed", "feed", "shed",
    "hundred", "open", "often", "even", "seven", "eleven", "when", "then",
    "than", "token", "children", "garden", "kitchen", "golden", "listen",
    "able", "based", "used", "supposed", "interested", "tired", "excited",
    "concerned", "done", "aimed", "located", "allowed", "required", "free",
    "installed", "enabled", "disabled", "finished", "closed",
}

# ---------------------------------------------------------------- parsing

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]+`")
LINK = re.compile(r"\[([^\]]+)\]\([^)]+\)")
URL = re.compile(r"https?://\S+")
PAREN = re.compile(r"\([^()]*\)")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")
HEADING = re.compile(r"^\s*#{1,6}\s")
BOLD_LEADIN = re.compile(r"^\s*(?:[-*+]|\d+[.)])?\s*\*\*[^*]{1,40}?(:\*\*|\*\*\s*[:.\-—])")
BOLD_HEADING = re.compile(r"^\s*(\*\*|__)[^*_]{1,60}\1\s*:?\s*$")
SENT_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[\"'(\[]?[A-Z0-9])")


def protect_abbrev(text):
    for a in ABBREVIATIONS + ["Mr.", "Dr.", "Ms.", "Mrs.", "No.", "approx."]:
        text = text.replace(a, a.replace(".", "․"))  # one-dot leader
    return text


def unprotect(text):
    return text.replace("․", ".")


def clean_inline(line):
    line = INLINE_CODE.sub("CODE", line)
    line = LINK.sub(r"\1", line)
    line = URL.sub("URL", line)
    line = re.sub(r"(\*\*|__|\*|_)(?=\S)(.+?)(?<=\S)\1", r"\2", line)
    return line


def parse_blocks(text):
    """Return a list of blocks: dicts with kind (para|item|heading) and text."""
    blocks = []
    in_fence = False
    para = []
    bullet_run = 0
    meta = {"bold_leadins": [], "nested_items": [], "long_lists": [], "line_count": 0}

    def flush():
        if para:
            blocks.append({"kind": "para", "text": " ".join(para)})
            para.clear()

    for raw in text.splitlines():
        meta["line_count"] += 1
        if FENCE.match(raw):
            in_fence = not in_fence
            flush()
            continue
        if in_fence:
            continue
        line = raw.rstrip()
        if not line.strip():
            flush()
            if bullet_run > 7:
                meta["long_lists"].append(bullet_run)
            bullet_run = 0
            continue
        if line.lstrip().startswith("|"):  # table row
            flush()
            continue
        if line.lstrip().startswith(">"):
            line = line.lstrip()[1:].lstrip()
            if not line:
                continue
        if BOLD_HEADING.match(line):
            meta["bold_leadins"].append(line.strip()[:70])
            flush()
            continue
        if BOLD_LEADIN.match(line):
            meta["bold_leadins"].append(line.strip()[:70])
        if HEADING.match(line):
            flush()
            blocks.append({"kind": "heading", "text": clean_inline(HEADING.sub("", line))})
            continue
        m = LIST_ITEM.match(line)
        if m:
            flush()
            indent = len(m.group(1).expandtabs(4))
            if indent >= 2:
                meta["nested_items"].append(line.strip()[:70])
            if m.group(2) in "-*+":
                bullet_run += 1
            blocks.append({"kind": "item", "text": clean_inline(line[m.end():])})
            continue
        para.append(clean_inline(line.strip()))
    flush()
    if bullet_run > 7:
        meta["long_lists"].append(bullet_run)
    return blocks, meta


def split_sentences(text):
    text = protect_abbrev(text)
    parts = [unprotect(p.strip()) for p in SENT_SPLIT.split(text) if p.strip()]
    return parts


def count_words(sentence):
    s = PAREN.sub(" PAREN ", sentence)  # STE: parenthetical text counts as one word
    tokens = re.findall(r"[A-Za-z0-9][A-Za-z0-9'’\-./%]*", s)
    return len(tokens)


# ---------------------------------------------------------------- checks

def find_all(pattern, text, flags=re.IGNORECASE):
    return [m.group(0) for m in re.finditer(pattern, text, flags)]


BARE_ANSWER = re.compile(r"^\W*(yes|no|yep|nope|correct|right)\W*$", re.I)


def check_sentence(s, max_words, issues, first):
    low = s.lower()
    n = count_words(s)

    def add(rule, msg, severity="error"):
        issues.append({"rule": rule, "severity": severity, "text": s[:140], "message": msg})

    if first and BARE_ANSWER.match(s):
        add("E2", "Bare yes or no. If the answer depends on a condition, put it in the first sentence: \"Yes, if X.\"", "info")

    if n > max_words:
        add("B1", f"{n} words. Maximum is {max_words}. Split the sentence.")
    for w in find_all(r"\b(" + "|".join(MODALS) + r")\b", s):
        add("B6", f'"{w}": use can, must, or will. Or state the fact.')
    for w in find_all(r"\b\w+(n['’]t|['’](re|ve|ll|d|m))\b", s):
        add("B11", f'Contraction "{w}". Write the full form.')
    for w in find_all(r"\b(it|that|there|what|here|let|he|she|who|where)['’]s\b", s):
        add("B11", f'Contraction "{w}". Write the full form.')
    if ";" in re.sub(r"\bTL;DR\b", "TLDR", s, flags=re.I):
        add("B12", "Semicolon. Write two sentences.")
    if "—" in s or " -- " in s or " – " in s:
        add("B12", "Dash between clauses. Write two sentences.")
    for w in find_all(r"\b(has|have|had) been\b|\b(is|are|was|were) being\b|\bwill have\b", s):
        add("B5", f'"{w}": use a simple tense.')
    for m in re.finditer(r"\b(is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(\w+(?:ed|en))\b", s, re.I):
        if m.group(2).lower() not in PASSIVE_SKIP:
            add("B4", f'Possible passive voice: "{m.group(0)}". Say who does the action.', "info")
    for m in re.finditer(r",\s+(\w+ing)\b", s):
        if m.group(1).lower() not in ING_OK:
            add("B5", f'"-ing" verb after a comma: ", {m.group(1)}". Write a new sentence.', "warn")
    unquoted = re.sub(r"\"[^\"]*\"|\u201c[^\u201d]*\u201d", " QUOTE ", low)
    if re.search(r"\b(if|unless)\b", unquoted) and not re.match(r"^\W*(if|unless|when|only if|even if)\b", unquoted):
        words = unquoted.split()
        idx = next((i for i, w in enumerate(words) if w.strip("(,") in ("if", "unless")), 0)
        whether = r"\b(whether|(check|see|ask|know|tell|find out|learn|show|test|decide)( \w+)? if)\b"
        if idx >= 3 and not re.search(whether, unquoted):
            add("B7", "Condition after the main clause. Put the condition first.", "warn")
    for a in ("e.g.", "i.e.", "etc."):
        if a in low:
            add("B14", f'"{a}": write "for example", "that is", or name the items.')
    for w in FILLER:
        if re.search(r"\b" + re.escape(w) + r"\b", low):
            add("C4", f'Filler word "{w}". Delete it or give the fact.', "warn")
    for p in FILLER_PHRASES:
        if p in low.replace("’", "'"):
            add("C4", f'Filler phrase "{p}". Delete it.', "warn")
    for k, v in SUBSTITUTIONS.items():
        if re.search(r"\b" + re.escape(k) + r"\b", low):
            add("C1", f'"{k}" → "{v}".', "warn")
    if first:
        for p in PREAMBLES:
            if low.replace("’", "'").startswith(p):
                add("A1", "Preamble. Start with the answer.")
                break
    for p in CLOSERS:
        if p in low.replace("’", "'"):
            add("A11", f'Closer "{p}". Delete it.', "warn")
    return n


def check(text, max_words=20, text_type="reply", descriptive_words=25):
    """Check text. text_type "reply" uses max_words for every sentence.
    text_type "doc" uses max_words for list items (procedural steps) and
    descriptive_words for paragraphs (descriptive text)."""
    blocks, meta = parse_blocks(text)
    issues = []
    lengths = []
    first = True
    all_words = []

    for b in blocks:
        if b["kind"] == "heading":
            continue
        sentences = split_sentences(b["text"])
        if b["kind"] == "para" and len(sentences) > 6:
            issues.append({"rule": "B3", "severity": "warn", "text": b["text"][:140],
                           "message": f"{len(sentences)} sentences in one paragraph. Maximum is 6."})
        limit = max_words
        if text_type == "doc" and b["kind"] == "para":
            limit = max(max_words, descriptive_words)
        for s in sentences:
            lengths.append(check_sentence(s, limit, issues, first))
            first = False
            all_words.extend(re.findall(r"[a-z]+", s.lower()))

    for line in meta["bold_leadins"]:
        issues.append({"rule": "A8", "severity": "warn", "text": line,
                       "message": "Bold lead-in or bold used as a heading. Remove the bold label."})
    for line in meta["nested_items"]:
        issues.append({"rule": "A5", "severity": "warn", "text": line,
                       "message": "Nested bullet. Use one level of bullets."})
    for n in meta["long_lists"]:
        issues.append({"rule": "A5", "severity": "warn", "text": f"{n} bullets",
                       "message": f"{n} bullets in one list. Maximum is 7."})

    words = set(all_words)
    for group in ROTATIONS:
        used = [w for w in group if w in words]
        if len(used) >= 2:
            issues.append({"rule": "C2", "severity": "info", "text": ", ".join(used),
                           "message": "Different words for one concept. Pick one."})

    total_words = sum(lengths)
    weight = {"error": 1.0, "warn": 0.5, "info": 0.25}
    penalty = sum(weight[i["severity"]] for i in issues)
    per100 = (penalty / total_words * 100) if total_words else 0.0
    score = max(0, round(100 - per100 * 8))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 60 else "D" if score >= 40 else "F"

    return {
        "type": text_type,
        "words": total_words,
        "sentences": len(lengths),
        "avg_sentence_words": round(total_words / len(lengths), 1) if lengths else 0,
        "longest_sentence_words": max(lengths) if lengths else 0,
        "issues": issues,
        "weighted_issues_per_100_words": round(per100, 2),
        "score": score,
        "grade": grade,
    }


def render(report):
    out = []
    out.append(f"Crisp score: {report['score']}/100 (grade {report['grade']})")
    out.append(f"Words: {report['words']}   Sentences: {report['sentences']}   "
               f"Average: {report['avg_sentence_words']} words   "
               f"Longest: {report['longest_sentence_words']} words")
    issues = report["issues"]
    if not issues:
        out.append("No issues found.")
        return "\n".join(out)
    order = {"error": 0, "warn": 1, "info": 2}
    out.append(f"Issues: {len(issues)}")
    out.append("")
    for i in sorted(issues, key=lambda x: (order[x["severity"]], x["rule"])):
        out.append(f"[{i['rule']}] {i['severity'].upper():5} {i['message']}")
        out.append(f"        > {i['text']}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check text against Crisp (ASD-STE100-based) rules.")
    ap.add_argument("file", help="Text or Markdown file. Use - for stdin.")
    ap.add_argument("--type", choices=["reply", "doc"], default="reply",
                    help="reply: 20 words for every sentence. doc: 20 for steps, 25 for descriptive paragraphs.")
    ap.add_argument("--max-words", type=int, default=20, help="Maximum words per sentence (default 20).")
    ap.add_argument("--version", action="version", version="crisp_check " + __version__)
    ap.add_argument("--json", action="store_true", help="Print JSON.")
    ap.add_argument("--fail-under", type=int, default=None, help="Exit 1 if the score is lower.")
    args = ap.parse_args(argv)

    if args.file == "-":
        text = sys.stdin.read()
    else:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()

    report = check(text, args.max_words, args.type)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.json else render(report))
    if args.fail_under is not None and report["score"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
