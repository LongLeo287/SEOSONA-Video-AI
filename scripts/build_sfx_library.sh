#!/usr/bin/env bash
# Curate the SEOSONA SFX library from the source "Sound Effects Pack".
# Source clips have long cinematic reverb tails; we trim each to a short, punchy
# cue, fade the tail, and peak-normalise to a comparable level. The engine
# (native_composer) then mixes these per-component at the right timestamps.
# Re-runnable: overwrites the curated cues. Provenance is documented in
# 7_ASSETS/audio/sfx/manifest.json.
set -e
SRC="/d/SEOSONA AI/Sound Effects Pack"
DST="/d/SEOSONA AI/SEOSONA Video/7_ASSETS/audio/sfx"

# cue <src> <out> <start> <dur> <fadeout_dur>  — trim, fade tail, peak-normalise to -1.5dB
cue() {
  local st; st=$(awk "BEGIN{printf \"%.3f\", $4 - $5}")
  ffmpeg -y -hide_banner -loglevel error -ss "$3" -t "$4" -i "$SRC/$1" \
    -af "afade=t=out:st=$st:d=$5,loudnorm=I=-16:TP=-1.5:LRA=11,volume=2" \
    -ar 48000 -ac 2 "$DST/$2"
  echo "  $2  <-  $1"
}

echo "TRANSITION (swish / whoosh)"
cue "Swish/Classic, Stone Texture, Fast.mp3"      "transition/swish_01.mp3" 0    0.9 0.25
cue "Swish/Fast, Clothy.mp3"                       "transition/swish_02.mp3" 0.05 0.8 0.25
cue "Whooshes/Fast, Close, Airy, Zoom 01.mp3"      "transition/whoosh_01.mp3" 0   1.1 0.35
cue "Whooshes/Classic, Airy.mp3"                   "transition/whoosh_02.mp3" 0.1 1.2 0.4
cue "Swish/Classic, Storm, Fast.mp3"               "transition/swish_03.mp3"  0.05 0.85 0.3
cue "Whooshes/Deep, Low, Cinematic.mp3"            "transition/whoosh_03.mp3" 0   1.2 0.4

echo "IMPACT (number / stat reveal)"
cue "Impacts/Cinematic, Deep, Boom, Impact.mp3"    "impact/impact_soft.mp3" 0 1.6 0.6
cue "Impacts/Bass, Boom, Distant Impact 02.mp3"    "impact/impact_deep.mp3" 0 1.8 0.7
cue "Impacts/Cinematic Hit, Soft Impact 02.mp3"    "impact/impact_hit.mp3"  0 1.4 0.6

echo "UI (badge / cta / step / success / pop)"
cue "User Interface/Button, Positive, Chord, Bright.mp3" "ui/positive.mp3" 0 1.8 0.6
cue "Clicks/Button, Generic UI Click x2.mp3"             "ui/click.mp3"    0 0.6 0.2
cue "User Interface/Achievement, Level Up, Notification, Goal Achieved, Positive 03.mp3" "ui/success.mp3" 0 1.6 0.5
cue "Clicks/Digital, Video Game, Select, Positive, Notification 01.mp3" "ui/pop.mp3" 0 0.55 0.15
cue "User Interface/Computer, Digital Beep, Short.mp3" "ui/notify.mp3" 0 0.9 0.3

echo "TYPING (terminal bed)"
cue "Typing/Keyboard, Apple Magic, Typing, Short Phrases.mp3" "typing/keyboard.mp3" 1.0 5.0 0.6

echo "RISER (hook lift)"
cue "Riser/Bass, Sharp Detail Riser.mp3"           "riser/riser_short.mp3" 0 0.95 0.2
cue "Riser/Epic Sunrise Riser.mp3"                 "riser/riser_long.mp3"  8.0 3.0 0.5

echo "TICK (urgency / deadline / countdown tension)"
cue "Clocks/Tick Tock.mp3"                         "tick/tick.mp3"       0 0.9 0.25
cue "Clocks/Ticking Clock, Classic, Countdown.mp3" "tick/countdown.mp3"  0 2.2 0.6

echo "SHUTTER (screenshot / capture / snapshot reveal)"
cue "Camera Shutter/Digital, Take Picture, Shutter 02.mp3" "shutter/shutter.mp3" 0 0.8 0.2

echo "DONE."
