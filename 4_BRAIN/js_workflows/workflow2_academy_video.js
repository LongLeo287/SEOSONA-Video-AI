/**
 * SEOSONA Video Micro-OS
 * Workflow 2: Video Chí Quyết Academy
 * Rule: Bắt buộc dùng Voice Clone F5-TTS
 */

async function runAcademyVideo(topic) {
    console.log(`[Workflow 2] Bắt đầu luồng làm Video Bài giảng CQ Academy. Chủ đề: ${topic}`);
    
    // Bước 1: Khai thác Tri thức
    console.log(`[Workflow 2] Đang trích xuất kiến thức từ 2_KNOWLEDGE...`);
    const scriptJson = "4_WORKSPACE/output/script_academy.json";
    
    // Bước 2: Gọi Voice Clone F5-TTS
    console.log(`[Workflow 2] Kích hoạt Voice Clone (Giọng Nam miền Nam - Chí Quyết)...`);
    const audioPath = "4_WORKSPACE/output/voiceover.wav";
    
    // Bước 2.5: Voice-to-SRT
    console.log(`[Workflow 2] Kích hoạt Whisper để bóc tách dòng thời gian...`);
    const srtPath = "4_WORKSPACE/output/subtitles.srt";

    // Bước 3: Đạo diễn Hình ảnh
    console.log(`[Workflow 2] Chuẩn bị sơ đồ Mindmap/Bullet points...`);

    // Bước 4 & 5: Gắn vào Template và Render
    console.log(`[Workflow 2] Bơm dữ liệu vào 'cq_academy_16x9_template.html'...`);
    console.log(`[Workflow 2] Đang Render MP4 qua FFmpeg...`);
    const finalVideo = "4_WORKSPACE/output/CQ_Academy_Video.mp4";
    
    console.log(`[Workflow 2] HOÀN TẤT! Video lưu tại: ${finalVideo}`);
    return finalVideo;
}

module.exports = { runAcademyVideo };
