/**
 * SEOSONA Video Factory - Template Core Sync
 * This script is injected into all 19 video templates.
 * It automatically handles BGM, Voice, and SFX generation based on Hyperframes variables.
 */

(function initSeosonaCore() {
  const vars = window.__hyperframes ? window.__hyperframes.getVariables() : {};
  const duration = parseFloat(vars.DURATION) || 60;
  
  // 1. Ensure Audio Container exists
  let audioContainer = document.getElementById('seosona-audio-core');
  if (!audioContainer) {
    audioContainer = document.createElement('div');
    audioContainer.id = 'seosona-audio-core';
    document.body.appendChild(audioContainer);
  }

  // 2. Generate Base Audio Tracks (Voice & BGM)
  let audioHtml = `
    <audio id="voice-track" src="assets/voice.wav" data-start="0" data-duration="${duration}" data-track-index="1" data-volume="1.0"></audio>
    <audio id="bgm-track" src="assets/bgm_news.mp3" data-start="0" data-duration="${duration}" data-timeline-role="music" data-track-index="6" data-volume="0.35"></audio>
  `;

  // 3. Auto-Generate SFX based on timeline variables (*_START)
  let sfxTrackIndex = 10;
  Object.keys(vars).forEach(key => {
    if (key.includes('START') && typeof vars[key] !== 'undefined') {
      const time = parseFloat(vars[key]);
      if (!isNaN(time) && time > 0 && time < duration) {
        audioHtml += `<audio id="sfx-whoosh-${key}" src="assets/sfx_whoosh.wav" data-start="${Math.max(0, time - 0.5)}" data-duration="0.5" data-track-index="${sfxTrackIndex++}" data-volume="0.65"></audio>`;
        audioHtml += `<audio id="sfx-pop-${key}" src="assets/sfx_pop.wav" data-start="${time + 0.1}" data-duration="0.1" data-track-index="${sfxTrackIndex++}" data-volume="0.6"></audio>`;
      }
    }
  });

  audioContainer.innerHTML = audioHtml;

  // 4. Try to auto-bind text variables to common classes if they exist
  // We look for elements with IDs matching text variables (e.g. id="TEXT_1") or data-bind="TEXT_1"
  Object.keys(vars).forEach(key => {
    if (key.startsWith('TEXT_') || key.includes('TITLE') || key.includes('DESC')) {
      // Find element by exact ID
      const elById = document.getElementById(key) || document.getElementById(key.toLowerCase());
      if (elById) elById.innerText = vars[key];
      
      // Find elements by data-bind
      const elsByBind = document.querySelectorAll(`[data-bind="${key}"]`);
      elsByBind.forEach(el => el.innerText = vars[key]);
    }
  });

  console.log('[SEOSONA Core] Initialized Audio Sync & Dynamic Text mapping.');
})();
