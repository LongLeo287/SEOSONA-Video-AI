"""Regression tests for the brand-safety + TTS-normalization gates.

These lock in fixes that are easy to silently regress:
  - content_moderation.off_platform_domain / moderate  (off-platform CTA blocking)
  - the unattributed-stat percentage catch
  - native_composer._vn_normalize  (VietNormalizer scoped to digit tokens so brand
    acronyms like SEO/AI are never mangled to "xơ" / "ét ê o")

All hermetic: content_moderation is pure; VietNormalizer is a local MIT lib (no network).
"""
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "4_BRAIN"))

import content_moderation as cm  # noqa: E402


class OffPlatformCtaTests(unittest.TestCase):
    def test_domain_after_cta_verb_is_blocked(self):
        # each of these is a real off-platform CTA: a non-SEOSONA domain + a CTA verb.
        for t in ["Liên hệ fiverr.com để thuê SEO", "Mua tại shopee-x.vn",
                  "Đặt hàng tại example-store.com", "Nhắn tin cho fanpage-x.com",
                  "Kết nối tại linkedin-x.io", "Tìm tại toptal-x.com", "Truy cập upwork.com ngay"]:
            self.assertTrue(cm.off_platform_domain(t), f"should flag off-platform CTA: {t}")

    def test_neutral_domain_mention_is_not_blocked(self):
        # informational mentions (no CTA verb, not the CTA scene) must pass — no false positives.
        for t in ["fiverr.com là một nền tảng freelance",
                  "Google gọi thuật toán này là RankBrain",
                  "Theo dõi thứ hạng của bạn — báo cáo tại seosona.com"]:  # own domain is safe
            self.assertIsNone(cm.off_platform_domain(t), f"should NOT flag: {t}")

    def test_cta_scene_flags_any_external_domain(self):
        # in the CTA scene, ANY external domain is off-platform even without a verb.
        self.assertTrue(cm.off_platform_domain("example-x.com", is_cta_scene=True))
        self.assertIsNone(cm.off_platform_domain("theo dõi seosona.com", is_cta_scene=True))

    def test_moderate_blocks_off_platform_cta(self):
        r = cm.moderate("Liên hệ fiverr.com để thuê dịch vụ")
        self.assertFalse(r["ok"])
        self.assertTrue(any(f["kind"] == "off-platform-cta" for f in r["flags"]))


class StatModerationTests(unittest.TestCase):
    def test_unattributed_percentage_is_flagged(self):
        # the STAT regex must catch a trailing "%" (an earlier trailing-\b version missed "70%").
        r = cm.moderate("Có tới 70% doanh nghiệp đang làm SEO sai cách")
        self.assertTrue(any(f["kind"] == "unattributed-stat" for f in r["flags"]))

    def test_attributed_stat_passes(self):
        r = cm.moderate("Theo nghiên cứu của Google, 47% người dùng rời trang chậm")
        self.assertFalse(any(f["kind"] == "unattributed-stat" for f in r["flags"]))

    def test_incidental_theo_does_not_count_as_a_source(self):
        # "theo tôi" = "in my opinion", "theo dõi" = "follow" — a bare "theo" is NOT a citation. It must not
        # mark the stat as cited (the old ["theo "] substring silently disabled the whole gate).
        r = cm.moderate("Theo tôi, 70% doanh nghiệp đang làm SEO sai — hãy theo dõi để biết thêm")
        self.assertTrue(any(f["kind"] == "unattributed-stat" for f in r["flags"]))

    def test_social_proof_with_incidental_theo_still_flagged(self):
        r = cm.moderate("Kênh này có 5 triệu lượt xem, theo tôi là rất ấn tượng")
        self.assertTrue(any(f["kind"] == "social-proof" for f in r["flags"]))

    def test_source_word_boundary_not_resource(self):
        # 'resource' / 'outsource' must NOT satisfy the source cue (old substring 'source' did)
        r = cm.moderate("We used this resource to grow 300% last year")
        self.assertTrue(any(f["kind"] == "unattributed-stat" for f in r["flags"]))


class AbsoluteClaimBoundaryTests(unittest.TestCase):
    """'số 1' (an absolute claim) must not match inside a plain number like 'số 10' / 'số 100'."""

    def _claims(self, t):
        return [f["detail"] for f in cm.moderate(t)["flags"] if f["kind"] == "absolute-claim"]

    def test_number_list_not_flagged(self):
        self.assertNotIn("số 1", self._claims("Top số 10 công cụ SEO tốt cho bạn"))
        self.assertNotIn("số 1", self._claims("Có tới số 100 mẹo hữu ích"))

    def test_chac_chan_1000_not_flagged(self):
        self.assertEqual(self._claims("Bạn sẽ có chắc chắn 1000 đồng lãi"), [])

    def test_genuine_absolute_claims_still_flag(self):
        self.assertIn("số 1", self._claims("Chúng tôi là số 1 thị trường"))
        self.assertTrue(self._claims("Sản phẩm tốt nhất hiện nay"))
        self.assertTrue(self._claims("Chúng tôi đảm bảo kết quả"))

    def test_unsafe_term_still_blocks(self):
        self.assertFalse(cm.moderate("Thần dược chữa khỏi mọi bệnh")["ok"])


class VnNormalizeTests(unittest.TestCase):
    """VietNormalizer must be scoped to digit-bearing tokens: numbers normalize, words don't."""

    @classmethod
    def setUpClass(cls):
        import native_composer as nc
        cls.nc = nc
        cls.available = nc._vn_normalize("47%") is not None  # lib present?

    def test_brand_acronyms_survive(self):
        if not self.available:
            self.skipTest("vietnormalizer not installed")
        out = self.nc._vn_normalize("SEO tăng 47% và AI là tương lai")
        self.assertIn("SEO", out)                 # not mangled to "xơ" / "ét ê o"
        self.assertNotIn("xơ", out)
        self.assertIn("phần trăm", out)           # the digit token still normalizes

    def test_pure_text_is_unchanged(self):
        if not self.available:
            self.skipTest("vietnormalizer not installed")
        s = "không có con số nào ở đây"
        self.assertEqual(self.nc._vn_normalize(s), s)

    def test_pron_speaks_seo_correctly(self):
        # end-to-end: the lexicon accent ("séo") + digit-scoping together must yield a correct
        # spoken form for SEO — never the bare-"seo"→"xơ" mangling.
        import re
        import news_video_standards as nvs
        lex = dict(nvs.PRONUNCIATION_LEXICON)
        s = "SEO"
        for k in sorted(lex, key=len, reverse=True):
            s = re.sub(r'(?<![A-Za-z0-9])' + re.escape(k) + r'(?![A-Za-z0-9])', lex[k], s)
        self.assertEqual(s, "séo")                # lexicon value is accented (survives VietNormalizer)
        self.assertNotEqual(s, "seo")


if __name__ == "__main__":
    unittest.main()
