# SEOSONA — MASTER VIDEO SPEC
> Bản chuẩn DUY NHẤT cho mọi video faceless SEOSONA (9:16, voice nam Trọng Hữu, light brand).
> Đây là **khung tư duy + rule chặt + policy nền tảng**, KHÔNG phải khuôn cứng. Nội dung quyết định cấu trúc — không bó vào 1 template / 1 số cảnh cố định.

---

## 0. TƯ DUY CỐT LÕI
- **1 video = 1 thông điệp.** Người xem lướt ~1.5s/cảnh — hiểu ngay "cái gì, lợi gì cho tôi".
- **Show, don't tell.** Có dữ liệu thật (số, lệnh, so sánh, screenshot) thì DỰNG ra, đừng chỉ nói.
- **Số liệu THẬT.** Sao GitHub, %, giá → fetch/đối chiếu. Bịa = mất kênh.
- **Đa dạng hình.** 1 video nên có **≥ 3 loại visual khác nhau** (vd bignum + terminal + compare), KHÔNG lặp 1 kiểu.
- **Brand bất biến:** light mode, xanh `#2A5BDA` + coral `#E2724D` + lá `#16A34A`, logo + footer + CTA SEOSONA luôn có; voice/màu/theme do engine khoá — đừng set tay.

---

## 1. ARC LINH HOẠT (không khoá số cảnh — 5 đến 9 cảnh tuỳ nội dung)
Một video tốt đi qua 4 **nhịp** (beat), mỗi nhịp có thể 1–3 cảnh tuỳ độ phức tạp:

1. **HOOK** (1 cảnh) — nỗi đau / con số sốc. Đầy đủ ở frame 0.
2. **GIÁ TRỊ** (1–4 cảnh) — nó là gì + vì sao đáng. Lấy đúng visual cho từng ý: repo, compare, terminal, steps, bignum, stats… Nội dung NHIỀU thì nhiều cảnh, ÍT thì gộp.
3. **PROOF** (0–2 cảnh) — uy tín: sao GitHub, badge giấy phép, benchmark. Bỏ qua nếu không có số thật.
4. **CTA** (1 cảnh) — follow SEOSONA + thử ngay.

→ **CHUẨN BRAND (video-maker_SKILL): 45–60s, 8–12 câu, 8–11 cảnh.** Tin nhanh tối giản 6–7 câu (~30–40s). **Video < 40s là QUÁ NGẮN (vi phạm RULE #8 ≥45s).**

**Quy tắc nhịp:** **VIẾT CÂU ĐẦY ĐỦ** (1 ý trọn vẹn ~12–18 chữ, KHÔNG câu cụt 3–4 chữ) → voice đủ dài, video 45–60s. Mỗi cảnh ~4–6s. Hook đầy đủ ở frame 0 (hero).

---

## 2. KHO COMPONENT (14 loại — chọn tự do, đừng lặp 1 loại)
Đang có trong engine `native_composer` (đều render-safe, pure HTML/CSS):
`bignum` (số to) · `repo` (thẻ GitHub) · `compare` (coral-trái cũ / xanh-phải mới) · `terminal` (lệnh thật) · `steps` (3–4 bước đánh số) · `badges` (nhãn) · `gittree` (git log graph) · `cta` · `stats` (3 thẻ con số) · `quote` (pull-quote lớn) · `tip` (box 💡 ghi nhớ) · `feature` (emoji + tiêu đề + phụ) · **`chart`** (biểu đồ cột — data viz) · **`mockup`** (cửa sổ trình duyệt/dashboard — giả lập screenshot).

**🎨 HERO scene** (chống đơn điệu): bất kỳ cảnh nào đặt `"hero": true` → **nền màu accent đậm full-bleed, chữ trắng** (thay vì nền sáng + card). Dùng cho HOOK để mỗi video mở đầu bằng 1 block màu nổi bật.

**🔁 XOAY ACCENT (chống trùng):** engine tự **xoay bảng màu theo chủ đề** (`accent_shift` auto từ tên output) → **2 video CÙNG template vẫn khác màu** (video A coral-chủ-đạo, video B xanh-chủ-đạo…). Deterministic, không random (an toàn cho HF). Truyền `accent_shift=0/1/2` để ép. → Cùng 1 template KHÔNG còn ra video y hệt.

Chọn theo **bản chất ý**, không theo template:
- Con số đơn/giá/quy mô → `bignum` · nhiều con số (benchmark) → `stats`
- Giới thiệu repo/tool → `repo` · "cũ vs mới" → `compare` · cài/chạy → `terminal`
- Liệt kê bước → `steps` · điểm nổi bật có icon → `feature` · uy tín/đặc điểm → `badges`
- Câu nói/luận điểm (góc nhìn) → `quote` · điều cốt lõi cần nhớ → `tip` · git/commit → `gittree`

*Component đặt ở cảnh 0 hoặc ≥ 2; giữ cảnh 1 là text "bắc cầu". Cần loại CHƯA có (browser/cửa sổ, screenshot thật `shot`, tagcloud, timeline) → ghi lại để bổ sung engine theo cách render-safe (HTML/CSS, KHÔNG inline-SVG / absolute / ảnh lồng scene), đừng ép dữ liệu sai loại.*

### Triết lý TEMPLATE (quan trọng) — KHÔNG khoá cứng
Template **chỉ là mẫu tham khảo**, KHÔNG phải khuôn cứng. Nội dung quyết định frame.
- Frame/cảnh **trùng style** → gom thành 1 template (template giàu frame hơn).
- Style **khác hẳn** → tách template MỚI (đừng gộp bừa).
- **Càng nhiều template khác nhau → video càng phong phú.** Hiện có 9: `repo-showcase`, `tool-walkthrough`, `ai-news-flash`, `resource-list`, `insight-explainer`, `tutorial-gittree`, `benchmark-news` (stats+feature), `opinion-insight` (quote+tip+feature), **`seo-explainer`** (SEO/Marketing).

### Chủ đề SEO/Marketing (domain LÕI của SEOSONA)
SEOSONA là brand SEO/Marketing — engine hợp chủ đề này hơn cả AI/dev. Dùng template `seo-explainer`
hoặc freeform với các component **không phải dev**: `bignum` (traffic/%, thứ hạng) · `compare` (SEO cũ vs
SEO thời AI — đúng slide brand gốc) · `steps` (quy trình SEO) · `feature` (yếu tố ranking, mẹo) · `tip`
(điều cốt lõi) · `stats` (3 chỉ số) · `quote` (góc nhìn). **Tránh** `repo`/`terminal`/`gittree` (đặc thù code).
Chủ đề SEO: Google update, AI Overview/GEO/AEO, E-E-A-T, từ khoá, content, backlink, local SEO, traffic.

**2 cách tạo video (chọn theo nhu cầu):**
1. **Theo template** (nhanh): `make_video_from_template(name, content, dir)` — lấp 1 template có sẵn.
2. **FREEFORM (không khoá template):** `make_video_custom(dir, scenes_spec)` — tự lắp cảnh từ 14 component theo nội dung: component nào, thứ tự nào, mấy cảnh đều do nội dung. `scenes_spec` = list `{"seg","kicker","h1","h2","acc","comp":(kind,data)}`. → Dùng khi nội dung không khớp template nào / muốn mix riêng.

*Component CHƯA có (dashboard nhiều thẻ, mockup/screenshot UI, ảnh, biểu đồ động, hiệu ứng riêng) → bổ sung vào engine theo cách render-safe rồi dùng trong freeform. Đừng ép nội dung vào sai component.*

### Âm thanh (SFX + Voice + BGM)
- **SFX (17 cue):** transition (6 loại xoay vòng) · impact (soft/deep/hit) · ui (positive/click/success/pop/notify) · typing · riser. Engine tự gắn theo component — mỗi loại 1 tiếng riêng, không lặp 1 beep.
- **Mix:** Voice là chủ đạo (luôn rõ). **BGM tự duck dưới voice** (sidechain) — to ở intro/outro/khoảng lặng, nhỏ khi đang nói. Cuối chuỗi có loudnorm -14 LUFS + brickwall limiter (TP < 0, không clip).
- **BGM theo mood:** `music="tech|news|insight"` (thả file royalty-free vào `7_ASSETS/audio/bgm`, map trong `BGM`). ⚠️ Nhạc viral/chart **có bản quyền** → đừng mux vào file (rủi ro tắt tiếng/gỡ, nhất là Ads); dùng sound library của nền tảng cho nhạc hot.

---

## 3. CÁCH VIẾT (nội dung hay hơn)
**HOOK** = câu hỏi nỗi đau HOẶC con số sốc, đủ ở frame 0. Tạo 1 câu hỏi trong đầu người xem.
- ✅ "Trả tiền API AI mỗi tháng có làm bạn mệt mỏi?" · "Chạy mọi model AI mà KHÔNG cần GPU."
- ❌ "Hôm nay mình giới thiệu…", chào hỏi, để con số ở cuối.

**THÂN** — mỗi câu **1 ý, ≤ 16 chữ hiển thị**, văn nói chủ động, có tên riêng + số thật.
- `compare`: trái = cách cũ (3 gạch xấu), phải = sản phẩm (3 điểm thắng — luôn xanh).
- `terminal`: lệnh thật + 1 dòng `ok` kết quả.
- `steps`: 3–4 mục ngắn, song song nhau.

**HEADING 2 TÔNG** — `h1` navy = chủ thể, `h2` accent = điểm chốt; ≤ 4 chữ/dòng.

**CTA** (cố định kiểu): "Vào [tên] để thử ngay. Theo dõi SEOSONA xem thêm thủ thuật." → `Theo dõi SEOSONA / xem thêm mỗi ngày`.

---

## 4. 🔴 RULE CỨNG (vi phạm = LÀM LẠI)
1. **TEXT ≠ PHIÊN ÂM (RULE #1):** chữ trên màn = display form đúng chính tả (`AI`, `GitHub`, `24/7`, `159K`); cách đọc để RIÊNG trong `lexicon`. KHÔNG viết "ây ai" lên màn.
2. **HOOK FULL Ở FRAME 0:** cảnh 0 hiện đủ hook ngay giây 0 (= thumbnail). Engine render cảnh 0 tĩnh.
3. **SỐ LIỆU THẬT:** fetch GitHub / nguồn chính. Không bịa sao, %, giá.
4. **≥ 3 VISUAL KHÁC NHAU/VIDEO:** không lặp 1 component. Tránh video "toàn text".
5. **KARAOKE & TEXT trong VÙNG AN TOÀN:** không sát đáy/cạnh (xem §6 safe zone từng nền tảng).
6. **COMPARE đúng màu:** coral trái (cũ/xấu) / xanh phải (mới/thắng). Không đảo.
7. **CTA SEOSONA** ở cảnh cuối, luôn có.
8. **VERIFY trước khi giao** (đừng bịa): trích frame (`ffmpeg -i v -ss T -frames:v 1`, dùng output-seek hoặc `select`), kiểm tra: không frame đen/trống, loudness ~ -14 LUFS, **True Peak < 0** (không clip), đủ component hiện, độ dài đúng.
9. **TÊN FILE = CAPTION ĐĂNG:** `<hook tiếng Việt CÓ DẤU> #SEOSONA #xuhuong #<chủ đề> (9x16).mp4`. Tránh ký tự cấm `< > : " / \ | ? *`.
10. **SFX ĐA DẠNG:** whoosh chuyển cảnh, impact cho số, gõ phím cho terminal, UI cho badge/CTA (engine tự lo theo component — đừng tắt).

---

## 5. SEO (TikTok / Shorts / Reels)
- **Giữ chân:** hook < 2s; mỗi 3–4s đổi cảnh; không "câu giờ".
- **Từ khoá trong text on-screen** (OCR + người đọc thấy): tên tool + chủ đề (AI, mã nguồn mở, miễn phí) ở heading/kicker.
- **Caption/Title:** `<Tên> — <lợi ích 1 câu có từ khoá>`. Mô tả: 1–2 câu giá trị + link GitHub + "Theo dõi SEOSONA…".
- **Hashtag 5–8:** rộng + ngách. Mặc định `#AI #AITools #congnghe #mannguonmo #SEOSONA` + ngách (`#ClaudeAI #AIAgent #RAG #LLM #vibecoding #opensource`).
- **Hook A/B:** viết 2 hook/chủ đề (nỗi đau · con số · phủ định kỳ vọng · bí mật · so sánh · đối tượng cụ thể). Đăng cái mạnh, giữ cái kia cho lần lặp lại.

---

## 6. 📋 POLICY NỀN TẢNG (PHẢI nắm — tránh bị giảm reach / gỡ / cấm)

### Chung cho cả 3 nền tảng
- **Nội dung gốc / có biến đổi:** KHÔNG repost nguyên video người khác. Ta dựng lại (re-create) theo brand → ổn. Không lấy footage/screenshot có bản quyền vượt fair-use; hiển thị dữ liệu GitHub công khai thì OK.
- **Nhạc có bản quyền:** dùng nhạc trong thư viện của ta (`7_ASSETS/audio/bgm`) hoặc nhạc royalty-free/được cấp phép. Nhạc thương mại (hit) → bị tắt tiếng/gỡ, nhất là khi chạy Ads.
- **Khai báo AI:** voice là TTS AI. Không giả mạo người thật → rủi ro thấp; nhưng nếu nền tảng yêu cầu nhãn "AI-generated/altered" cho nội dung tổng hợp thực tế thì BẬT nhãn đó (TikTok AI-label, YouTube "altered content", Meta AI label).
- **Không watermark nền tảng khác** (logo TikTok/CapCut trên video đăng nơi khác → giảm reach). Xuất bản sạch.
- **Tuyên bố trung thực:** "miễn phí", "159K sao", "nhanh gấp 6 lần" PHẢI đúng sự thật (khớp rule #3). Không clickbait sai.
- **An toàn nội dung:** chủ đề tech/AI của ta vốn ít rủi ro (không bạo lực/người lớn/y tế/chính trị). Tránh: hướng dẫn vượt rào bảo mật/bẻ khoá, tuyên bố tài chính/đầu tư đảm bảo lợi nhuận.

### TikTok
- 9:16 1080×1920; thời lượng tốt nhất 15–60s (hỗ trợ tới 10 phút).
- **Safe zone:** chừa **phải ~120px** (nút like/share), **đáy ~150px** (caption + @handle), **trên ~100px**. → karaoke/footer của ta đã ở giữa-đáy an toàn; giữ text quan trọng trong khung giữa.
- Nhạc: tài khoản business PHẢI dùng **Commercial Music Library**; nhạc hot bị chặn cho mục đích thương mại.
- Branded/Ads: gắn nhãn "Paid partnership"/Spark Ads khi là quảng cáo.
- Link ngoài chỉ ở bio (organic không cho link trong caption).
- Cấm: thông tin sai (y tế/bầu cử), spam "follow for follow", hashtag bị cấm.

### YouTube Shorts
- 9:16; **≤ 3 phút** mới tính Short (ta luôn < 40s → ổn).
- **Safe zone:** chừa **đáy** (tiêu đề + @handle + nút), **phải** (like/dislike/share). Đừng đặt text/CTA quan trọng ở đáy.
- **Originality:** nội dung "reused/lặp lại không biến đổi" KHÔNG được bật kiếm tiền → ta phải tự dựng, thêm giá trị (đang làm đúng).
- Nhạc: YouTube Audio Library hoặc có license; coi chừng Content ID claim.
- Khai báo "altered/synthetic content" nếu thực tế-giả. Metadata/thumbnail không gây hiểu lầm.

### Facebook (Reels / Post / Ads)
- **Reels:** 9:16, tới ~90s. **Post video:** linh hoạt. Tuân Community Standards.
- **Ads (Meta Advertising Policies — chặt nhất):**
  - Không tuyên bố sai/quá mức, không "before/after" phi thực tế, không nhắm "thuộc tính cá nhân" ("bạn đang nợ…"), không clickbait/emoji quá đà.
  - Landing page phải hoạt động, khớp nội dung quảng cáo.
  - Một số ngành cần phép/giới hạn (tài chính, sức khoẻ…). Tech/AI thường OK.
  - Nhạc/footage phải có quyền (Meta Sound Collection cho an toàn).
  - Quảng cáo xã hội/chính trị phải khai báo AI.
- Branded content: dùng nhãn "Paid partnership". Reels nhạc: thư viện được cấp phép; tài khoản business hạn chế nhạc hot.

### Bảng safe-zone nhanh (px trên khung 1080×1920)
| Nền tảng | Trên | Phải | Đáy |
|---|---|---|---|
| TikTok | ~100 | ~120 | ~150 |
| YT Shorts | ~80 | ~110 | ~160 |
| FB Reels | ~90 | ~110 | ~150 |
→ **Giữ chữ quan trọng trong khung an toàn chung: trên 110 / phải 120 / đáy 160.** (Engine để footer/karaoke vùng giữa-đáy; kiểm khi đổi layout.)

---

## 7. PROMPT ĐIỀN SẴN (mỗi video — điền rồi giao Scene-Composer)
```
CHỦ ĐỀ:        <repo URL / tin / khái niệm>
NHỊP DỰ KIẾN:  HOOK + <n cảnh giá trị> + <proof?> + CTA   (5–9 cảnh, theo nội dung)
TEMPLATE:      <repo-showcase | tool-walkthrough | ai-news-flash | resource-list | insight-explainer | tutorial-gittree | hoặc custom scenes>
DỮ LIỆU THẬT:  fetch_github(<repo>)  →  sao/giấy phép/ngôn ngữ
TÊN FILE:      <hook CÓ DẤU> #SEOSONA #xuhuong #<chủ đề> (9x16)

HOOK (×2 để A/B):  1) ...   2) ...
SCRIPT (1 câu/cảnh ≤16 chữ, display form):
  0 [h1 / h2] ...
  ... (đủ cảnh đã chọn)
VISUAL mỗi cảnh:  <bignum | repo | compare | terminal | steps | badges | gittree>  (≥3 loại khác nhau)
DATA:  repo/★/badges = slots (auto) · terminal/compare/steps = tự viết (lệnh/điểm thật)
LEXICON: { "<từ khó>":"<cách đọc>" }   # vd Docker→"đốc cơ", npm→"en pi em"

ĐĂNG:  caption = tên file · hashtag 5–8 · platform: <TikTok/Shorts/Reels> → kiểm safe-zone + nhạc license + nhãn AI nếu cần
```
→ Render: `make_video_from_template(...)` hoặc `python 4_BRAIN/make_video.py <github-url>`.

---

## 8. VÍ DỤ MẪU CHUẨN (đã render đạt)
`9_PROMPTS/video_scripts/`: `local-ai-engine.md` (repo-showcase) · `file-to-markdown.md` (tool-walkthrough) · `leaked-system-prompts.md` (ai-news-flash 6 cảnh) · +3 nữa. Mở để xem 1 kịch bản hoàn chỉnh đúng chuẩn.
