import subprocess, sys, numpy as np, io, os
from PIL import Image
def probe(f):
    d=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f],capture_output=True,text=True).stdout.strip()
    try: return float(d)
    except: return 0.0
def frames(f, fps=2, w=96):
    # decode grayscale small frames as rawvideo
    h=int(w*16/9)
    p=subprocess.run(["ffmpeg","-nostdin","-v","error","-i",f,"-vf",f"fps={fps},scale={w}:{h}",
        "-pix_fmt","gray","-f","rawvideo","-"],capture_output=True)
    buf=np.frombuffer(p.stdout,dtype=np.uint8)
    n=len(buf)//(w*h)
    if n<2: return None
    return buf[:n*w*h].reshape(n,h,w).astype(np.int16)
# ---------------------------------------------------------------------------
# WARNING (2026-07-17): ADJACENT-FRAME DELTA IS NOT "ALIVENESS".
# It measures PIXEL CHURN. A slow fade/settle on a completely static layout
# produces high churn while the viewer sees nothing new -> scores "alive",
# reads FROZEN. This defect made v7 score 90.8% alive while two 10s bento
# scenes (s33, s36) were perceptually frozen.
# Use novelty() below (compare against a frame ~2s earlier) for any
# aliveness claim. Adjacent-delta is retained only for CONC%/slam detection.
# Corollary: adjacent-delta results are also violently sensitive to sample
# rate + downscale (v7 "frozen%" = 0.8% @4fps/96px vs 53.5% @24fps/64x36 --
# same file, same 0.5/255 threshold). Never quote it without both.
# ---------------------------------------------------------------------------
def novelty(f, fps=4, lag_s=2.0):
    """Perceptual novelty: mean |frame(t) - frame(t-lag)|. Low => viewer sees
    nothing new, regardless of how much churn is happening. <6 reads FROZEN."""
    a=frames(f, fps=fps)
    if a is None: return None
    lag=int(fps*lag_s)
    if len(a)<=lag: return None
    return float(np.abs(a[lag:]-a[:-lag]).mean(axis=(1,2)).mean())

def analyze(f):
    dur=probe(f); a=frames(f)
    if a is None: return None
    d=np.abs(np.diff(a,axis=0)).mean(axis=(1,2))   # per-step mean abs diff (CHURN, not aliveness)
    luma=a.mean()
    # spatial detail = mean stdev within frame (density proxy)
    detail=a.std(axis=(1,2)).mean()
    return dict(dur=dur, change=d.mean(), change_p90=np.percentile(d,90),
                still_pct=100.0*(d<1.0).mean(), luma=luma, detail=detail,
                beats=int((d>d.mean()+d.std()).sum()))
if __name__=="__main__":
    print(f"{'CHG':>6} {'P90':>6} {'STILL%':>7} {'LUMA':>5} {'DETAIL':>6} {'BEATS':>5} {'DUR':>6}  NAME")
    for f in sys.argv[1:]:
        r=analyze(f)
        if not r: print("  (decode fail)",os.path.basename(f)[:40]); continue
        print(f"{r['change']:6.2f} {r['change_p90']:6.2f} {r['still_pct']:7.1f} {r['luma']:5.0f} {r['detail']:6.1f} {r['beats']:5d} {r['dur']:6.1f}  {os.path.basename(f)[:44]}")
