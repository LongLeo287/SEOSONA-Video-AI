# -*- coding: utf-8 -*-
"""Mirror the factory's state to a local snapshot (always) and Google Sheets (when
credentials exist). The "management layer" surface of task #15 — see
6_SOP/GOOGLE_DRIVE_SHEETS_LAYER.md.

Gathers three views:
  • Queue   — 0_INPUT_INBOX/production_queue.yaml (what's pending)
  • Ledger  — 3_MEMORY/learning/ledger.json (what's winning, per variant)
  • Videos  — every production_manifest.json (what was made + QA score)

Writes them to 3_MEMORY/factory_state/*.csv NOW (a local control view, no creds needed),
and — IF 1_CONFIG/credentials/credentials.json + google-api libs are present — pushes
the same tables to a Google Sheet so the factory can be run/observed from Sheets.

    python scripts/sheets_mirror.py            # snapshot (+ Sheets if creds)
    python scripts/sheets_mirror.py --sheet <spreadsheetId>
"""
import os, sys, json, csv

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "4_BRAIN"))
OUT = os.path.join(ROOT, "3_MEMORY", "factory_state")
CRED = os.path.join(ROOT, "1_CONFIG", "credentials", "credentials.json")


def _queue_rows():
    rows = [["category", "item"]]
    try:
        import yaml
        q = yaml.safe_load(open(os.path.join(ROOT, "0_INPUT_INBOX", "production_queue.yaml"),
                                  encoding="utf-8")) or {}
        for cat, items in q.items():
            for it in (items or []):
                if it and str(it).strip():
                    rows.append([cat, str(it).strip()])
    except Exception as e:
        rows.append(["(error)", str(e)])
    return rows


def _ledger_rows():
    rows = [["dimension", "value", "n", "avg_score", "qa_pass_rate", "views_total"]]
    p = os.path.join(ROOT, "3_MEMORY", "learning", "ledger.json")
    if os.path.exists(p):
        led = json.load(open(p, encoding="utf-8"))
        for dim, vals in (led.get("dimensions") or {}).items():
            for val, s in vals.items():
                rows.append([dim, val, s.get("n"), s.get("avg_score"),
                             s.get("qa_pass_rate"), s.get("views_total")])
    return rows


def _video_rows():
    import production_manifest as pm
    rows = [["video_id", "template", "brand", "aspect", "voice", "topic",
             "duration_s", "qa_score", "qa_pass", "created"]]
    for m in pm.scan():
        v = m.get("variant", {}); q = m.get("quality", {})
        rows.append([m.get("video_id"), v.get("template"), v.get("brand"), v.get("aspect"),
                     v.get("voice"), v.get("topic"), m.get("duration_s"),
                     q.get("score"), q.get("pass"), m.get("created")])
    return rows


def _write_csv(name, rows):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name + ".csv")
    with open(p, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    return p


def _push_sheets(tabs, spreadsheet_id=None):
    """Push {tab_name: rows} to a Google Sheet. Returns the sheet URL or None."""
    if not os.path.exists(CRED):
        print(f"[sheets_mirror] no {CRED} — local snapshot only. Add OAuth credentials "
              f"to mirror to Google Sheets (see 6_SOP/GOOGLE_DRIVE_SHEETS_LAYER.md).")
        return None
    try:
        from google.oauth2.credentials import Credentials  # noqa: F401
        from googleapiclient.discovery import build  # noqa: F401
        # Auth via the os_gdrive-manager token (run its auth_setup.py once).
        # Integration point: create/update the spreadsheet + write each tab's values.
        # Left as the explicit wire-up once credentials exist (no guessing the token path).
        print("[sheets_mirror] credentials present — TODO: wire Sheets push via "
              "os_gdrive-manager token. Tabs ready: " + ", ".join(tabs))
        return None
    except ImportError:
        print("[sheets_mirror] pip install google-api-python-client google-auth-oauthlib "
              "to enable the Sheets push.")
        return None


def run(spreadsheet_id=None):
    tabs = {"Queue": _queue_rows(), "Ledger": _ledger_rows(), "Videos": _video_rows()}
    for name, rows in tabs.items():
        p = _write_csv(name.lower(), rows)
        print(f"[sheets_mirror] {name}: {len(rows)-1} rows -> {p}")
    _push_sheets(tabs, spreadsheet_id)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="target spreadsheetId (else create/local-only)")
    a = ap.parse_args()
    run(a.sheet)
