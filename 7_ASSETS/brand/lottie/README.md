# Lottie motion-graphics (drop-in)

Free After-Effects animations (the huge LottieFiles ecosystem) render here to a **transparent .mov**
via `element_maker.render_lottie_clip("<name>", out.mov)` — vendored `lottie.min.js` (airbnb lottie-web, MIT),
seek-safe, headless, alpha (qtrle). Same pipeline as the verified Track-2 native clips.

**To add one:** download a `.json` from https://lottiefiles.com (filter to free / check the license) into this
folder, then reference it by file name. Real LottieFiles exports are well-formed and render correctly; do NOT
hand-author Lottie JSON (the schema is fragile). Colours are baked into the JSON (Lottie clips are pre-coloured).
