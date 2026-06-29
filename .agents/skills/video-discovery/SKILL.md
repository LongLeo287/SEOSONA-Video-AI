---
name: video-discovery
description: Self-enqueues new work from a maintained source list into the production queue, skipping anything already done or queued.
---

# Video Discovery (loop move #2)

The fix for the "blind loop": the loop identifies its own work instead of a human hand-picking
each item every run. Discovery reads a source list, drops anything already produced or already
queued, and appends the new items to the production queue — so a scheduled run finds fresh work
by itself.

## Implementation
`4_BRAIN/discovery.py` → `discover(dry_run)`. Free/local; PyYAML only.

## How it works
- Source: `0_INPUT_INBOX/sources.txt` (one per line; a GitHub URL or a Vietnamese topic;
  `#` lines ignored).
- Dedup: skips an item whose key `news_videos::<item>` is in the processed-ledger
  (`0_INPUT_INBOX/.processed_ledger.txt`) or that is already in the queue (rule: avoid duplicates).
- Enqueue: appends the new items to `0_INPUT_INBOX/production_queue.yaml` under `news_videos`,
  preserving template placeholders.

## How it connects
- Feeds the **queue** consumed by `scripts/queue_processor.py`.
- Runs automatically at the start of `scripts/daily_production.py` (before the queue), so each
  daily batch self-discovers, then the guarded queue produces the videos.

## Run
```
python 4_BRAIN/discovery.py            # discover + enqueue
python 4_BRAIN/discovery.py --dry-run  # preview only
```

See `2_KNOWLEDGE/loop-engineering/README.md` (Discovery / the blind loop) and
`6_SOP/LOOP_OPERATING_SOP.md`.
