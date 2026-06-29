# Google Drive / Sheets Management Layer (task #15)

The plan to manage the whole factory on Google Drive/Sheets/Docs. The TOOLING now
exists in-repo; the only blocker is **credentials** (the user must supply them). This
SOP defines the architecture so it connects cleanly — and clarifies the TWO Drive
paths so they don't overlap.

## Two Drive roles (do NOT merge — different jobs, different auth)

| Role | Component | Auth | Use |
|---|---|---|---|
| **Publish outputs** (push a finished video to Drive) | `1_AGENTS/publisher_agent/gdrive_uploader.py` | **service account** JSON | the factory PUBLISH stage (`SEOSONA_PUBLISH=google_drive`) — unattended, one-way upload |
| **Manage everything** (control surface: Docs/Sheets/Slides/folders CRUD) | `2_SKILLS/os_gdrive-manager/` (`gdrive.py`) | **OAuth2** `credentials.json` | create/read/update Sheets+Docs, organise folders, the human-facing management layer; destructive ops gated by `safety.py` |

Rule: the **publisher** is the autonomous one-way push (service account, no prompts);
**os_gdrive-manager** is the interactive management/control surface (OAuth). They share
the platform, not the code path.

## The management-layer vision (what #15 delivers)
Mirror the factory's state TO Google Sheets/Drive so it can be run/observed from there:
- **Queue** ← a Sheet tab ↔ `0_INPUT_INBOX/production_queue.yaml` (edit topics in Sheets → factory produces).
- **Reports/ledger** → push `3_MEMORY/learning/ledger.json` + per-video manifests to a Sheet (the dashboard mirror, OBSERVE in [[autonomous-factory-northstar]]).
- **Outputs** → finished `video.mp4` + `script.txt` to a Drive folder (publisher).
- **Docs** → SEO metadata / scripts as Google Docs (os_gdrive-manager `mkdoc`).

## Setup to UNBLOCK (the only thing missing)
1. **OAuth (management):** create an OAuth client in Google Cloud → download
   `credentials.json` → `1_CONFIG/credentials/credentials.json`; run
   `python 2_SKILLS/os_gdrive-manager/scripts/auth_setup.py` once (stores token).
   Deps: `pip install google-api-python-client google-auth-oauthlib` (not yet pinned).
2. **Service account (publish):** create a service account → share the target Drive
   folder with its email → `1_CONFIG/credentials/google_drive.json`
   (`GDRIVE_SERVICE_ACCOUNT_FILE` + `GDRIVE_FOLDER_ID`). See `1_CONFIG/README.md`.
3. Both credential files are **gitignored** (`1_CONFIG/credentials/*.json`, only
   `*.example.json` is tracked). Never commit real keys.

## Status
- ✅ Tooling present: publisher uploader + os_gdrive-manager skill (Drive/Docs/Sheets/Slides).
- ✅ Architecture defined (this doc) — two roles, no overlap, connected to the factory loop.
- ⚠️ **Blocked on credentials** (user provides OAuth + service-account JSON). Once added,
   wire the Sheets queue/ledger mirror (a small sync script) to finish the layer.
