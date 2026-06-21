import os
import sys
import shutil
import subprocess
import json
from datetime import datetime
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from importlib import import_module

def _html_escape(value):
    import html
    return html.escape(str(value), quote=True)

def generate_karaoke_and_timestamps(audio_path, script_text, duration):
    try:
        whisper_engine = import_module('2_SKILLS.srt_maker.whisper_engine')
        words_data = whisper_engine.generate_word_level_data(audio_path)
    except Exception as e:
        print("Whisper failed, estimating words...", e)
        pipeline_mgr = import_module('4_BRAIN.pipeline_manager')
        words_data = pipeline_mgr._estimate_word_level_data_from_script(script_text, duration)

    caption_groups = []
    current_group = []
    group_start = None
    group_end = None

    # We need to extract 8 timestamps based on keywords
    keywords = [
        "engineering", # N1
        "đường", # N2
        "5 nhịp", # N3
        "cấp", # N4 (Cấp độ 1)
        "driven", # N5
        "kiến", # N6 (Kiến trúc)
        "done", # N7 (Definition of Done)
        "cộng" # N8 (Cộng sự)
    ]
    node_starts = {k: None for k in keywords}

    for item in words_data:
        start = max(0.0, float(item.get("start", 0)))
        end = min(duration, start + max(0.04, float(item.get("duration", 0.12))))
        word = str(item.get("word", "")).strip()
        if not word or start >= duration: continue

        # Keyword matching
        lower_word = word.lower()
        for k in keywords:
            if node_starts[k] is None and k in lower_word:
                node_starts[k] = start

        should_flush = (current_group and (len(current_group) >= 5 or end - group_start > 2.0))
        if should_flush:
            caption_groups.append({"words": current_group, "start": group_start, "end": group_end})
            current_group = []
            group_start = None

        if group_start is None: group_start = start
        current_group.append(word)
        group_end = end
    if current_group:
        caption_groups.append({"words": current_group, "start": group_start, "end": group_end})

    tags = []
    for idx, group in enumerate(caption_groups):
        start = max(0.0, float(group["start"]))
        caption_duration = max(0.12, float(group["end"]) - start)
        tags.append(f'''<div class="clip word-box" data-start="{start:.3f}" data-duration="{min(caption_duration, duration - start):.3f}" data-track-index="20">{_html_escape(" ".join(group["words"]))}</div>''')

    # Fill missing node starts with estimates if they weren't found
    final_starts = []
    default_interval = duration / 8
    for i, k in enumerate(keywords):
        t = node_starts[k]
        if t is None: t = i * default_interval
        final_starts.append(t)

    return "\n".join(tags), final_starts

def run():
    text = "Meta mới của AI đang chuyển từ Prompt Engineering sang Loop Engineering. Thiết kế một hệ thống biết tự vận hành, tự kiểm tra và tự sửa sai. Chatbot truyền thống đi theo đường thẳng, nhận yêu cầu rồi trả kết quả. AI Agent thì chạy trong vòng lặp khép kín, tiếp tục hành động cho đến khi đạt mục tiêu hoặc chạm điều kiện dừng. Vòng lặp cốt lõi có 5 nhịp. Perceive để nhận thức mục tiêu, Reason để suy luận, Plan để lập kế hoạch, Act để dùng công cụ và Observe để đọc kết quả. Nếu chưa đạt, nó quay lại và chọn bước tiếp theo. Cấp độ 1 là Agent Look, đọc file, viết code, chạy thử rồi sửa lỗi. Cấp độ 2 là Verification Look, một bộ test hoặc grader chấm kết quả và đẩy phản hồi ngược về Agent nếu chưa đạt. Cấp độ 3 là event-driven loop. Agent được kích hoạt bởi lịch hoặc sự kiện, chẳng hạn tự quét pull request, phân tích vấn đề và giao việc cho các agent con. Các công cụ như MCP và LangGraph đã biến loop thành kiến trúc thực chiến. Một prompt chỉ chạy một lượt. Công việc phức tạp cần nhiều vòng quan sát, hành động và kiểm chứng. Kỹ năng quan trọng vì thế là thiết kế Definition of Done, quản lý context, xử lý ngoại lệ và đặt Termination Logic để agent không chạy vô hạn. Loop tốt không phải Loop lâu mà là Loop biết khi nào đã đủ. Loop chính là cơ chế biến AI từ một kẻ trả lời hay thành cộng sự tự chủ, kiên trì đi đến tận cùng mục tiêu. Và đó là nền móng của phần mềm tự vận hành trong năm 2026."

    project_name = "NEWS_LOOP_8NODES_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    workspace = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '8_WORKSPACE'))
    proj_dir = os.path.join(workspace, project_name)
    os.makedirs(proj_dir, exist_ok=True)

    print(f"=== FULL PIPELINE START: {project_name} ===")

    print("[1] Generating Voice (~1m36s)...")
    tts_engine = import_module('2_SKILLS.tts_generator.tts_engine')
    audio_out = os.path.join(proj_dir, "voice.mp3")
    res = tts_engine.generate_voice_with_subtitles(text, audio_out, voice='vi-VN-NamMinhNeural')

    from moviepy import AudioFileClip
    clip = AudioFileClip(audio_out)
    duration = clip.duration + 2.0
    clip.close()

    print(f"Voice duration: {duration:.2f}s")

    print("[2] Copying Template...")
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '7_ASSETS', 'video_templates', 'seosona-loop-path'))
    render_dir = os.path.join(proj_dir, "hf_render")
    shutil.copytree(template_dir, render_dir)
    os.makedirs(os.path.join(render_dir, "assets"), exist_ok=True)
    shutil.copy2(audio_out, os.path.join(render_dir, "assets", "voice.mp3"))

    print("[3] Generating BGM & Karaoke & Timestamps...")
    bgm_path = os.path.join(render_dir, "assets", "bgm.mp3")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=frequency=110:duration={duration:.3f}", "-f", "lavfi", "-i", f"sine=frequency=165:duration={duration:.3f}", "-filter_complex", f"[0:a][1:a]amix=inputs=2,volume=0.2", bgm_path], check=True)

    karaoke_html, node_starts = generate_karaoke_and_timestamps(audio_out, text, duration)

    index_path = os.path.join(render_dir, "index.html")
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Inject Karaoke
    html = html.replace('<!-- Subtitles injected here via Python -->', karaoke_html)

    # Inject Audio
    audio_tags = f'<audio src="assets/voice.mp3" data-start="0" data-duration="{duration:.3f}" data-track-index="5" data-volume="1"></audio>\n<audio src="assets/bgm.mp3" data-start="0" data-duration="{duration:.3f}" data-track-index="6" data-volume="0.3"></audio>'
    html = html.replace('</body>', f'{audio_tags}\n</body>')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[4] Node Starts Map: {node_starts}")
    print("[5] Rendering Video...")
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    final_output = os.path.join(proj_dir, f"{project_name}.mp4")
    cmd = [
        npx, "--yes", "hyperframes@0.6.112", "render", ".", "--format", "mp4",
        "--var", f"DURATION={duration}",
        "--var", f"N1_START={node_starts[0]}",
        "--var", f"N2_START={node_starts[1]}",
        "--var", f"N3_START={node_starts[2]}",
        "--var", f"N4_START={node_starts[3]}",
        "--var", f"N5_START={node_starts[4]}",
        "--var", f"N6_START={node_starts[5]}",
        "--var", f"N7_START={node_starts[6]}",
        "--var", f"N8_START={node_starts[7]}",
        "--output", final_output
    ]
    subprocess.run(cmd, cwd=render_dir, check=True)
    print(f"=== PIPELINE DONE ===\nVideo saved to: {final_output}")

if __name__ == "__main__":
    run()
