# -*- coding: utf-8 -*-
"""SEOSONA Video — source ingester (SYSTEM capability).

Turn ANY source (PDF, DOCX, PPTX, HTML page, URL, ...) into clean Markdown so it can become
knowledge. Uses Microsoft's `markitdown` (MIT). Free/local. This is the SYSTEM side of the
two-part model (it makes the brain learn faster); curated outputs then move into
`2_KNOWLEDGE/<area>/` per `6_SOP/REPO_VETTING_SOP.md`.

  python 2_KNOWLEDGE/scripts/ingest_source.py <file_or_url> [output_name]
  → writes 2_KNOWLEDGE/_ingest_inbox/<name>.md  (review, then file it where it belongs)
"""
import os
import sys
import re
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[2]
INBOX = ROOT / "2_KNOWLEDGE" / "_ingest_inbox"


def ingest(source, out_name=None):
    try:
        from markitdown import MarkItDown
    except ImportError:
        print("[ingest] markitdown not installed → pip install markitdown")
        return None
    try:
        result = MarkItDown().convert(source)
    except Exception as e:
        print(f"[ingest] convert failed for {source}: {e}")
        return None
    text = getattr(result, "text_content", "") or ""
    if not text.strip():
        print(f"[ingest] no text extracted from {source}")
        return None
    INBOX.mkdir(parents=True, exist_ok=True)
    base = out_name or re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(str(source)).stem or "source").strip("-")
    out = INBOX / f"{base}.md"
    header = f"<!-- ingested {datetime.now().isoformat(timespec='seconds')} from: {source} -->\n\n"
    out.write_text(header + text, encoding="utf-8")
    print(f"[ingest] {source} → {out}  ({len(text)} chars)")
    return str(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python 2_KNOWLEDGE/scripts/ingest_source.py <file_or_url> [output_name]")
        sys.exit(1)
    r = ingest(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    sys.exit(0 if r else 1)
