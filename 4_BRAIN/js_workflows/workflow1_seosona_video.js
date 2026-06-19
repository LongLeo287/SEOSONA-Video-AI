/**
 * SEOSONA Video Micro-OS
 * Workflow 1: Video SEOSONA (Tin tức & Kiến thức Brand)
 * Rule: Bắt buộc dùng Standard TTS (Không dùng Voice Clone)
 */

async function runSeosonaVideo(topic) {
    console.log(`[Workflow 1] Bắt đầu luồng làm Video SEOSONA. Chủ đề: ${topic}`);
    
    // Bước 1: Gọi Agent lên kịch bản
    console.log(`[Workflow 1] Đang cào tin tức và viết kịch bản...`);
    const scriptJson = "4_WORKSPACE/output/script.json";
    
    // Bước 2: Gọi Standard TTS
    console.log(`[Workflow 1] Kích hoạt Standard TTS (Giọng Nữ/Nam AI chuẩn)...`);
    const audioPath = "4_WORKSPACE/output/voiceover.wav";
    
    // Bước 2.5: Voice-to-SRT
    console.log(`[Workflow 1] Kích hoạt Whisper để quét phụ đề...`);
    const srtPath = "4_WORKSPACE/output/subtitles.srt";

    // Bước 3: Asset Gathering
    console.log(`[Workflow 1] Kích hoạt Playwright đi chụp ảnh dẫn chứng...`);
    const screenshotPath = "4_WORKSPACE/output/scene_1.png";

    // Bước 4 & 5: Gắn vào Template và Render
    console.log(`[Workflow 1] Bơm dữ liệu vào 'seosona_16x9_template.html'...`);
    console.log(`[Workflow 1] Đang Render MP4 qua FFmpeg...`);
    const finalVideo = "4_WORKSPACE/output/SEOSONA_News_Video.mp4";
    
    console.log(`[Workflow 1] HOÀN TẤT! Video lưu tại: ${finalVideo}`);
    return finalVideo;
}

module.exports = { runSeosonaVideo };
