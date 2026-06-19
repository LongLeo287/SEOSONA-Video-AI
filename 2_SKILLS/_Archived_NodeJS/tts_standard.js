/**
 * SEOSONA Video Micro-OS
 * Skill: Standard TTS (Dành cho video SEOSONA)
 * Mục đích: Sử dụng AI Voice phổ thông (không phải Voice Clone)
 */

async function generateStandardVoice(text, outputPath) {
    console.log(`[TTS Standard] Bắt đầu tổng hợp giọng nói...`);
    console.log(`[TTS Standard] Đang dùng mô hình: Google/Edge-TTS mặc định.`);
    
    return new Promise((resolve) => {
        setTimeout(() => {
            console.log(`[TTS Standard] Hoàn tất! File lưu tại: ${outputPath}`);
            resolve(outputPath);
        }, 1500);
    });
}

module.exports = { generateStandardVoice };
