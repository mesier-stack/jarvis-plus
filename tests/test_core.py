import tempfile
import unittest
import os
import zipfile
from pathlib import Path
from unittest.mock import patch

from jarvis_core import AIClient, JarvisBrain, MemoryStore, SafeCalculator, SystemActions, VoiceEngine
from updater import _safe_archive_members, version_tuple


class JarvisCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.brain = JarvisBrain(MemoryStore(Path(self.temp.name) / "test.db"))

    def tearDown(self):
        self.temp.cleanup()

    def test_calculator(self):
        self.assertEqual(SafeCalculator.evaluate("(45 * 8) / 3"), 120)

    def test_calculator_rejects_code(self):
        with self.assertRaises(ValueError):
            SafeCalculator.evaluate("__import__('os').system('echo unsafe')")

    def test_note_roundtrip(self):
        self.brain.handle("note buy the Ryzen")
        self.assertIn("buy the Ryzen", self.brain.handle("my notes").text)

    def test_power_requires_confirmation(self):
        reply = self.brain.handle("shutdown")
        self.assertEqual(reply.requires_confirmation, "shutdown")

    def test_natural_open_command(self):
        with patch.object(SystemActions, "open_app", return_value=(True, "Opening calculator.")) as launch:
            reply = self.brain.handle("please open the calculator")
        launch.assert_called_once_with("the calculator")
        self.assertEqual(reply.kind, "action")

    def test_natural_task_first_reminder(self):
        reply = self.brain.handle("perfect now remind me to test jarvis in 1 minute")
        self.assertIn("test jarvis", reply.text.lower())

    def test_learns_and_reuses_correction(self):
        learned = self.brain.handle("teach launch numbers => open calculator")
        self.assertEqual(learned.kind, "learning")
        with patch.object(SystemActions, "open_app", return_value=(True, "Opening calculator.")) as launch:
            reply = self.brain.handle("launch numbers")
        launch.assert_called_once_with("calculator")
        self.assertIn("Learned", reply.text)

    def test_learned_power_command_keeps_confirmation(self):
        self.brain.handle("teach emergency sleep => shutdown")
        reply = self.brain.handle("emergency sleep")
        self.assertEqual(reply.requires_confirmation, "shutdown")

    def test_unknown_attempt_is_recorded(self):
        reply = self.brain.handle("do a totally unknown thing")
        self.assertEqual(reply.kind, "unknown")
        self.assertGreaterEqual(self.brain.memory.learning_stats()[2], 1)

    def test_learning_report(self):
        self.brain.handle("teach launch numbers => open calculator")
        report = self.brain.handle("learning report")
        self.assertIn("1 corrections stored", report.text)

    def test_language_preference_persists(self):
        reply = self.brain.handle("speak Spanish")
        self.assertEqual(reply.voice_language, "es-CL")
        self.assertEqual(self.brain.memory.get_setting("voice_language"), "es-CL")

    def test_bilingual_mode(self):
        self.brain.handle("speak Spanish")
        reply = self.brain.handle("bilingual mode")
        self.assertEqual(reply.voice_language, "auto")
        self.assertEqual(self.brain.memory.get_setting("voice_language"), "auto")

    def test_natural_capabilities_question_works_offline(self):
        reply = self.brain.handle("what you can do")
        self.assertIn("open safe apps", reply.text)
        self.assertNotEqual(reply.kind, "unknown")

    def test_identity_question_works_offline(self):
        reply = self.brain.handle("who are you")
        self.assertIn("JARVIS+", reply.text)

    def test_voice_preview_command(self):
        reply = self.brain.handle("voice test")
        self.assertIn("Voice synthesis online", reply.text)

    def test_fast_voice_setting_persists(self):
        reply = self.brain.handle("voice faster")
        self.assertEqual(reply.voice_speed, "fast")
        self.assertEqual(self.brain.memory.get_setting("voice_speed"), "fast")

    def test_slow_voice_setting_persists(self):
        reply = self.brain.handle("voice slower")
        self.assertEqual(reply.voice_speed, "slow")

    def test_google_ai_studio_key_selects_gemini(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            self.assertEqual(AIClient().provider, "gemini")

    def test_openai_has_priority_when_both_keys_exist(self):
        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "google-test", "OPENAI_API_KEY": "openai-test"},
            clear=True,
        ):
            self.assertEqual(AIClient().provider, "openai")

    def test_elevenlabs_has_voice_priority(self):
        with patch.dict(
            os.environ,
            {"ELEVENLABS_API_KEY": "voice-test", "GEMINI_API_KEY": "chat-test"},
            clear=True,
        ):
            voice = VoiceEngine.__new__(VoiceEngine)
            self.assertEqual(voice.cloud_provider, "elevenlabs")

    def test_version_comparison_parts(self):
        self.assertGreater(version_tuple("3.1.0"), version_tuple("3.0.9"))

    def test_updater_rejects_path_traversal(self):
        archive_path = Path(self.temp.name) / "unsafe.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("../main.py", "bad")
        with zipfile.ZipFile(archive_path) as archive, self.assertRaises(ValueError):
            _safe_archive_members(archive)


if __name__ == "__main__":
    unittest.main()
