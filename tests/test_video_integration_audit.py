import os
import sys
import tempfile
import unittest


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

from video_integration_audit import run_integration_audit  # noqa: E402


class VideoIntegrationAuditTests(unittest.TestCase):
    def test_audit_reports_ready_core_and_voice_reference_issue(self):
        with tempfile.TemporaryDirectory() as tmp:
            def touch(relative_path, content="x"):
                path = os.path.join(tmp, relative_path)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(content)

            required_files = [
                "system_config.yaml",
                ".agents/skills/hyperframes/SKILL.md",
                ".agents/skills/seosona-news-maker/SKILL.md",
                "6_SOP/HYPERFRAMES_INTEGRATION.md",
                "6_SOP/tech_news_faceless_sop.md",
                "5_FRAMEWORK/news_spatial_hyperframes/index.html",
                "5_FRAMEWORK/news_loop_path_hyperframes/index.html",
                "7_ASSETS/audio/bgm/bgm_tech_ambient.mp3",
                "7_ASSETS/audio/sfx/pops/pop_01.wav",
                "7_ASSETS/audio/sfx/transitions/whoosh_01.wav",
            ]
            for relative in required_files:
                touch(relative)

            touch(
                "system_config.yaml",
                """
profiles:
  seosona:
    voice:
      required_gender: male
      required_accent: southern
      reference_audio: 7_ASSETS/voice/profiles/seosona_male_southern.wav
      fallback_voice: vi-VN-NamMinhNeural
""".strip(),
            )

            hyperframes_source = os.path.join(tmp, "downloads", "hyperframes-main")
            seosona_skill = os.path.join(tmp, "downloads", "seosona-news-maker_SKILL.md")
            touch("downloads/hyperframes-main/README.md", "Write HTML. Render video.")
            touch("downloads/hyperframes-main/package.json", "{\"name\":\"hyperframes-monorepo\"}")
            touch("downloads/seosona-news-maker_SKILL.md", "TEXT/PHU DE != PHIEN AM\nSFX\n")

            result = run_integration_audit(
                project_root=tmp,
                hyperframes_source=hyperframes_source,
                seosona_skill_path=seosona_skill,
            )

            self.assertFalse(result["ok"])
            self.assertTrue(any(check["name"] == "HyperFrames local source" and check["ok"] for check in result["checks"]))
            self.assertTrue(any(check["name"] == "SEOSONA source skill" and check["ok"] for check in result["checks"]))
            self.assertTrue(any(issue["id"] == "SV-INT-VOICE-REFERENCE" for issue in result["issues"]))


if __name__ == "__main__":
    unittest.main()
