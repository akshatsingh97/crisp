"""Unit tests for skills/crisp/scripts/crisp_check.py. Run: python3 -m unittest discover tests"""
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "crisp" / "scripts" / "crisp_check.py"
sys.path.insert(0, str(SCRIPT.parent))

import crisp_check  # noqa: E402


def rules(text, **kw):
    return [i["rule"] for i in crisp_check.check(text, **kw)["issues"]]


class SentenceRules(unittest.TestCase):
    def test_long_sentence(self):
        text = " ".join(["word"] * 21) + "."
        self.assertIn("B1", rules(text))
        self.assertNotIn("B1", rules(" ".join(["word"] * 20) + "."))

    def test_doc_type_allows_25_words_in_paragraphs_but_20_in_steps(self):
        sentence = " ".join(["word"] * 23) + "."
        self.assertNotIn("B1", rules(sentence, text_type="doc"))
        self.assertIn("B1", rules("1. " + sentence, text_type="doc"))

    def test_parentheses_count_as_one_word(self):
        text = "A cache (a fast copy of data that a program uses many times every second) is fast."
        self.assertEqual(crisp_check.check(text)["longest_sentence_words"], 5)

    def test_banned_modals(self):
        self.assertEqual(rules("You should restart it. It might fail.").count("B6"), 2)
        self.assertNotIn("B6", rules("You must restart it. It can fail."))

    def test_contractions_semicolons_dashes(self):
        found = rules("It doesn't work; it's broken — fix it.")
        self.assertIn("B11", found)
        self.assertIn("B12", found)

    def test_trailing_condition(self):
        self.assertIn("B7", rules("Read the build log if the build fails."))
        self.assertNotIn("B7", rules("If the build fails, read the log."))

    def test_if_meaning_whether_and_quoted_if_are_not_conditions(self):
        self.assertNotIn("B7", rules("A timeout does not tell you if the first request arrived."))
        self.assertNotIn("B7", rules('A conditional answer starts with "Yes, if X".'))

    def test_tldr_is_not_a_semicolon(self):
        self.assertNotIn("B12", rules("Run the TL;DR command."))

    def test_latin_abbreviations(self):
        self.assertIn("B14", rules("Use a tool, e.g. a linter."))


class AnswerShapeRules(unittest.TestCase):
    def test_preamble_only_in_first_sentence(self):
        self.assertIn("A1", rules("Great question! The answer is 4."))
        self.assertNotIn("A1", rules("The answer is 4. Sure, it is simple."))

    def test_closer(self):
        self.assertIn("A11", rules("The answer is 4. Hope this helps!"))

    def test_bold_heading_and_lead_in(self):
        self.assertIn("A8", rules("**How it works**\n\nThe server sends a token."))
        self.assertIn("A8", rules("**Note:** The server sends a token."))

    def test_nested_and_long_lists(self):
        self.assertIn("A5", rules("- one\n  - nested"))
        self.assertIn("A5", rules("\n".join(f"- item {n}" for n in range(9))))


class CompletenessRules(unittest.TestCase):
    def test_bare_yes_is_flagged(self):
        self.assertIn("E2", rules("Yes.\n\nThe retry is safe."))
        self.assertNotIn("E2", rules("Yes, if the request has an idempotency key."))


class WordRules(unittest.TestCase):
    def test_filler_and_inflated_words(self):
        found = rules("We leverage a robust cache.")
        self.assertIn("C1", found)
        self.assertIn("C4", found)

    def test_word_rotation(self):
        self.assertIn("C2", rules("Check the file. Then verify the output."))


class Untouchables(unittest.TestCase):
    def test_code_is_ignored(self):
        text = "Run the script.\n\n```python\n# you should not see this; it's code\nx = 1\n```\n\nIt prints `you'd should`."
        self.assertEqual(crisp_check.check(text)["issues"], [])


class Scoring(unittest.TestCase):
    def test_clean_text_scores_100(self):
        report = crisp_check.check("The server restarts in 2 seconds. If it fails, read the log.")
        self.assertEqual(report["score"], 100)
        self.assertEqual(report["grade"], "A")

    def test_bad_text_scores_low(self):
        bad = ("Great question! You should definitely leverage a robust cache here; it's really "
               "important because it has been shown to seamlessly improve speed. Hope this helps!")
        self.assertLess(crisp_check.check(bad)["score"], 40)


class CommandLine(unittest.TestCase):
    def run_cli(self, *args, stdin=""):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=stdin,
                              capture_output=True, text=True)

    def test_stdin_and_json(self):
        result = self.run_cli("-", "--json", stdin="The answer is 4.")
        self.assertEqual(result.returncode, 0)
        self.assertIn('"score": 100', result.stdout)

    def test_fail_under(self):
        result = self.run_cli("-", "--fail-under", "90", stdin="You should maybe do it; it's fine.")
        self.assertEqual(result.returncode, 1)

    def test_version(self):
        self.assertIn(crisp_check.__version__, self.run_cli("--version").stdout)


if __name__ == "__main__":
    unittest.main()
