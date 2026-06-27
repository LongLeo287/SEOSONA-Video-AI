---
name: talking-head-video-editor
description: >
  dựng và edit video talking-head, video tự quay, screen-recording hoặc footage thô thành video dọc 9:16 hoặc ngang 16:9 với transcript đã căn chữ, phụ đề karaoke, caption style theo nền tảng, card neon, callout, mockup ui cutaway, nhạc nền, sfx và bước verify trước khi giao. dùng khi user nói edit video, dựng talking-head, làm caption video, thêm phụ đề karaoke, thêm card/callout, dựng video review, hướng dẫn, giới thiệu sản phẩm, app demo, hoặc chỉnh video tự quay bằng edit_footage.py, hyperframes và ffmpeg.
---

# Talking-head Video Editor

## Mục tiêu

Dùng skill này để biến footage tự quay hoặc screen-recording thành video hoàn chỉnh có caption, card, callout, mockup UI, nhạc nền và SFX. Không dùng workflow faceless scene-slides (đó là `seosona-news-maker`), không tự sinh giọng AI, dùng GIỌNG THẬT từ footage.

## Engine thật (đã build trong project)

- **2 script:** `scripts/talking_head_transcribe.py` (= `npm run talkinghead:transcribe`) và `scripts/talking_head_edit.py` (= `npm run talkinghead:edit`). Tái dùng `asr_router` (PhoWhisper) + `native_composer._ffmpeg_bin/_bgm/_sfx` + SFX library.
- **Tỉ lệ:** GIỮ NGUYÊN độ phân giải của footage → tự hỗ trợ **9:16 lẫn 16:9** (không cần cấu hình).
- **Caption:** karaoke `\k` + card render bằng **ASS subtitle**, burn bằng ffmpeg (không cần alpha-render).
- **Đầu ra:** `final.mp4` + ASS bên cạnh. SFX trong `sfx_events.file` nhận **tên gợi nhớ** (`whoosh`/`pop`/`ding`/`success`/`notify`/`swipe`) → tự map vào SFX library; hoặc đường dẫn tuyệt đối.
- Các trường `enter`/`width`/`duration` trong `cards.json` hiện được chấp nhận nhưng chưa dùng (để dành); `--composition` được chấp nhận nhưng bỏ qua.

## Đầu vào cần có

- Footage chính: `.mp4`, ưu tiên 9:16 nếu đăng TikTok/Reels/Shorts; 16:9 nếu đăng YouTube hoặc demo dài.
- Transcript word-level: tạo bằng `npm run talkinghead:transcribe`, sau đó sửa chính tả brand → `words_fixed.json`.
- File cấu hình edit: `cards.json` (footage, caption_bottom, music, music_vol, keywords, cards, sfx_events).
- Tùy chọn (NÂNG CAO, chưa wire sẵn trong repo): screenshot/mockup UI HyperFrames, `capture_shot.ps1` — bỏ qua phần Mục B mockup nếu chưa có công cụ.

## Đầu vào cần có

- Footage chính: `.mp4`, ưu tiên 9:16 nếu đăng TikTok/Reels/Shorts; 16:9 nếu đăng YouTube hoặc demo dài.
- Transcript word-level: tạo từ footage bằng `transcribe_video.py`, sau đó sửa chính tả brand thành `words_fixed.json`.
- File cấu hình edit: `cards.json`, chứa footage, duration, caption zone, music, keyword, cards và sfx_events.
- Tùy chọn: screenshot thật, mockup UI HyperFrames, clip cutaway, logo, asset app, hoặc screen-recording phụ.

## Workflow chuẩn

### 1. Transcribe và sửa transcript

Chạy:

```bash
npm run talkinghead:transcribe -- --video <mp4> --out selfshot
# (= python scripts/talking_head_transcribe.py --video <mp4> --out selfshot)
```

Kết quả chính là `words.json`. Trước khi dựng, luôn tạo `words_fixed.json` bằng cách sửa các lỗi nhận diện phổ biến:

- brand/app: `Cloud` -> `Claude`, `herme` -> `Hermes`, `Chat GBT` -> `ChatGPT`.
- thuật ngữ: giữ dạng hiển thị đúng trên caption, ví dụ `AI`, `24/7`, `9Router`, `email`, `API`.
- số liệu: giữ dạng ngắn, dễ đọc trên màn hình, ví dụ `40`, `24/7`, `3 bước`.

### 2. Chọn style caption trước khi viết cards

Chọn 1 style chính cho toàn video, rồi dùng card/callout để nhấn ý. Không trộn quá nhiều style trong một video ngắn.

| Style | Dùng khi | Quy tắc caption |
|---|---|---|
| `karaoke_neon` | video bán hàng, review app, giới thiệu tool, nội dung cần giữ retention | caption đáy, active word màu vàng, keyword màu accent, chunk 5-7 từ |
| `clean_tutorial` | video hướng dẫn thao tác, demo màn hình, nội dung cần rõ ràng | caption gọn 1-2 dòng, ít hiệu ứng, ưu tiên không che UI |
| `tiktok_bold` | hook mạnh, clip viral, short-form nhanh | chữ to, phrase ngắn 3-5 từ, nhấn động từ/số liệu, card xuất hiện sớm |
| `authority_news` | tin tức, phân tích, cập nhật thị trường | caption chắc, ít bounce, dùng lower-third/card headline thay vì nhiều sticker |
| `review_compare` | so sánh tool, pricing, tính năng, before-after | caption vừa phải, card dạng bullet/compare/stat đúng thời điểm nói |
| `screen_demo` | video app/web có nhiều UI | caption đặt thấp hoặc lệch vùng an toàn, mockup/cutaway full màn, không để card đè UI quan trọng |

Thiết lập mặc định an toàn:

- `caption_bottom`: `380` đến `390` cho 9:16.
- `--caption-chunk`: `6` cho talking-head thường; `4-5` cho TikTok nhanh; `7-8` cho tutorial chậm.
- Keyword trong caption phải khớp từ trong transcript để tô accent ổn định.

### 3. Viết `cards.json`

Template tối thiểu:

```json
{
  "footage": "assets/footage.mp4",
  "duration": 108,
  "caption_bottom": 380,
  "music": "tech",
  "music_vol": 0.10,
  "keywords": ["claude", "hermes", "ai"],
  "cards": [
    {
      "type": "term",
      "title": "Claude là gì?",
      "sub": "AI viết code và xử lý tài liệu",
      "accent": "cyan",
      "enter": "right",
      "left": 600,
      "top": 150,
      "width": 460,
      "t": 2.0,
      "dur": 7.5
    }
  ],
  "sfx_events": [
    {"file": "whoosh.wav", "t": 2.0, "db": -14}
  ]
}
```

Card types chuẩn:

- `term`: giải thích một thuật ngữ, tool, khái niệm hoặc tên brand.
- `bullet`: liệt kê 2-4 ý; dùng `rows` và `cue` để đồng bộ theo từ khóa.
- `stat`: nhấn số liệu, KPI, giá, thời gian, phần trăm, before/after.

Accent chuẩn: `cyan`, `violet`, `gold`, `green`. Dùng 1 accent chính và tối đa 1 accent phụ trong một video để tránh rối.

### 4. Đặt card/callout không đè mặt

- Với talking-head: đặt card ở vùng trống đối diện mặt, thường phía trên vai hoặc bên còn trống của khung hình.
- Mỗi card có một khung giờ riêng; không để nhiều card cùng lúc nếu video ngắn.
- Không để card đè caption, mắt, miệng, UI quan trọng, hoặc sản phẩm chính.
- Nếu dùng mockup/cutaway full màn, không hiện card cùng lúc.
- Card đầu tiên nên xuất hiện trong 1-3 giây đầu nếu video có hook bán hàng hoặc viral.

### 5. Dựng mockup UI động khi video cần demo app

Dùng mockup khi footage chỉ có talking-head nhưng nội dung đang nói về app/web/tool cần minh họa.

Quy trình:

1. Chụp screenshot thật nếu có thể:

```powershell
capture_shot.ps1 -Url <url> -Out <abs.png>
```

Chụp trang chủ hoặc trang public; tránh login page. Nếu gặp 403, captcha, trắng màn, hãy đổi trang hoặc vẽ mockup.

2. Vẽ mỗi UI thành một file HTML HyperFrames riêng: 1080x1920, có `#stage` và `window.__timelines["main"]`.
3. Animation chỉ dùng `tl.set()` và `tl.to()`. Không dùng `tl.call()` vì render-seek có thể không chạy.
4. Hiệu ứng gõ chữ phải pre-bake từng `<span opacity="0">`, rồi bật bằng `tl.set(span,{opacity:1}, t)`.
5. Render mỗi mockup thành clip, sau đó overlay cutaway đúng thời điểm bằng ffmpeg:

```bash
[i]setpts=PTS+START/TB[ci]
overlay=enable='between(t,START,END)'
```

6. Sau khi có `combined_visual`, mux lại giọng gốc rồi chạy `edit_footage.py` để thêm card, karaoke caption và SFX.

Với video demo app, bắt buộc chuẩn bị ít nhất 2-3 mockup hoặc minh họa khác nhau, mỗi tính năng một màn. Không dùng một mockup duy nhất cho cả video.

### 6. Chạy edit footage

Chạy:

```bash
npm run talkinghead:edit -- --spec cards.json --video <mp4> --words words_fixed.json --out final.mp4 --caption-chunk 6
# (= python scripts/talking_head_edit.py --spec cards.json --video <mp4> --words words_fixed.json --out final.mp4 --caption-chunk 6)
```

Không dùng `--post` của scene-slides cho workflow này. Nếu đổi caption/card nhưng không đổi footage, chỉ cần cập nhật `cards.json` hoặc `words_fixed.json` rồi chạy lại lệnh edit.

## Công thức style nhanh

### Talking-head review app

- Style: `karaoke_neon` hoặc `tiktok_bold`.
- Caption: `caption_bottom: 380`, `--caption-chunk 5-6`.
- Card: `term` ở hook, `bullet` cho 3 lợi ích, `stat` cho giá/tốc độ/kết quả.
- SFX: `whoosh` cho card vào, `pop` cho bullet, `ding/success` cho kết quả.

### Tutorial screen-recording

- Style: `clean_tutorial` hoặc `screen_demo`.
- Caption: chunk 6-8 từ, tránh che thanh menu, nút bấm, terminal hoặc form.
- Card: ít, dùng callout đúng chỗ thay vì card lớn.
- Mockup: chỉ overlay khi cần zoom một thao tác quan trọng.

### Video bán hàng/giới thiệu dịch vụ

- Style: `tiktok_bold` cho hook, sau đó `karaoke_neon`.
- Card: hook trong 1-2 giây đầu; card lợi ích xuất hiện khi người nói nhắc đúng ý.
- Caption: keyword accent cho vấn đề, giải pháp, con số, CTA.
- SFX: đa dạng nhưng không dày quá 1 hiệu ứng mỗi 2-4 giây.

### Video phân tích/news

- Style: `authority_news`.
- Card: dùng headline/lower-third, ít chuyển động.
- Caption: nhịp chắc, không dùng quá nhiều emoji hoặc bounce.
- SFX: nhẹ, chủ yếu whoosh/ding ở chuyển ý.

## Quy tắc bắt buộc

1. Chữ trên caption/card phải là dạng hiển thị đúng, không viết phiên âm vào transcript hoặc text màn hình.
2. `caption_bottom` luôn giữ vùng an toàn 380-390 cho 9:16, trừ khi UI bắt buộc phải né khu vực đó.
3. Card, mockup và caption không được đè nhau; mockup cutaway full màn thì không để card cùng lúc.
4. SFX phải đa dạng: `whoosh`, `pop`, `coin`, `ding`, `success`, `notify`, `swipe`; không lặp một tiếng cho mọi sự kiện.
5. Video dài hơn 120 giây phải dùng caption gộp 1 clip nếu pipeline đã vá `build_captions`, để tránh rớt clip.
6. Batch lớn nên chia 6-8 video mỗi session để tránh tràn context hoặc lỗi gateway.
7. Tên file xuất nên là caption đăng có dấu kèm hashtag, ví dụ: `<hook tiếng việt có dấu> #seosonavideo #xuhuong #ai #tool #automation (9x16).mp4`. Không dùng ký tự cấm Windows: `< > : " / \ | ? *`.

## Checklist verify trước khi giao

Luôn verify bằng dữ liệu thật, không đoán:

- Trích frame ở nhiều mốc: đầu video, giữa video, đoạn có card, đoạn có mockup, gần cuối video.
- Kiểm tra frame không đen; nếu đo bằng ffmpeg thì YAVG nên lớn hơn 12.
- Đo loudness gần `-16 LUFS` nếu xuất cho social.
- Xác nhận duration đúng brief và tối thiểu 45 giây nếu video dạng giới thiệu/review chuẩn.
- Xem caption có đúng chính tả brand, số liệu, thuật ngữ và không bị rơi chữ.
- Xem card/mockup không đè mặt, không đè caption, không che UI quan trọng.
- Xác nhận SFX không quá lớn, không lặp đơn điệu và không che giọng nói.

## Không làm trong skill này

- Không tạo faceless scene-slides bằng `build_scene_slides.py`.
- Không tự sinh voice bằng VieNeu/F5 cho video này, trừ khi user yêu cầu workflow voice-over riêng.
- Không dùng text phiên âm để sửa phát âm trong caption.
- Không post-process scene-slides hoặc dùng lệnh dành cho scene-slides lên footage talking-head.
