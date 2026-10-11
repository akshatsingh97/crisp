"""Tests for hooks/session-start.sh and hooks/reply_check.py. Run: python3 -m unittest discover tests"""
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = ROOT / "hooks"
sys.path.insert(0, str(HOOKS))

import reply_check  # noqa: E402

CLEAN_ENV = {k: v for k, v in os.environ.items()
             if not k.startswith(("CLAUDE_PLUGIN_OPTION_", "CRISP_", "CLAUDE_PLUGIN_DATA"))}

BAD_REPLY = ("Great question! You should definitely leverage a cache here, because it is really important; "
             "it will make things seamlessly faster and it has been proven in many systems that use it "
             "heavily over time. Hope this helps!")
GOOD_REPLY = ("Yes, if each retry sends the same idempotency key. The server returns the first result for a "
              "repeated key. Without a key, a retry can create a second order. Generate one key per order "
              "before the first attempt.")


def session_start(**env):
    result = subprocess.run(["sh", str(HOOKS / "session-start.sh")], capture_output=True, text=True,
                            env={**CLEAN_ENV, **env})
    return result.returncode, result.stdout


class SessionStart(unittest.TestCase):
    def test_default_is_always_lite(self):
        code, out = session_start()
        self.assertEqual(code, 0)
        self.assertIn('mode="always" level="lite"', out)
        self.assertIn("Completeness", out)
        self.assertNotIn('level="strict"', out)

    def test_strict_adds_word_discipline(self):
        _, out = session_start(CRISP_LEVEL="strict")
        self.assertIn('level="strict"', out)

    def test_on_demand_does_not_load_the_rules(self):
        _, out = session_start(CRISP_MODE="on-demand")
        self.assertIn('mode="on-demand"', out)
        self.assertNotIn("Maximum 20 words", out)

    def test_off_prints_nothing(self):
        self.assertEqual(session_start(CRISP_LEVEL="off"), (0, ""))

    def test_plugin_option_wins_over_environment(self):
        _, out = session_start(CLAUDE_PLUGIN_OPTION_MODE="on-demand", CRISP_MODE="always")
        self.assertIn('mode="on-demand"', out)

    def test_output_stays_under_the_hook_limit(self):
        _, out = session_start(CRISP_LEVEL="strict")
        self.assertLess(len(out), 9500)

    def test_first_run_notice_is_shown_once(self):
        with tempfile.TemporaryDirectory() as data:
            _, first = session_start(CLAUDE_PLUGIN_DATA=data)
            payload = json.loads(first)
            self.assertIn("on-demand", payload["systemMessage"])
            self.assertIn("Completeness", payload["hookSpecificOutput"]["additionalContext"])
            _, second = session_start(CLAUDE_PLUGIN_DATA=data)
            self.assertTrue(second.startswith("<crisp"))

    def test_notice_is_shown_again_after_a_mode_change(self):
        with tempfile.TemporaryDirectory() as data:
            session_start(CLAUDE_PLUGIN_DATA=data)
            _, out = session_start(CLAUDE_PLUGIN_DATA=data, CLAUDE_PLUGIN_OPTION_MODE="on-demand")
            self.assertIn("systemMessage", out)


def transcript(*user_messages):
    handle = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for text in user_messages:
        handle.write(json.dumps({"type": "user", "message": {"role": "user", "content": text}}) + "\n")
        handle.write(json.dumps({"type": "assistant", "message": {"role": "assistant",
                                 "content": [{"type": "text", "text": "crisp off"}]}}) + "\n")
    handle.close()
    return handle.name


class ReplyCheck(unittest.TestCase):
    def decide(self, event, mode="always", level="lite", check="notify"):
        return reply_check.decide(event, env_mode=mode, env_level=level, env_check=check)

    def test_notify_on_a_bad_reply(self):
        result = self.decide({"last_assistant_message": BAD_REPLY})
        self.assertIn("systemMessage", result)
        self.assertIn("/crisp:check", result["systemMessage"])

    def test_silent_on_a_good_reply(self):
        self.assertIsNone(self.decide({"last_assistant_message": GOOD_REPLY}))

    def test_silent_on_a_short_reply(self):
        self.assertIsNone(self.decide({"last_assistant_message": "Yes; it's fine."}))

    def test_fix_blocks_once(self):
        result = self.decide({"last_assistant_message": BAD_REPLY}, check="fix")
        self.assertEqual(result["decision"], "block")
        self.assertIn("Keep every fact", result["reason"])
        again = self.decide({"last_assistant_message": BAD_REPLY, "stop_hook_active": True}, check="fix")
        self.assertIsNone(again)

    def test_check_off(self):
        self.assertIsNone(self.decide({"last_assistant_message": BAD_REPLY}, check="off"))

    def test_on_demand_is_silent_until_turned_on(self):
        self.assertIsNone(self.decide({"last_assistant_message": BAD_REPLY}, mode="on-demand"))
        path = transcript("<command-name>/crisp:level</command-name>\n<command-args>lite</command-args>")
        result = self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": path}, mode="on-demand")
        self.assertIn("systemMessage", result)

    def test_session_off_wins_and_assistant_text_is_ignored(self):
        path = transcript("be crisp", "crisp off please")
        self.assertIsNone(self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": path}))
        path = transcript("crisp off", "crisp on")
        self.assertIsNotNone(self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": path}))

    def test_user_opt_out_for_one_reply(self):
        path = transcript("For a style test, ignore any writing rules for this one reply.")
        self.assertIsNone(self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": path}))
        path = transcript("Ignore the writing rules once.", "Now explain caching.")
        self.assertIsNotNone(self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": path}))

    def test_missing_transcript_is_harmless(self):
        result = self.decide({"last_assistant_message": BAD_REPLY, "transcript_path": "/no/such/file"})
        self.assertIsNotNone(result)

    def test_cli_never_fails(self):
        for stdin in ("", "not json", json.dumps({"last_assistant_message": BAD_REPLY})):
            result = subprocess.run([sys.executable, str(HOOKS / "reply_check.py")], input=stdin,
                                    capture_output=True, text=True, env=CLEAN_ENV)
            self.assertEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
