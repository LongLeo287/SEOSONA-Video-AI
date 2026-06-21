import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
filepath = ROOT / "5_FRAMEWORK" / "hf_cards" / "master_template_9_16" / "index.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Title & Meta
content = content.replace("<title>SEOSONA · Frame Showcase — Landscape 16:9</title>",
                          "<title>SEOSONA · Frame Showcase — Vertical 9:16</title>")
content = content.replace("frame.md · 16:9 · 1920×1080", "frame.md · 9:16 · 1080×1920")
content = content.replace("16:9 · 1920×1080 · contact sheet", "9:16 · 1080×1920 · contact sheet")

# 2. Aspect ratios
content = content.replace("aspect-ratio:16/9;", "aspect-ratio:9/16;")

# 3. Treatment 1: Cover (Wordmark 22cqw on two lines, dot beneath)
content = re.sub(
    r'<div class="cover-wordmark">.*?</div>',
    r'<div class="cover-wordmark" style="flex-direction:column; align-items:center; gap:0;">\n      <span>SEO</span>\n      <span>SONA</span>\n      <span class="dot-signal" aria-hidden="true" style="align-self:center; margin-top:2cqw; margin-bottom:0;"></span>\n    </div>',
    content,
    flags=re.DOTALL
)

# 4. Treatment 2: Oversized Claim (Claim wraps to 3-4 lines, rule 32cqw)
content = content.replace('style="width:18cqw;"', 'style="width:32cqw;"')

# 5. Treatment 3: Focal Artifact (Card 78x88cqw, sparkline 60cqw)
content = content.replace('style="width:62cqw;min-height:62cqw;justify-content:space-between;"',
                          'style="width:78cqw;min-height:88cqw;justify-content:space-between;"')
content = content.replace('<svg class="f-spark" viewBox="0 0 100 18"',
                          '<svg class="f-spark" style="width:60cqw;" viewBox="0 0 100 18"')

# 6. Treatment 4: Stat Plate (Numeral 28cqw)
content = content.replace('class="f-stat"', 'class="f-stat" style="font-size:28cqw;"')

# 7. Treatment 5: Ledger (2x3 grid)
content = content.replace('grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(2,1fr);',
                          'grid-template-columns:repeat(2,1fr);grid-template-rows:repeat(3,1fr);')

# 8. Treatment 6: Closer (Pill 38cqw wide)
content = content.replace('<button class="f-btn-ink">Book the audit →</button>',
                          '<button class="f-btn-ink" style="width:38cqw; font-size:3cqw; padding:2.5cqw 0;">Book the audit →</button>')
content = content.replace('font-size:2.1cqw;', 'font-size:4cqw;') # make wordmark larger

# 9. Treatment 7: Catalog Trio (1 col stacked)
content = content.replace('grid-template-columns:repeat(3,1fr);', 'grid-template-columns:1fr;')
# Reduce index numeral font sizes from section-head (4.4cqw) to something more appropriate for vertical rows
content = content.replace('class="f-section-head" style="font-size:3.6cqw;', 'class="f-title-md" style="font-size:4cqw;')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully converted index.html to 9:16 layout.")
