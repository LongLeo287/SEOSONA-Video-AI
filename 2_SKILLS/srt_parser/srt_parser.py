"""
SRT Parser Skill — Reads and parses standard .srt subtitle files.
"""
import re

def parse_srt(srt_path):
    """
    Parses a standard SubRip (.srt) file into a list of dicts.
    Returns: [{"index": 1, "start": 0.0, "end": 2.5, "text": "Hello"}, ...]
    """
    entries = []

    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by blank lines
    blocks = re.split(r'\n\s*\n', content.strip())

    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) < 3:
            continue

        try:
            index = int(lines[0].strip())
        except ValueError:
            continue

        # Parse timecode line: 00:00:01,500 --> 00:00:04,200
        time_match = re.match(
            r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*(\d{2}):(\d{2}):(\d{2}),(\d{3})',
            lines[1].strip()
        )
        if not time_match:
            continue

        g = time_match.groups()
        start = int(g[0])*3600 + int(g[1])*60 + int(g[2]) + int(g[3])/1000
        end = int(g[4])*3600 + int(g[5])*60 + int(g[6]) + int(g[7])/1000

        text = '\n'.join(lines[2:]).strip()

        entries.append({
            "index": index,
            "start": start,
            "end": end,
            "text": text
        })

    print(f"[SRT Parser] Parsed {len(entries)} entries from {srt_path}")
    return entries

def srt_to_full_text(entries):
    """
    Combines all SRT entries into a single text block.
    Useful for feeding into LLM for analysis.
    """
    return ' '.join([e['text'] for e in entries])

def get_total_duration(entries):
    """Returns total duration in seconds from parsed SRT entries."""
    if not entries:
        return 0
    return entries[-1]['end']

def find_entries_in_range(entries, start_sec, end_sec):
    """Returns all SRT entries within a time range."""
    return [e for e in entries if e['start'] >= start_sec and e['end'] <= end_sec]
