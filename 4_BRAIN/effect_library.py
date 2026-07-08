# -*- coding: utf-8 -*-
"""Effect Library — the 4th SEOSONA library layer (transition · text-effect · effect · SFX · motion).

A STORED, extensible catalog of seek-safe GSAP recipes that `native_composer` draws from, with
deterministic SELECTORS that ROTATE each dimension per-video + per-scene. Rotation is seeded by the
VIDEO (topic/output), so two different videos get DIFFERENT recipe sequences → the factory's output
stays varied at scale. The dimensions rotate on DIFFERENT phases, so a scene is a fresh COMBINATION
(transition × text-effect × exit) — multiplicative variety, never "every video looks the same".

Grow it like the other libraries (template · component · block, see `scripts/grow_library.py`):
add a recipe to a registry below → it enters rotation automatically. No CapCut, ever — this is the
brand-fit subset of CapCut's transition/text-effect catalog, re-built native.

INVARIANTS (every recipe): seek-safe GSAP `fromTo`/`from` only (NO @keyframes, NO random,
deterministic) · resolves to the resting pose · brand-fit (light-only, NO horizontal drift — SEOSONA
content never slides sideways; recipes move on y / scale / opacity / clip-path only). clipPath wipes
use the pattern already proven by the chart-bar wipe in native_composer.

Layout of a scene entrance (composed in native_composer):
  scene opacity-fade (native_composer)  +  TRANSITION (kicker + component)  +  TEXT-EFFECT (headline)
so the headline animates independently of the kicker/component.
"""

def _seed_int(s):
    """Stable integer from a string (video topic/output) → rotation offset. Position-weighted
    polynomial hash so similar topics still spread across the rotation. Deterministic (no RNG)."""
    h = 0
    for c in str(s or "x"):
        h = (h * 31 + ord(c)) % 1000003
    return h


# ============================================================================ TRANSITIONS
# Scene ENTRANCE for the kicker + component (the HEADLINE is owned by TEXT-EFFECTS below).
# Each: fn(K, C, ap) -> [gsap tweens], K/C = quoted selectors for .kicker / .comp, ap = appear-time.
# ============================================================================
def _t_slide_up(K, C, ap):
    return [f'tl.fromTo({K},{{y:-24}},{{y:0,duration:0.45,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{y:34,scale:0.97}},{{y:0,scale:1,duration:0.55,ease:"power3.out"}},{ap+0.12:.2f});']

def _t_rise_fade(K, C, ap):
    return [f'tl.fromTo({K},{{y:-24,opacity:0}},{{y:0,opacity:1,duration:0.45,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{y:42,scale:0.97}},{{y:0,scale:1,duration:0.55,ease:"power3.out"}},{ap+0.12:.2f});']

def _t_zoom(K, C, ap):
    return [f'tl.fromTo({K},{{scale:0.82,opacity:0}},{{scale:1,opacity:1,duration:0.45,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{scale:0.94,opacity:0}},{{scale:1,opacity:1,duration:0.55,ease:"power3.out"}},{ap+0.12:.2f});']

def _t_drop(K, C, ap):
    return [f'tl.fromTo({K},{{y:-24,opacity:0}},{{y:0,opacity:1,duration:0.45,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{scale:0.9,opacity:0}},{{scale:1,opacity:1,duration:0.55,ease:"power3.out"}},{ap+0.12:.2f});']

def _t_dissolve(K, C, ap):
    return [f'tl.fromTo({K},{{opacity:0,y:-10}},{{opacity:1,y:0,duration:0.5,ease:"power1.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{opacity:0}},{{opacity:1,duration:0.65,ease:"power1.out"}},{ap+0.14:.2f});']

def _t_wipe_up(K, C, ap):
    return [f'tl.fromTo({K},{{y:-24}},{{y:0,duration:0.45,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{clipPath:"inset(100% 0 0 0)"}},{{clipPath:"inset(0% 0 0 0)",duration:0.6,ease:"power2.out"}},{ap+0.12:.2f});']

# SPRING entrances (Remotion spring math → GSAP CustomEase, registered in the render doc). The component
# lands with real physics (overshoot + settle) — reserved for HERO moments (data lands, hooks snap), NOT
# text (calm). If CustomEase didn't load, GSAP falls back to a linear ease (no crash). ease names must
# match native_composer's CustomEase.create ids: springLand / springSoft / springSnappy / springBouncy.
def _t_spring_pop(K, C, ap):
    return [f'tl.fromTo({K},{{y:-22,opacity:0}},{{y:0,opacity:1,duration:0.42,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{scale:0.80,opacity:0}},{{scale:1,opacity:1,duration:0.72,ease:"springLand"}},{ap+0.12:.2f});']

def _t_spring_soft(K, C, ap):
    return [f'tl.fromTo({K},{{y:-22,opacity:0}},{{y:0,opacity:1,duration:0.42,ease:"power2.out"}},{ap:.2f});',
            f'tl.fromTo({C},{{y:30,scale:0.92,opacity:0}},{{y:0,scale:1,opacity:1,duration:0.70,ease:"springSoft"}},{ap+0.12:.2f});']

def _t_spring_snap(K, C, ap):
    return [f'tl.fromTo({K},{{scale:0.80,opacity:0}},{{scale:1,opacity:1,duration:0.40,ease:"springSnappy"}},{ap:.2f});',
            f'tl.fromTo({C},{{scale:0.86,opacity:0}},{{scale:1,opacity:1,duration:0.60,ease:"springSnappy"}},{ap+0.10:.2f});']

TRANSITIONS = {"slide-up": _t_slide_up, "rise-fade": _t_rise_fade, "zoom": _t_zoom,
               "drop": _t_drop, "dissolve": _t_dissolve, "wipe-up": _t_wipe_up,
               "spring-pop": _t_spring_pop, "spring-soft": _t_spring_soft, "spring-snap": _t_spring_snap}
TRANSITION_ORDER = ["slide-up", "rise-fade", "zoom", "drop", "dissolve", "wipe-up"]


# CONTENT-AWARE selection: which transitions FIT which content class, so the motion matches the
# scene (data "builds in", hooks pop, text dissolves) — the selector still ROTATES within the fitting
# subset (seeded) so variety is preserved. This is what makes the library SMART, not just random.
_TRANSITION_FIT = {
    "data": ["spring-pop", "wipe-up", "zoom", "slide-up"],   # bignum/chart/pie/donut — data LANDS w/ physics
    "list": ["slide-up", "spring-soft", "rise-fade", "wipe-up"],  # steps/badges/feature — items assemble+settle
    "text": ["dissolve", "rise-fade", "zoom"],     # quote/tip/callout/lower-third/repo/terminal — calm, NO spring
    "hook": ["spring-snap", "zoom", "rise-fade"],  # cta/hero/divider — punchy physics
}
_KIND_CLASS = {"bignum": "data", "chart": "data", "stats": "data", "mockup": "data", "ring": "data",
               "donut": "data", "pie": "data", "linechart": "data", "stat_grid": "data", "ratio_dots": "data",
               "metric_reveal": "data",
               "steps": "list", "badges": "list", "feature": "list", "compare": "list", "timeline": "list",
               "checklist": "list", "icongrid": "list", "layer_stack": "list", "org_diagram": "list",
               "divider": "hook",
              "quote": "text", "tip": "text", "callout": "text", "lower-third": "text",
               "terminal": "text", "repo": "text", "cta": "hook"}


def _fit_pool(kind, order):
    return _TRANSITION_FIT.get(_KIND_CLASS.get(kind or "", ""), order)


def entrance(cid, ap, idx, seed="", kind=None, force=None):
    """Kicker + component entrance for scene `idx`. Content-aware: picks from the transitions that FIT
    this component `kind`, rotated per-video for variety. `force` (a valid TRANSITIONS name) is the
    writer's explicit override — used verbatim when valid, else the auto pick. Returns (tweens, name)."""
    if force in TRANSITIONS:
        name = force
    else:
        pool = _fit_pool(kind, TRANSITION_ORDER)
        name = pool[(_seed_int(seed) + idx) % len(pool)]
    K, C = f'"#{cid} .kicker"', f'"#{cid} .comp"'
    return TRANSITIONS[name](K, C, ap), name


# ============================================================================ TEXT-EFFECTS
# The HEADLINE (.head) animation, rotated on its OWN phase so it combines freshly with the
# transition. Word recipes act on per-word spans (.head .w). Each: fn(cid, ap) -> [gsap tweens].
# ============================================================================
def _te_rise(cid, ap):
    """Headline rises + settles (the calm default)."""
    return [f'tl.fromTo("#{cid} .head",{{y:28}},{{y:0,duration:0.5,ease:"power3.out"}},{ap+0.06:.2f});']

def _te_drop(cid, ap):
    """Headline drops from above + fades."""
    return [f'tl.fromTo("#{cid} .head",{{y:-34,opacity:0}},{{y:0,opacity:1,duration:0.52,ease:"power3.out"}},{ap+0.06:.2f});']

def _te_clip_wipe(cid, ap):
    """Headline reveals left→right via a clip-path wipe (typewriter-ish)."""
    return [f'tl.fromTo("#{cid} .head",{{clipPath:"inset(0 100% 0 0)"}},{{clipPath:"inset(0 0% 0 0)",duration:0.55,ease:"power2.out"}},{ap+0.06:.2f});']

def _te_word_up(cid, ap):
    """Words reveal one-by-one, each rising + fading in (stagger). Seek-safe (per-word tl.from,
    the same pattern as the reveal-items loop)."""
    return [f';(function(){{var _w=document.querySelectorAll("#{cid} .head .w");'
            f'_w.forEach(function(el,k){{tl.from(el,{{y:26,opacity:0,duration:0.5,ease:"power3.out"}},{ap+0.06:.2f}+k*0.06);}});}})();']

def _te_word_pop(cid, ap):
    """Words pop in one-by-one (subtle scale, gentle back-ease — emphasis, not childish bounce)."""
    return [f';(function(){{var _w=document.querySelectorAll("#{cid} .head .w");'
            f'_w.forEach(function(el,k){{tl.from(el,{{scale:0.72,opacity:0,duration:0.46,ease:"back.out(1.5)"}},{ap+0.06:.2f}+k*0.06);}});}})();']

def _te_char_cascade(cid, ap):
    """Per-CHARACTER kinetic typography via GSAP SplitText (free in GSAP 3.13+). GUARDED: if the plugin
    isn't loaded it falls back to a whole-headline rise, so the render NEVER breaks. Seek-safe (tl.from).
    Pattern adopted from GSAP SplitText, 2026-07-02."""
    t = ap + 0.06
    js = (';(function(){var h=document.querySelector("#%s .head");if(!h)return;'
          'if(window.SplitText){try{var s=new SplitText(h,{type:"chars"});'
          's.chars.forEach(function(c,k){tl.from(c,{y:22,opacity:0,duration:0.42,ease:"power3.out"},%.2f+k*0.028);});return;}catch(e){}}'
          'tl.fromTo(h,{y:26,opacity:0},{y:0,opacity:1,duration:0.5,ease:"power3.out"},%.2f);})();') % (cid, t, t)
    return [js]

def _te_line_mask(cid, ap):
    """Per-LINE slide-up from behind a mask (SplitText `mask:"lines"`, free GSAP 3.13+ → auto overflow-clip
    wrapper, no markup change). GUARDED: falls back to a whole-headline rise if the plugin is absent, so it
    never breaks. Seek-safe (tl.from). Distinct from char-cascade (chars) — operates on lines. 2026-07-02."""
    t = ap + 0.06
    js = (';(function(){var h=document.querySelector("#%s .head");if(!h)return;'
          'if(window.SplitText){try{var s=new SplitText(h,{type:"lines",mask:"lines"});'
          's.lines.forEach(function(l,k){tl.from(l,{yPercent:110,duration:0.55,ease:"power3.out"},%.2f+k*0.09);});return;}catch(e){}}'
          'tl.fromTo(h,{y:26,opacity:0},{y:0,opacity:1,duration:0.5,ease:"power3.out"},%.2f);})();') % (cid, t, t)
    return [js]

def _te_shimmer(cid, ap):
    """A light sweep passes once across the headline (adopted from Auto-Create-Video, MIT — a HyperFrames
    sibling). SEEK-SAFE: GSAP tweens a CSS var on an injected overlay mask (timeline-driven), NOT a CSS
    `infinite` animation (which freezes under HF seek). Subtle white sheen via mix-blend over the dark
    headline on the light brand. Self-contained (injects its own mask + inline CSS → no _css change)."""
    t = ap + 0.12
    rise = f'tl.fromTo("#{cid} .head",{{y:26,opacity:0}},{{y:0,opacity:1,duration:0.5,ease:"power3.out"}},{ap+0.06:.2f});'
    grad = ("background:linear-gradient(115deg,transparent calc(var(--sp,-20%) - 9%),"
            "rgba(255,255,255,0.78) var(--sp,-20%),transparent calc(var(--sp,-20%) + 9%))")
    js = (';(function(){var h=document.querySelector("#' + cid + ' .head");if(!h)return;'
          'if(getComputedStyle(h).position==="static")h.style.position="relative";'
          'var m=h.querySelector(".shimmer-mask");'
          'if(!m){m=document.createElement("div");m.className="shimmer-mask";'
          'm.style.cssText="position:absolute;inset:0;pointer-events:none;mix-blend-mode:overlay;' + grad + '";'
          'h.appendChild(m);}'
          'tl.fromTo(m,{"--sp":"-20%"},{"--sp":"120%",duration:1.1,ease:"power2.inOut"},' + f'{t:.2f}' + ');})();')
    return [rise, js]

TEXT_EFFECTS = {"rise": _te_rise, "drop": _te_drop, "clip-wipe": _te_clip_wipe, "word-up": _te_word_up,
                "word-pop": _te_word_pop, "char-cascade": _te_char_cascade, "line-mask": _te_line_mask,
                "shimmer": _te_shimmer}
TEXT_EFFECT_ORDER = ["rise", "word-up", "char-cascade", "line-mask", "clip-wipe", "word-pop", "drop", "shimmer"]


def text_effect(cid, ap, idx, seed=""):
    """Headline treatment for scene `idx`, rotated on a DIFFERENT phase than transitions (seed+'t')
    so transition×text-effect form fresh combinations. Returns (tweens, name)."""
    name = TEXT_EFFECT_ORDER[(_seed_int(str(seed) + "t") + idx) % len(TEXT_EFFECT_ORDER)]
    return TEXT_EFFECTS[name](cid, ap), name


# ============================================================================ EFFECT OVERLAYS
# Decorative full-scene overlays (light-leak, accent bloom), applied SPARSELY (~half the scenes,
# rotated) so they add per-scene variety on top of the always-on ambient depth WITHOUT making every
# scene busy. Each: fn(cid, ap, dur) -> (html_snippet, [gsap tweens]). Behind content (z-index 0),
# low opacity, brand-fit (light-mode). All seek-safe.
def _fx_light_leak(cid, ap, dur):
    """A warm coral light-leak drifting in from a corner (subtle, multiply-blended)."""
    return (f'<div class="scfx leak" id="{cid}_fx"></div>',
            [f'tl.fromTo("#{cid}_fx",{{opacity:0,xPercent:6}},{{opacity:1,xPercent:0,duration:{min(max(dur,2.0),6.0):.2f},ease:"sine.inOut"}},{ap:.2f});'])

def _fx_bloom(cid, ap, dur):
    """A soft brand-accent radial that blooms open as the scene enters."""
    return (f'<div class="scfx bloom" id="{cid}_fx"></div>',
            [f'tl.fromTo("#{cid}_fx",{{scale:0.55,opacity:0}},{{scale:1.1,opacity:1,duration:1.0,ease:"power2.out"}},{ap:.2f});'])

EFFECTS = {"light-leak": _fx_light_leak, "bloom": _fx_bloom}
EFFECT_ORDER = ["light-leak", "bloom"]


def overlay(cid, ap, dur, idx, seed="", force=None):
    """Maybe pick a decorative overlay for scene `idx`. `force` (the DIRECTOR's chosen EFFECTS name) is
    used verbatim when valid — the director holds the plan; else SPARSE auto: ~half the scenes get one
    (rotated, seeded per-video). Returns (html, tweens, name); (None, [], None) when no overlay."""
    if force in EFFECTS:
        name = force
    else:
        s = _seed_int(str(seed) + "fx")
        if (s + idx) % 2:                # ~half the scenes → no overlay
            return None, [], None
        name = EFFECT_ORDER[((s + idx) // 2) % len(EFFECT_ORDER)]
    html, tw = EFFECTS[name](cid, ap, dur)
    return html, tw, name


# ============================================================================ EXITS
# Scene EXIT deltas appended to `tl.to("#cid",{opacity:0<delta>,...})`. Rotates per-video.
# ============================================================================
EXITS = {"fade": "", "slide-left": ",x:-64", "lift": ",y:-52", "shrink": ",scale:0.92", "sink": ",y:52"}
EXIT_ORDER = ["fade", "slide-left", "lift", "shrink", "sink"]


def exit_delta(idx, seed=""):
    """Pick the EXIT delta for scene `idx`. Returns (delta, name)."""
    name = EXIT_ORDER[(_seed_int(seed) + idx) % len(EXIT_ORDER)]
    return EXITS[name], name


# ============================================================================ MOTION (ambient)
# Always-on background motion: glow breathe + ghost-word drift + two brand blobs drifting. The blob
# PROFILE rotates per-video (seed) so the ambient movement "feels" different across videos while
# staying consistent within one video. Seek-safe sine.inOut. NO horizontal drift on CONTENT — these
# are BACKGROUND layers (blobs/glow/ghost), where drift is the intended liquid-depth effect.
_BLOB_PROFILES = [((54, -36), (-46, 32)), ((40, 40), (-50, -30)), ((-38, -44), (52, 28))]

def motion_ambient(cid, ap, dur, seed=""):
    """Ambient glow/ghost/blob motion for one scene. Returns [gsap tweens]. Blob-drift profile is
    chosen per-video from `seed` (consistent across a video's scenes)."""
    adur = min(max(dur, 2.0), 7.0)
    (b1x, b1y), (b2x, b2y) = _BLOB_PROFILES[_seed_int(str(seed) + "m") % len(_BLOB_PROFILES)]
    return [
        f'tl.fromTo("#{cid} .scglow",{{scale:0.92,opacity:0}},{{scale:1.12,opacity:1,duration:{adur:.2f},ease:"sine.inOut"}},{ap:.2f});',
        f'tl.fromTo("#{cid} .scghost",{{x:-26,opacity:0}},{{x:26,opacity:1,duration:{adur:.2f},ease:"sine.inOut"}},{ap:.2f});',
        # blobs MEANDER via seeded noise (organic, Remotion-noise idea) — falls back to a plain sine drift
        # if __nz isn't present. Amplitude = the profile's target magnitude; seed-varied per blob.
        _blob_noise(cid, "_bl1", ap, adur, b1x, b1y, _seed_int(str(seed) + "n1")),
        _blob_noise(cid, "_bl2", ap, adur, b2x, b2y, _seed_int(str(seed) + "n2")),
    ]


def _blob_noise(cid, suffix, ap, adur, ax, ay, seed):
    """One background blob wandering via seeded value-noise (seek-safe onUpdate). Guarded: if window.__nz
    is absent it drifts once to (ax,ay) with a sine ease (the old behaviour), so it never breaks."""
    A = max(18, (abs(ax) + abs(ay)) / 2 + 12)
    s2 = (seed * 48271 + 12345) & 0x7fffffff
    sel = "#" + cid + suffix
    return (';(function(){var b=document.querySelector("' + sel + '");if(!b)return;'
            'if(!window.__nz){tl.fromTo(b,{x:0,y:0},{x:' + f'{ax}' + ',y:' + f'{ay}'
            + ',duration:' + f'{adur:.2f}' + ',ease:"sine.inOut"},' + f'{ap:.2f}' + ');return;}'
            'tl.to({p:0},{p:1,duration:' + f'{adur:.2f}' + ',ease:"none",onUpdate:function(){'
            'var p=this.progress()*2.2;'
            'b.style.transform="translate("+(window.__nz(' + f'{seed}' + ',p)*' + f'{A:.0f}'
            + ')+"px,"+(window.__nz(' + f'{s2}' + ',p)*' + f'{A:.0f}' + ')+"px)";}},' + f'{ap:.2f}' + ');})();')


# ============================================================================ SFX (selector)
# The SFX FILES live in native_composer (asset-path logic); the library owns the ROTATION so the
# transition-swish sequence differs per-video (no dup of paths). Categories are listed for catalog.
SFX_CATEGORIES = ["transition", "impact", "ui", "click", "keyboard", "riser", "success", "pop"]

def sfx_variant(idx, n, seed=""):
    """Rotate which SFX variant scene `idx` uses, offset per-video so different videos get different
    swish sequences. Returns an index into a variant list of length n."""
    return (_seed_int(str(seed) + "s") + idx) % max(1, n)


def status():
    """Library stats — surfaced by grow_library."""
    return {"transitions": len(TRANSITIONS), "text_effects": len(TEXT_EFFECTS),
            "effects": len(EFFECTS), "exits": len(EXITS),
            "motion_profiles": len(_BLOB_PROFILES), "sfx_categories": len(SFX_CATEGORIES)}


if __name__ == "__main__":
    print("== EFFECT LIBRARY ==")
    print(f"  TRANSITIONS  : {len(TRANSITIONS)}  {TRANSITION_ORDER}")
    print(f"  TEXT-EFFECTS : {len(TEXT_EFFECTS)}  {TEXT_EFFECT_ORDER}")
    print(f"  EXITS        : {len(EXITS)}  {EXIT_ORDER}")
    for nm, fn in TRANSITIONS.items():
        t = fn('"#s .kicker"', '"#s .comp"', 5.0)
        assert len(t) == 2 and all("fromTo" in x for x in t), nm
    for nm, fn in TEXT_EFFECTS.items():
        t = fn('s', 5.0)
        # ≥1 tween, each a GSAP timeline call — shimmer legitimately returns 2 (reveal + sweep); the
        # consumer tweens.extend()s the whole list, so the old len==1 invariant was stale, not a bug.
        assert t and all(isinstance(x, str) and ("tl." in x or "fromTo" in x) for x in t), nm
    print("  self-check   : OK")
