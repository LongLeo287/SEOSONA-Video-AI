import os
import shutil
import re
import json
import html as html_lib
import subprocess
import random

def _json_for_script(value):
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")

def _html_escape(value):
    return html_lib.escape(str(value), quote=True)

def _looks_vietnamese(text):
    return bool(re.search(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]", text, re.IGNORECASE))

def _split_sentences(text):
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    parts = re.split(r"(?<=[.!?。！？])\s+", cleaned)
    return [part.strip(" -") for part in parts if part.strip(" -")]

def _limit_words(text, max_words):
    words = str(text).split()
    if len(words) <= max_words:
        return str(text).strip()
    return " ".join(words[:max_words]).rstrip(",.;:") + "..."

def _extract_stat(text, fallback):
    patterns = [
        r"\b\d+\s?%",
        r"\b\d+[,.]?\d*\s?(?:tỷ|triệu|nghìn|ngàn|billion|million|k)\+?",
        r"\bAI\s?SEO\b",
        r"\b\d{1,2}\s?tháng\s?\d{1,2}\b",
        r"\b20\d{2}\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(0)
    return fallback

def _make_news_scene_copy(script_text, duration):
    sentences = _split_sentences(script_text)
    if not sentences:
        sentences = ["Bản tin SEOSONA hôm nay tập trung vào những thay đổi quan trọng trong AI Search."]

    vietnamese = _looks_vietnamese(script_text)
    if vietnamese:
        scene_templates = [
            ("BẢN TIN SEOSONA", "AI Search đang đổi luật chơi SEO", "Toàn bộ bản tin hôm nay được dựng bằng tiếng Việt, bám theo voice-over và dữ liệu chính.", "2026", "Bối cảnh"),
            ("HÀNH VI TÌM KIẾM", None, None, "60%", "Người dùng đọc tóm tắt AI"),
            ("RỦI RO THƯƠNG HIỆU", None, None, "69%", "AI vẫn có thể giới thiệu đối thủ"),
            ("GOOGLE SEARCH", None, None, "1B+", "Người dùng AI Mode hàng tháng"),
            ("OPENAI", None, None, "18/6", "Cập nhật trải nghiệm hỏi đáp"),
            ("GÓC NHÌN SEOSONA", "KPI mới là visibility trong câu trả lời AI", "Doanh nghiệp cần tối ưu entity, citation, structured data, độ tin cậy và nội dung sẵn sàng cho AI trích dẫn.", "AI SEO", "Lớp vận hành mới"),
        ]
    else:
        scene_templates = [
            ("SEOSONA NEWSROOM", "AI Search is changing SEO", "This video needs a Vietnamese rewrite before Vietnamese TTS is used.", "2026", "Language gate"),
            ("SEARCH BEHAVIOR", None, None, "60%", "Search behavior"),
            ("BRAND RISK", None, None, "69%", "Competitor risk"),
            ("GOOGLE SEARCH", None, None, "1B+", "AI Mode"),
            ("OPENAI", None, None, "18 Jun", "Release update"),
            ("SEOSONA TAKEAWAY", "Visibility inside AI answers is the new KPI", "Entity, citation, structured data and trust now matter in answer engines.", "AI SEO", "Operating layer"),
        ]

    scenes = []
    for idx, source_sentence in enumerate(sentences):
        kicker = f"TIN TỨC SỐ {idx+1}"
        title = _limit_words(source_sentence, 6)
        body = _limit_words(source_sentence, 30)
        stat = _extract_stat(source_sentence, None)
        label = "Điểm đáng chú ý"
        
        mode = "screenshot"
        if stat and idx % 2 == 0:
            mode = "dashboard"
        elif "nguồn" in source_sentence.lower() or "báo cáo" in source_sentence.lower():
            mode = "source-card"
            
        scenes.append({
            "kicker": kicker,
            "title": title,
            "body": body,
            "stat": stat if stat else f"{idx+1:02d}",
            "label": label,
            "mode": mode,
            "source_sentence": source_sentence
        })

    return scenes[:len(sentences)]

def _get_theme_css(theme_name="random"):
    themes = {
        "classic_navy": """
        --bg-color: #1A2DB5;
        --kicker-bg: #BBDEFB;
        --kicker-text: #1A2DB5;
        --text-main: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.85);
        --stat-bg: #ffffff;
        --stat-text: #000000;
        --stat-border: #BBDEFB;
        --word-text: #ffffff;
        --word-shadow: rgba(0, 0, 0, 0.5);
        --overlay-gradient: linear-gradient(to top, rgba(26, 45, 181, 0.9), transparent 40%);
        """,
        "ethereal_glass": """
        --bg-color: #131110;
        --kicker-bg: #ee5422;
        --kicker-text: #f5f2ed;
        --text-main: #f5f2ed;
        --text-secondary: #a6a29e;
        --stat-bg: rgba(27, 25, 24, 0.6);
        --stat-text: #f5f2ed;
        --stat-border: rgba(238, 84, 34, 0.35);
        --word-text: #f5f2ed;
        --word-shadow: rgba(238, 84, 34, 0.35);
        --overlay-gradient: linear-gradient(to top, rgba(19, 17, 16, 0.95), transparent 50%);
        --backdrop-filter: blur(12px);
        """,
        "cyberpunk_neon": """
        --bg-color: #050510;
        --kicker-bg: #00f3ff;
        --kicker-text: #050510;
        --text-main: #ffffff;
        --text-secondary: #b3b3b3;
        --stat-bg: rgba(5, 5, 16, 0.8);
        --stat-text: #ff00ea;
        --stat-border: #00f3ff;
        --word-text: #00f3ff;
        --word-shadow: rgba(255, 0, 234, 0.8);
        --overlay-gradient: linear-gradient(to top, rgba(5, 5, 16, 0.95), transparent 40%);
        """,
        "minimal_clean": """
        --bg-color: #f7f7f8;
        --kicker-bg: #000000;
        --kicker-text: #ffffff;
        --text-main: #111111;
        --text-secondary: #444444;
        --stat-bg: #ffffff;
        --stat-text: #111111;
        --stat-border: #e0e0e0;
        --word-text: #111111;
        --word-shadow: rgba(255, 255, 255, 0.9);
        --overlay-gradient: linear-gradient(to top, rgba(247, 247, 248, 0.95), transparent 40%);
        """
    }
    if theme_name == "random" or theme_name not in themes:
        theme_name = random.choice(list(themes.keys()))
    
    return themes[theme_name]

def write_hyperframes_render_project(render_dir, audio_path, duration, scenes_data, words_data, script_text="", brand="seosona", logo_path="", theme="random"):
    os.makedirs(render_dir, exist_ok=True)
    assets_dir = os.path.join(render_dir, "assets")
    fonts_dir = os.path.join(assets_dir, "fonts")
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(fonts_dir, exist_ok=True)

    audio_ext = os.path.splitext(audio_path)[1] or ".mp3"
    audio_name = f"voice{audio_ext}"
    render_audio_path = os.path.join(assets_dir, audio_name)
    shutil.copy2(audio_path, render_audio_path)

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    font_source = os.path.join(project_root, "7_ASSETS", "brand", "fonts", "Montserrat-Black.ttf")
    if os.path.exists(font_source):
        shutil.copy2(font_source, os.path.join(fonts_dir, "Montserrat-Black.ttf"))

    render_scenes = []
    for idx, scene in enumerate(scenes_data):
        source_path = scene.get("source_path")
        if not source_path or not os.path.exists(source_path):
            continue
        ext = os.path.splitext(source_path)[1] or ".mp4"
        scene_name = f"scene_{idx}{ext}"
        shutil.copy2(source_path, os.path.join(assets_dir, scene_name))
        render_scenes.append({
            "path": f"assets/{scene_name}",
            "start": float(scene.get("start", 0)),
            "duration": max(0.1, float(scene.get("duration", duration))),
            "media_start": max(0.0, float(scene.get("media_start", 0)))
        })

    video_tags = []
    for idx, scene in enumerate(render_scenes):
        video_tags.append(f'''      <video
        id="bg-video-{idx}"
        class="clip bg-video"
        src="{scene["path"]}"
        data-start="{scene["start"]:.3f}"
        data-duration="{scene["duration"]:.3f}"
        data-media-start="{scene["media_start"]:.3f}"
        data-track-index="0"
        muted
        playsinline
      ></video>''')

    source_screenshots = []
    screenshot_env = os.environ.get("SEOSONA_NEWS_SCREENSHOTS", "")
    for raw_path in [item.strip().strip('"') for item in screenshot_env.split(";") if item.strip()]:
        if not os.path.exists(raw_path):
            continue
        ext = os.path.splitext(raw_path)[1] or ".png"
        shot_name = f"source_screenshot_{len(source_screenshots)}{ext}"
        shutil.copy2(raw_path, os.path.join(assets_dir, shot_name))
        source_screenshots.append(f"assets/{shot_name}")

    clean_visuals_class = "clean-visuals" if not video_tags else ""
    overlay_class = "overlay clean-overlay" if not video_tags else "overlay"
    script_is_vietnamese = _looks_vietnamese(script_text)

    if logo_path and os.path.exists(logo_path):
        logo_ext = os.path.splitext(logo_path)[1] or ".png"
        render_logo = f"logo{logo_ext}"
        shutil.copy2(logo_path, os.path.join(assets_dir, render_logo))
        logo_tag = f'<img src="assets/{render_logo}" class="brand-logo" alt="Logo" />'
    else:
        logo_tag = f'<div class="brand-logo-text">{brand.upper()}</div>'

    html_lang = "vi" if script_is_vietnamese else "en"
    scene_timings = []
    transition_timings = []
    scene_tags = ""
    fallback_background = ""
    scene_layer = ""
    bgm_tag = ""
    sfx_tags = []
    
    if not video_tags:
        scene_copy = _make_news_scene_copy(script_text, duration)
        weights = [max(1, len(scene.get("source_sentence", scene.get("title", "x")))) for scene in scene_copy]
        total_weight = sum(weights)
        cursor = 0.0
        scene_edges = [0.0]
        audio_dur = max(1.0, duration - 2.0)
        for w in weights[:-1]:
            dur = float(audio_dur) * w / total_weight
            cursor += dur
            scene_edges.append(round(cursor, 3))
        scene_edges.append(float(duration))
        scene_chunks = []
        for idx, copy in enumerate(scene_copy):
            if idx + 1 >= len(scene_edges):
                break
            start = scene_edges[idx]
            end = scene_edges[idx + 1]
            if end <= start:
                continue
            scene_timings.append({"id": f"news-scene-{idx}", "start": start, "end": end})
            if idx > 0:
                transition_timings.append(max(0.2, start - 0.42))
            mode = copy.get("mode", "headline")
            dashboard_rows = ""
            if mode == "dashboard":
                dashboard_rows = f'''
          <div class="dashboard-panel">
            <div><span>Entity</span><strong>84</strong></div>
            <div><span>Citation</span><strong>72</strong></div>
            <div><span>Trust</span><strong>91</strong></div>
          </div>'''
            elif mode == "screenshot":
                if source_screenshots:
                    shot_src1 = source_screenshots[idx % len(source_screenshots)]
                    shot_src2 = source_screenshots[(idx + 1) % len(source_screenshots)]
                    dashboard_rows = f'''
          <div class="screenshots-container" style="position: relative; width: 100%; height: 460px; margin-top: 20px; z-index: 10;">
            <div class="browser-shot real-shot" style="position:absolute; top: 0; left: 0; z-index:2; transform-origin:center; box-shadow: 0 40px 100px rgba(0,0,0,0.3);">
              <div class="browser-bar"><i></i><i></i><i></i><span>Project Preview</span></div>
              <img src="{_html_escape(shot_src1)}" alt="Source screenshot" />
            </div>
            <div class="browser-shot real-shot" style="position:absolute; top: 80px; left: 80px; z-index:1; opacity:0.6; transform-origin:center; filter:blur(2px); box-shadow: 0 20px 50px rgba(0,0,0,0.2);">
              <div class="browser-bar"><i></i><i></i><i></i><span>Background Context</span></div>
              <img src="{_html_escape(shot_src2)}" alt="Source screenshot" />
            </div>
          </div>'''
                else:
                    dashboard_rows = f'''
          <div class="browser-shot">
            <div class="browser-bar"><i></i><i></i><i></i><span>search.google.com / ai-overview</span></div>
            <div class="browser-line wide"></div>
            <div class="browser-line"></div>
            <div class="browser-line short"></div>
          </div>'''
            elif mode == "source-card":
                dashboard_rows = f'''
          <div class="source-card">
            <span>Nguồn đã kiểm tra</span>
            <strong>Search Engine Land · Google · OpenAI</strong>
          </div>'''
            elif mode == "timeline":
                dashboard_rows = f'''
          <div class="timeline-strip">
            <b>18/6</b><b>19/6</b><b>2026</b>
          </div>'''
            scene_chunks.append(f'''        <section
          id="news-scene-{idx}"
          class="news-scene scene-tone-{idx % 3} mode-{_html_escape(mode)}"
        >
          <div class="scene-kicker">{_html_escape(copy["kicker"])}</div>
          <h1>{_html_escape(copy["title"])}</h1>
          <p>{_html_escape(copy["body"])}</p>
{dashboard_rows}
          <div class="scene-stat">
            <strong>{_html_escape(copy["stat"])}</strong>
            <span>{_html_escape(copy["label"])}</span>
          </div>
        </section>''')
        scene_tags = "\n".join(scene_chunks)
        fallback_background = f'''      <div id="fallback-bg" class="clip fallback-bg" data-start="0" data-duration="{duration:.3f}" data-track-index="0">
        <div class="news-grid"></div>
      </div>'''
        scene_layer = f'''      <div class="scan-line"></div>
      <div class="transition-wipe"></div>
{scene_tags}
      <div class="news-source">{_html_escape("Nguồn: Search Engine Land / Google Search / OpenAI" if script_is_vietnamese else "Sources: Search Engine Land / Google Search / OpenAI")}</div>'''

    caption_groups = []
    current_group = []
    group_start = None
    group_end = None
    for item in words_data:
        start = max(0.0, float(item.get("start", 0)))
        end = min(duration, start + max(0.04, float(item.get("duration", 0.12))))
        word = str(item.get("word", "")).strip()
        if not word or start >= duration:
            continue
        should_flush = (
            current_group
            and (len(current_group) >= 4 or end - group_start > 1.8)
        )
        if should_flush:
            caption_groups.append({
                "words": current_group,
                "start": group_start,
                "end": group_end
            })
            current_group = []
            group_start = None
            group_end = None
        if group_start is None:
            group_start = start
        current_group.append(word)
        group_end = end
    if current_group:
        caption_groups.append({
            "words": current_group,
            "start": group_start,
            "end": group_end
        })

    word_tags = []
    for idx, group in enumerate(caption_groups):
        start = max(0.0, float(group["start"]))
        caption_duration = max(0.12, float(group["end"]) - start)
        word_tags.append(f'''      <div
        id="caption-{idx}"
        class="clip word-box"
        data-start="{start:.3f}"
        data-duration="{min(caption_duration, max(0.04, duration - start)):.3f}"
        data-track-index="20"
      >{_html_escape(" ".join(group["words"]))}</div>''')

    theme_css = _get_theme_css(theme)

    html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>SEOSONA Video Render</title>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>
    <style>
      :root {{
        {theme_css}
      }}
      html, body {{ margin: 0; padding: 0; width: 1080px; height: 1920px; overflow: hidden; background: var(--bg-color); font-family: "Be Vietnam Pro", "MontserratLocal", Arial, sans-serif; }}
      #root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: var(--bg-color); }}
      .brand-logo {{ position: absolute; top: 64px; left: 72px; height: 50px; z-index: 100; background: white; padding: 12px 24px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
      .brand-logo-text {{ position: absolute; top: 64px; left: 72px; font-size: 38px; font-weight: 900; color: var(--text-main); letter-spacing: -1px; z-index: 100; }}
      .fallback-bg {{ position: absolute; inset: 0; background: var(--bg-color); z-index: 0; }}
      .news-grid {{ position: absolute; inset: 0; background-image: radial-gradient(rgba(128, 128, 128, 0.15) 2px, transparent 2px); background-size: 60px 60px; opacity: 0.8; }}
      .news-scene {{ position: absolute; inset: 0; z-index: 2; display: flex; flex-direction: column; justify-content: center; gap: 36px; padding: 140px 72px 300px; box-sizing: border-box; color: var(--text-main); opacity: 0; }}
      .scene-kicker {{ width: fit-content; max-width: 900px; padding: 14px 28px; border-radius: 100px; background: var(--kicker-bg); color: var(--kicker-text); font-size: 26px; font-weight: 800; line-height: 1; text-transform: uppercase; letter-spacing: 1.5px; }}
      .news-scene h1 {{ margin: 0; max-width: 940px; font-size: 82px; font-weight: 800; line-height: 1.1; color: var(--text-main); letter-spacing: -1.5px; }}
      .news-scene p {{ margin: 0; max-width: 900px; font-size: 34px; font-weight: 500; line-height: 1.5; color: var(--text-secondary); }}
      .scene-stat {{ width: 720px; min-height: 230px; padding: 40px; border: 1px solid var(--stat-border); border-radius: 24px; background: var(--stat-bg); color: var(--stat-text); box-shadow: 0 30px 80px rgba(0, 0, 0, 0.25); box-sizing: border-box; backdrop-filter: var(--backdrop-filter, none); }}
      .scene-stat strong {{ display: block; font-size: 92px; font-weight: 900; line-height: 0.9; }}
      .scene-stat span {{ display: block; margin-top: 16px; font-size: 28px; font-weight: 700; line-height: 1.3; color: var(--text-secondary); }}
      .bg-video {{ position: absolute; inset: 0; width: 1080px; height: 1920px; object-fit: cover; z-index: 0; }}
      .overlay {{ position: absolute; inset: 0; z-index: 10; background: var(--overlay-gradient); pointer-events: none; }}
      .word-box {{ position: absolute; left: 50%; bottom: 140px; z-index: 20; width: 940px; transform: translateX(-50%); color: var(--word-text); font-size: 58px; font-weight: 800; line-height: 1.2; text-align: center; text-shadow: 0 8px 24px var(--word-shadow); }}
    </style>
  </head>
  <body>
    <div id="root" class="{clean_visuals_class}" data-composition-id="main" data-start="0" data-duration="{duration:.3f}" data-width="1080" data-height="1920">
      {logo_tag}
{fallback_background}
{scene_layer}
{chr(10).join(video_tags)}
      <audio
        id="voice-audio"
        src="assets/{audio_name}"
        data-start="0"
        data-duration="{duration:.3f}"
        data-track-index="5"
        data-volume="1"
      ></audio>
{bgm_tag}
{chr(10).join(sfx_tags)}
      <div class="{overlay_class}"></div>
{chr(10).join(word_tags)}
      <script>
        window.__timelines = window.__timelines || {{}};
        const tl = gsap.timeline({{ paused: true }});
        const sceneTimings = {_json_for_script(scene_timings)};
        const transitionTimings = {_json_for_script(transition_timings)};
        
        sceneTimings.forEach((scene, index) => {{
          const start = Math.max(0, Number(scene.start) || 0);
          const end = Math.max(start + 0.5, Number(scene.end) || start + 8);
          const root = `#${{scene.id}}`;
          tl.set(root, {{ opacity: 1 }}, start);
          
          if (index === 0) {{
            tl.set(`${{root}} .scene-kicker`, {{ opacity: 1, y: 0 }}, start);
            tl.set(`${{root}} h1`, {{ opacity: 1, y: 0 }}, start);
          }} else {{
            tl.from(`${{root}} .scene-kicker`, {{ y: 34, opacity: 0, duration: 0.58, ease: "power3.out" }}, start + 0.18);
            tl.from(`${{root}} h1`, {{ y: 40, opacity: 0, duration: 0.72, ease: "expo.out" }}, start + 0.34);
          }}
          tl.from(`${{root}} p`, {{ y: 30, opacity: 0, duration: 0.64, ease: "power2.out" }}, start + 0.55);
          tl.from(`${{root}} .scene-stat`, {{ y: 44, scale: 0.94, opacity: 0, duration: 0.66, ease: "back.out(1.7)" }}, start + 0.86);
          if (index < sceneTimings.length - 1) {{
            tl.to(root, {{ opacity: 0, duration: 0.42, ease: "power2.inOut" }}, Math.max(start + 1, end - 0.42));
          }}
        }});
        window.__timelines["main"] = tl;
      </script>
    </div>
  </body>
</html>"""

    index_path = os.path.join(render_dir, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    production_manifest = {
        "language": html_lang,
        "duration": duration,
    }
    with open(os.path.join(render_dir, "production_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(production_manifest, f, ensure_ascii=False, indent=2)
    return render_dir
