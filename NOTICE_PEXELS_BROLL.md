# NOTICE — Pexels b-roll auto-sourcing (News-Stack faceless mode)

_Uncommitted provenance note for the legacy repo. The build itself lives in the V2 repo
`seosona-video-os` (`packages/engines/src/pexelsBroll.ts` + `nativeRenderAdapter.ts`)._

## What

V2's faceless **News-Stack** mode auto-sources real b-roll to fill its full-frame slot instead of
the brand-gradient placeholder:

- **Preferred:** a Pexels **video** (portrait / 9:16 stock clip) — real motion b-roll.
- **Fallback:** a Pexels **photo**, turned into motion via a Ken-Burns pan/zoom.
- **Fallback of last resort:** the honest SEOSONA brand-gradient placeholder (offline / no key / no result).

The visual search query is derived from each news beat's headline + keywords.

## Source & license

- **Provider:** Pexels API (`https://api.pexels.com`). "Pexels" is an API/provider name, not a
  competitor video-editing brand.
- **License:** the **Pexels License** (`https://www.pexels.com/license/`) — free to use, modify, and
  use commercially; **attribution is appreciated, not legally required**; the media may not be resold
  unaltered or used to imply endorsement.
- **Attribution carried:** every sourced asset's creator + Pexels page URL is written to the reel's
  `<final>.mp4.credits.txt` (e.g. `B-roll video by <creator> on Pexels (<url>) — Pexels license`).
  A publisher should keep these credits with the published video.

## Key

- Requires `PEXELS_API_KEY` (read from the environment, or this legacy repo's `.env`). Absent → the
  News-Stack mode keeps its honest brand-gradient placeholder; nothing is fabricated.

## Honesty

- Probe-gated on the key; a failed search / download / empty result resolves to an honest miss
  (→ gradient fallback), never a fabricated media path.
- Results are cached by query (content-addressed) so the same query does not re-download or re-hit
  the API.
