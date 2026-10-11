"""Consistency tests for the plugin files. Run: python3 -m unittest discover tests"""
import json
import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "crisp" / "scripts"))

import crisp_check  # noqa: E402


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path} has no frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


class Manifests(unittest.TestCase):
    def test_versions_match(self):
        claude = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
        codex = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text())
        skill = frontmatter(ROOT / "skills" / "crisp" / "SKILL.md")
        self.assertEqual(claude["version"], codex["version"])
        self.assertIn(claude["version"], (ROOT / "skills" / "crisp" / "SKILL.md").read_text())
        self.assertEqual(claude["version"], crisp_check.__version__)
        self.assertEqual(skill["name"], "crisp")
        self.assertIn(f"## {claude['version']}", (ROOT / "CHANGELOG.md").read_text())

    def test_user_config_defaults_are_valid_options(self):
        config = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["userConfig"]
        for key, option in config.items():
            self.assertIn(option["default"], option["options"], key)

    def test_hook_files_exist(self):
        hooks = json.loads((ROOT / "hooks" / "hooks.json").read_text())["hooks"]
        self.assertIn("SessionStart", hooks)
        self.assertIn("Stop", hooks)
        for name in ("session-start.sh", "reply_check.py"):
            self.assertTrue((ROOT / "hooks" / name).is_file(), name)


class Skills(unittest.TestCase):
    def test_every_skill_has_name_and_description(self):
        for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
            fields = frontmatter(path)
            self.assertEqual(fields.get("name"), path.parent.name)
            self.assertTrue(fields.get("description"), path)
            self.assertLessEqual(len(fields["description"]), 1024, path)

    def test_main_skill_does_not_trigger_on_every_answer(self):
        description = frontmatter(ROOT / "skills" / "crisp" / "SKILL.md")["description"]
        self.assertNotIn("any chat answer", description)
        self.assertIn("on-demand", description)

    def test_referenced_files_exist(self):
        text = (ROOT / "skills" / "crisp" / "SKILL.md").read_text()
        for ref in set(re.findall(r"`(references/[\w.-]+|scripts/[\w.-]+)`", text)):
            self.assertTrue((ROOT / "skills" / "crisp" / ref).is_file(), ref)

    def test_chatgpt_copy_is_in_sync(self):
        main = ROOT / "skills" / "crisp"
        copy = ROOT / "portable" / "chatgpt-skill" / "crisp"
        for rel in ("references/docs.md", "references/vocabulary.md", "references/examples.md",
                    "scripts/crisp_check.py"):
            self.assertEqual((main / rel).read_text(), (copy / rel).read_text(), rel)
        sys.path.insert(0, str(ROOT / "tools"))
        import build_chatgpt_skill
        expected = build_chatgpt_skill.build_skill_md((main / "SKILL.md").read_text())
        chatgpt = (copy / "SKILL.md").read_text()
        self.assertEqual(chatgpt, expected, "Run python3 tools/build_chatgpt_skill.py")
        self.assertNotIn("/crisp:", chatgpt)
        self.assertIn("## Part E: Completeness", chatgpt)


class Portable(unittest.TestCase):
    def test_chatgpt_block_fits_the_free_plan_limit(self):
        text = (ROOT / "portable" / "chatgpt-custom-instructions.md").read_text()
        block = re.search(r"```\n(.*?)\n```", text, re.S).group(1)
        self.assertLessEqual(len(block) + 1, 1500)

    def test_full_prompt_fits_the_paid_plan_limit(self):
        text = (ROOT / "portable" / "system-prompt.md").read_text()
        block = re.search(r"## Full prompt.*?```\n(.*?)\n```", text, re.S).group(1)
        self.assertLessEqual(len(block) + 1, 5000)

    def test_every_portable_version_has_completeness_rules(self):
        for name in ("system-prompt.md", "chatgpt-custom-instructions.md", "AGENTS.md"):
            text = (ROOT / "portable" / name).read_text().lower()
            self.assertIn("yes, if", text, name)


if __name__ == "__main__":
    unittest.main()
