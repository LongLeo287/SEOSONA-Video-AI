# -*- coding: utf-8 -*-
"""Generate royalty-free ambient BGM beds with ffmpeg (100% original — no copyright).

Each mood = a soft chord-pad progression (layered sine partials + tremolo + lowpass +
reverb), looped ~60s, normalised LOW (it gets ducked under the voice at mix time).
Safe to mux into any video on any platform — we synthesize it, so no takedown risk.
"""
import os, subprocess, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "7_ASSETS", "audio", "bgm")
os.makedirs(OUT, exist_ok=True)

# note -> frequency (Hz)
N = {"C2":65.41,"D2":73.42,"E2":82.41,"F2":87.31,"G2":98.00,"A2":110.00,"B2":123.47,
     "C3":130.81,"D3":146.83,"E3":164.81,"F3":174.61,"G3":196.00,"A3":220.00,"B3":246.94,
     "C4":261.63,"D4":293.66,"E4":329.63,"F4":349.23,"G4":392.00,"A4":440.00}

# mood -> (progression [chord = list of notes], seconds-per-chord, brightness lowpass Hz, tremolo Hz)
MOODS = {
    # tech: existing file kept; we add the rest
    "news":    ([["C3","E3","G3","C4"],["G2","B2","D3","G3"],["A2","C3","E3","A3"],["F2","A2","C3","F3"]], 3.0, 3200, 1.8),
    "insight": ([["A2","C3","E3"],["F2","A2","C3"],["C3","E3","G3"],["G2","B2","D3"]], 4.5, 2000, 0.7),
    "upbeat":  ([["D3","F3","A3","D4"],["A2","C3","E3","A3"],["B2","D3","F3","B3"],["G2","B2","D3","G3"]], 2.5, 3800, 2.4),
}

def chord_wav(notes, dur, path):
    """One chord = amix of sine partials with a soft fade in/out (smooth pad)."""
    ins, filt, mixn = [], [], []
    for i, note in enumerate(notes):
        f = N[note]
        ins += ["-f", "lavfi", "-i", f"sine=frequency={f:.2f}:duration={dur}"]
        # add a quiet upper octave partial for warmth via the same sine (kept simple)
        filt.append(f"[{i}]volume={0.9/len(notes):.3f}[c{i}]"); mixn.append(f"[c{i}]")
    fade = min(0.8, dur/3)
    fc = ";".join(filt) + ";" + "".join(mixn) + f"amix=inputs={len(notes)}:normalize=0," \
         f"afade=t=in:st=0:d={fade},afade=t=out:st={dur-fade:.2f}:d={fade}[a]"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",*ins,
                    "-filter_complex",fc,"-map","[a]","-ar","48000","-ac","2",path], check=True)

def build(mood):
    prog, dur, lp, trem = MOODS[mood]
    tmp = tempfile.mkdtemp()
    parts = []
    for i, ch in enumerate(prog):
        p = os.path.join(tmp, f"c{i}.wav"); chord_wav(ch, dur, p); parts.append(p)
    listf = os.path.join(tmp, "list.txt")
    with open(listf, "w", encoding="utf-8") as _lf:   # explicit UTF-8: a non-ASCII tmp path must not crash on Windows cp1252
        _lf.write("".join(f"file '{p}'\n" for p in parts))
    bed = os.path.join(tmp, "bed.wav")
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0",
                    "-i",listf,"-c","copy",bed], check=True)
    out = os.path.join(OUT, f"bgm_{mood}.mp3")
    # movement (tremolo) + warmth (lowpass) + space (reverb) + loop to ~60s + low level
    total = dur*len(prog)
    loops = int(60/total)+1
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error","-stream_loop",str(loops),"-i",bed,
                    "-af",f"apulsator=hz={trem},lowpass=f={lp},aecho=0.8:0.6:60:0.25,"
                          f"loudnorm=I=-20:TP=-3:LRA=11,atrim=0:60,afade=t=in:st=0:d=2,afade=t=out:st=58:d=2",
                    "-ar","48000","-ac","2",out], check=True)
    print(f"  {os.path.basename(out)}  ({total:.0f}s prog x{loops} -> 60s)")
    return out

if __name__ == "__main__":
    print("Generating royalty-free BGM beds:")
    for m in MOODS: build(m)
    print("DONE")
