# Component gallery — native_composer scene components (light render)

Rendered previews of the scene components delivered from the 45-video craft study
(`../../template-study-2026-07.md` §7). These are the LIBRARY visual reference (tracked); the
throwaway render scratch lives in the gitignored `8_WORKSPACE/template_study/`.

Re-render any component: `python scripts/preview_component.py` (or import
`preview_component.preview(kind, data, out_png, brand=…, kicker=…, title=…)`).

| File | Component | Notes |
|---|---|---|
| compare_vs_seosona | `compare` | VS badge + winner-glow |
| compare_beforeafter_cqa | `compare` mode=beforeafter | arrow variant, CQA hues |
| bignum_strike_seosona | `bignum` strike | red diagonal = false/unverified number |
| checklist_status_cqa | `checklist` | tri-state ✓ done / ◐ doing / 🔒 locked |
| hub_seosona | `hub` | hub-and-spoke + travelling-dot progress line |
| icongrid_seosona | `icongrid` | 2-col categorical-colour grid |
| alert_danger_seosona | `alert` role=danger | dashed coral border callout |
| bars_seosona | `bars` | score/compare bars + grey baseline |
| filetree_seosona | `filetree` | repo file listing, rows reveal |
| chiprow_seosona | `chiprow` | compat/tool pill row |

Data schemas: see `template-study-2026-07.md` §7. Colours come from the semantic role tokens
(`brand_kit.ROLES`), so they remap correctly between SEOSONA and CQA.
