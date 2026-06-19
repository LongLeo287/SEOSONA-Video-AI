const { chromium } = require('playwright');
const ffmpeg = require('fluent-ffmpeg');
const path = require('path');
const fs = require('fs');

async function renderVideo(htmlFilePath, outputVideoPath, fps = 30, duration = 10, width = 1080, height = 1920) {
    console.log(`[HTML Renderer] Starting render for ${htmlFilePath}`);
    console.log(`[HTML Renderer] Output: ${outputVideoPath} | Duration: ${duration}s | FPS: ${fps}`);

    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width, height } });

    // Open file
    await page.goto(`file://${path.resolve(htmlFilePath)}`, { waitUntil: 'networkidle' });

    // Inject a script to pause all animations and manually step them
    await page.evaluate(() => {
        // We pause all animations.
        // And we will provide a global function to advance time.
        window.setAnimationTime = (timeMs) => {
            const anims = document.getAnimations();
            for (let a of anims) {
                a.pause();
                a.currentTime = timeMs;
            }
            // If using Remotion or similar JS frameworks, they can hook into window.setAnimationTime
            if (window.onTimeUpdate) {
                window.onTimeUpdate(timeMs);
            }
        };
        // Disable transitions to snap immediately
        const style = document.createElement('style');
        style.innerHTML = `* { transition: none !important; }`;
        document.head.appendChild(style);
    });

    const totalFrames = fps * duration;
    
    // Set up ffmpeg to read from stdin
    const ffmpegCmd = ffmpeg()
        .input('pipe:0')
        .inputFormat('image2pipe')
        .inputOptions([
            `-framerate ${fps}`,
        ])
        .outputOptions([
            '-vcodec qtrle', // Apple Animation codec supports Alpha channel!
            '-pix_fmt argb'
        ])
        .output(outputVideoPath)
        .on('end', () => console.log('[HTML Renderer] FFmpeg encoding finished.'))
        .on('error', (err) => console.error('[HTML Renderer] FFmpeg error:', err.message));

    // The stream to pipe into ffmpeg
    const stdin = ffmpegCmd.pipe();

    for (let frame = 0; frame < totalFrames; frame++) {
        const timeMs = (frame / fps) * 1000;
        
        await page.evaluate((t) => window.setAnimationTime(t), timeMs);
        
        // Wait a tiny bit for layout calculation if needed
        await page.waitForTimeout(5);
        
        const buffer = await page.screenshot({ type: 'png', omitBackground: true });
        
        // Pipe buffer to ffmpeg
        stdin.write(buffer);
        
        if (frame % 30 === 0) {
            console.log(`[HTML Renderer] Rendered frame ${frame}/${totalFrames}`);
        }
    }

    stdin.end();

    await browser.close();
    
    // Return a promise that resolves when ffmpeg finishes
    return new Promise((resolve, reject) => {
        ffmpegCmd.on('end', resolve);
        ffmpegCmd.on('error', reject);
    });
}

// CLI Interface
const args = process.argv.slice(2);
if (args.length >= 2) {
    const htmlFile = args[0];
    const outFile = args[1];
    const duration = parseFloat(args[2] || 10);
    renderVideo(htmlFile, outFile, 30, duration)
        .then(() => process.exit(0))
        .catch(err => {
            console.error(err);
            process.exit(1);
        });
} else {
    console.log("Usage: node engine.js <input.html> <output.mp4> <durationInSeconds>");
}
