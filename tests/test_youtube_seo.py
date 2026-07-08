"""Regression test: YouTube chapter timestamps must be valid MM:SS at any duration.

A plain `00:{seconds}` formatter produced invalid markers ('00:72', '00:108') for videos
longer than ~60s, which makes YouTube reject the whole chapter list. SEOSONA ships
course / talking-head / 16:9 videos well over 60s, so this is public-facing metadata.
"""
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "1_AGENTS", "seo_optimizer"))

import youtube_seo as ys  # noqa: E402

_TS = re.compile(r"\b(\d{2}):(\d{2})\b")


class TimestampValidityTests(unittest.TestCase):
    def _timestamps(self, dur):
        md = ys.generate_youtube_metadata("Hook", ["SEO", "traffic"], {}, video_duration=dur)
        return [(int(m.group(1)), int(m.group(2))) for line in md["description"].splitlines()
                for m in [_TS.search(line)] if m and "—" in line]

    def test_seconds_never_exceed_59(self):
        for dur in (30, 60, 90, 120, 240, 600):
            for mm, ss in self._timestamps(dur):
                self.assertLess(ss, 60, f"invalid MM:SS at duration {dur}s: {mm:02d}:{ss:02d}")

    def test_chapters_start_at_zero_and_increase(self):
        for dur in (60, 120, 240):
            secs = [mm * 60 + ss for mm, ss in self._timestamps(dur)]
            self.assertGreaterEqual(len(secs), 3)          # YouTube needs ≥3 chapters
            self.assertEqual(secs[0], 0)                   # first must be 00:00
            self.assertEqual(secs, sorted(secs))           # monotonic
            self.assertEqual(len(secs), len(set(secs)))    # strictly distinct

    def test_mmss_helper(self):
        self.assertEqual(ys._mmss(72), "01:12")
        self.assertEqual(ys._mmss(0), "00:00")
        self.assertEqual(ys._mmss(59), "00:59")
        self.assertEqual(ys._mmss(3600), "60:00")


class TagOrderingTests(unittest.TestCase):
    def test_primary_keyword_is_first_and_present(self):
        # a plain list(set(...)) reorders by hash and could bury/drop the primary keyword
        kws = ["SEO", "traffic", "backlink", "content marketing"]
        md = ys.generate_youtube_metadata("Hook", kws, {}, video_duration=60)
        self.assertEqual(md["tags"][0], "SEO")             # primary keyword survives, first
        for k in kws:
            self.assertIn(k, md["tags"])

    def test_case_insensitive_dedupe_and_cap(self):
        kws = ["SEO", "seo", "Seo"] + [f"kw{i}" for i in range(30)]
        md = ys.generate_youtube_metadata("Hook", kws, {}, video_duration=60)
        self.assertLessEqual(len(md["tags"]), 15)
        self.assertEqual(len([t for t in md["tags"] if t.lower() == "seo"]), 1)  # deduped


class TitleCasingTests(unittest.TestCase):
    def test_acronym_primary_keyword_preserved(self):
        # str.title() would mangle 'SEO' -> 'Seo' in the public title, diluting the exact-match keyword
        md = ys.generate_youtube_metadata("Hook", ["SEO", "traffic"], {}, video_duration=60)
        self.assertTrue(md["title"].startswith("SEO |"), md["title"])

    def test_smart_title_helper(self):
        self.assertEqual(ys._smart_title("SEO"), "SEO")
        self.assertEqual(ys._smart_title("AI"), "AI")
        self.assertEqual(ys._smart_title("content marketing"), "Content Marketing")
        self.assertEqual(ys._smart_title("ChatGPT prompt"), "ChatGPT Prompt")


class TiktokCaptionTests(unittest.TestCase):
    def test_hashtags_survive_a_long_hook(self):
        # the OLD code capped the whole caption at 150 chars and sliced the hashtags (placed last) off
        # the end — killing discovery. A long hook must be trimmed, hashtags + CTA kept.
        r = ys.generate_tiktok_metadata("Cách tối ưu SEO cho website " * 40, ["SEO", "traffic"])
        self.assertLessEqual(len(r["caption"]), 2200)
        for h in r["hashtags"]:
            self.assertIn(h, r["caption"])
        self.assertIn("Click link ở Bio", r["caption"])   # CTA preserved

    def test_short_hook_is_not_truncated(self):
        r = ys.generate_tiktok_metadata("Hook ngắn", ["SEO"])
        self.assertNotIn("...", r["caption"])
        for h in r["hashtags"]:
            self.assertIn(h, r["caption"])


if __name__ == "__main__":
    unittest.main()
