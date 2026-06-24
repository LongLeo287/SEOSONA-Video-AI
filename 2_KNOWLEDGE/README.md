# 2_KNOWLEDGE — knowledge base (start here)

Project knowledge for SEOSONA Video. **Use the curated layer below — agents read
that, not the raw scratch pile.**

## Curated, usable knowledge (tracked, this is the real KB)
| Path | What |
|------|------|
| `INGESTION_INDEX.md` | **Source of truth** — what repos have been ingested + exactly where each is integrated. Check before ingesting anything new. |
| `hyperframes/` | The render engine docs — `guides/`, `reference/`, `catalog/`. Start at `hyperframes/README.md`. The core knowledge agents use to author/render. |
| `data/` | `brand_guidelines.json` + curated OS-knowledge routing cards (`os_knowledge/`). |
| `raw_data/` | source corpora (e.g. `vietnamese_lines.txt`). |

## `repos/` — raw ingestion scratch (gitignored, NOT the KB)
`2_KNOWLEDGE/repos/*.md` holds raw per-repo distillation notes produced by the
ingestion pipeline. It is **gitignored, read by no code, and mostly not
video-related** (general AI/agent repos). The video-relevant ones are the ones
listed in `INGESTION_INDEX.md`; the rest is a research archive.

> If you're an agent or a human looking for "how do I do X", read the curated layer
> + `INGESTION_INDEX.md` — do not grep the whole `repos/` pile.

Authoritative SEOSONA OS knowledge lives under `~/.seosona/2_KNOWLEDGE/`. Files here
should be concise routing cards connecting local workflows to OS-level capabilities.
