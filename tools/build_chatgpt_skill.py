#!/usr/bin/env python3
"""Build portable/chatgpt-skill/crisp from skills/crisp.

ChatGPT has no slash commands, no session hook, and no plugin settings. This
script copies the main skill and replaces the parts that depend on them.
Run it after every change to skills/crisp. The tests fail if the copy is stale.

Usage: python3 tools/build_chatgpt_skill.py
"""
import pathlib
import re
import shutil
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "skills" / "crisp"
DST = ROOT / "portable" / "chatgpt-skill" / "crisp"

DESCRIPTION = (
    'description: Crisp writing rules adapted from ASD-STE100 Simplified Technical English. '
    'Answer first, sentences of 20 words or fewer, plain words, and no missing facts. Use when the user '
    'says "crisp", "be crisp", "crisp on", "clarify", "tldr", "check", "simplify", "plain English", '
    '"explain simply", "STE", "ASD-STE100", or "make this readable", asks for a readability check, asks '
    'for a README, runbook, or other document in Crisp style, or pastes text from another AI and asks '
    'what it means.'
)

JOBS = '''## Jobs

ChatGPT has no slash commands. The user starts each job with a word at the start of the message:

| The user types | Job | Section |
|---|---|---|
| `crisp on` or `be crisp` + a question | Answer mode for the rest of the chat | Parts A to E |
| `crisp strict` | Answer mode plus strict word discipline | Parts A to E, `references/vocabulary.md` section 4 |
| `crisp off` | Stop applying Crisp in this chat | None |
| `clarify` + text or a file | Clarify mode. With no text, rewrite your previous answer. | "Clarify mode" |
| `tldr` + optional text | TL;DR mode. With no text, use your previous answer. | "TL;DR mode" |
| `check` + text or a file | Check mode | "Check mode" |
| A request for a README, runbook, error message, or other document in Crisp style | Docs mode | "Docs mode" |

The user can also upload a file (.md, .txt, .docx) with any of these words. The latest request wins.

| Level | What you apply |
|---|---|
| `lite` (default) | Parts A to E. Domain terms stay. |
| `strict` | Lite, plus the word discipline in `references/vocabulary.md` (section 4). |
| `off` | No Crisp rules. |

'''


def build_skill_md(text):
    text = re.sub(r"^description: .*$", DESCRIPTION, text, count=1, flags=re.M)
    start, end = text.index("## Jobs"), text.index("## Part A")
    text = text[:start] + JOBS + text[end:]
    text = text.replace(
        "1. If you can run Python, run `scripts/crisp_check.py` from the folder of this skill: "
        "`python3 <skill-folder>/scripts/crisp_check.py <file>`. Add `--type doc` for documents. "
        "The script also reads stdin.",
        "1. If you can run Python, save the text to a file and run `scripts/crisp_check.py` from this "
        "skill: `python3 scripts/crisp_check.py text.md`. Add `--type doc` for documents. It needs only "
        "the standard library.")
    text = text.replace(
        "6. End with the score from the script, or a count of violations.",
        "6. End with the score from the script, or a count of violations. Then ask if the user wants "
        "the fixes applied.")
    return text


def main():
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    (DST / "SKILL.md").write_text(build_skill_md((SRC / "SKILL.md").read_text()), encoding="utf-8")
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    with zipfile.ZipFile(dist / "crisp-chatgpt.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(DST.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(DST.parent))
    print(f"Built {DST.relative_to(ROOT)} and dist/crisp-chatgpt.zip")


if __name__ == "__main__":
    main()
