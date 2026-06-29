import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError:  # pragma: no cover - runtime fallback for minimal environments
    yaml = None


DEFAULT_HYPERFRAMES_SOURCE = None
DEFAULT_seosona_SKILL = None


def _exists(root: str, relative_path: str) -> bool:
    return os.path.exists(os.path.join(root, relative_path))


def _read_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def _hyperframes_readme_candidates(source_root: str) -> List[str]:
    candidates = [
        os.path.join(source_root, "README.md"),
        os.path.join(source_root, "packages", "cli", "README.md"),
        os.path.join(source_root, "packages", "core", "README.md"),
        os.path.join(source_root, "packages", "engine", "README.md"),
    ]
    return [path for path in candidates if os.path.exists(path)]


def _load_config(project_root: str) -> Dict[str, Any]:
    config_path = os.path.join(project_root, "system_config.yaml")
    if not os.path.exists(config_path) or yaml is None:
        return {}
    with open(config_path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _first_existing_path(candidates: List[Path]) -> str:
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return str(candidates[0]) if candidates else ""


def _default_external_sources(project_root: str) -> Dict[str, str]:
    project_path = Path(project_root).resolve()
    project_drive = Path(project_path.anchor) if project_path.anchor else project_path
    home_downloads = Path.home() / "Downloads"
    drive_downloads = project_drive / "Downloads"

    hyperframes_candidates = [
        Path(os.environ["SEOSONA_HYPERFRAMES_SOURCE"]).expanduser()
    ] if os.environ.get("SEOSONA_HYPERFRAMES_SOURCE") else []
    hyperframes_candidates.extend([
        project_path / "5_FRAMEWORK" / "hf_engine",
        project_path / "5_FRAMEWORK" / "hf_engine" / "hyperframes-main",
        project_path / "5_FRAMEWORK" / "hf_core",
        drive_downloads / "hyperframes-main",
        home_downloads / "hyperframes-main",
    ])

    seosona_candidates = [
        Path(os.environ["SEOSONA_seosona_SKILL"]).expanduser()
    ] if os.environ.get("SEOSONA_seosona_SKILL") else []
    seosona_candidates.extend([
        project_path / ".agents" / "skills" / "seosona-news-maker" / "SKILL.md",
        drive_downloads / "seosona-news-maker_SKILL.md",
        home_downloads / "seosona-news-maker_SKILL.md",
    ])

    return {
        "hyperframes_source": _first_existing_path(hyperframes_candidates),
        "seosona_skill_path": _first_existing_path(seosona_candidates),
    }


def run_integration_audit(
    project_root: str,
    hyperframes_source: str = DEFAULT_HYPERFRAMES_SOURCE,
    seosona_skill_path: str = DEFAULT_seosona_SKILL,
) -> Dict[str, Any]:
    project_root = os.path.abspath(project_root)
    defaults = _default_external_sources(project_root)
    hyperframes_source = hyperframes_source or defaults["hyperframes_source"]
    seosona_skill_path = seosona_skill_path or defaults["seosona_skill_path"]
    checks: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any, issue_id: str = "", severity: str = "P2") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok and issue_id:
            issues.append({"id": issue_id, "severity": severity, "area": name, "detail": detail})

    hyperframes_source = os.path.abspath(hyperframes_source)
    seosona_skill_path = os.path.abspath(seosona_skill_path)

    check(
        "HyperFrames local source",
        os.path.isdir(hyperframes_source)
        and os.path.exists(os.path.join(hyperframes_source, "package.json"))
        and bool(_hyperframes_readme_candidates(hyperframes_source)),
        hyperframes_source,
        "SV-INT-HYPERFRAMES-SOURCE",
        "P1",
    )
    check(
        "SEOSONA source skill",
        os.path.isfile(seosona_skill_path),
        seosona_skill_path,
        "SV-INT-seosona-SOURCE",
        "P1",
    )

    required_project_files = [
        (".agents/skills/hyperframes/SKILL.md", "SV-INT-HYPERFRAMES-SKILL"),
        (".agents/skills/seosona-news-maker/SKILL.md", "SV-INT-seosona-SKILL"),
        ("6_SOP/HYPERFRAMES_INTEGRATION.md", "SV-INT-HYPERFRAMES-SOP"),
        ("6_SOP/tech_news_faceless_sop.md", "SV-INT-NEWS-SOP"),
        ("4_BRAIN/news_video_standards.py", "SV-INT-NEWS-STANDARDS"),
        ("4_BRAIN/video_engine.py", "SV-INT-VIDEO-ENGINE"),
        ("4_BRAIN/native_composer.py", "SV-INT-NATIVE-COMPOSER"),
        ("4_BRAIN/scene_composer.py", "SV-INT-SCENE-COMPOSER"),
    ]
    for relative_path, issue_id in required_project_files:
        check(f"project artifact: {relative_path}", _exists(project_root, relative_path), relative_path, issue_id, "P1")

    # New engine: templates are JSON (structure only) under 7_ASSETS/templates/,
    # consumed by native_composer.fill_template (the old HTML scaffolds are retired).
    templates_dir = os.path.join(project_root, "7_ASSETS", "templates")
    json_templates = [f for f in os.listdir(templates_dir)] if os.path.isdir(templates_dir) else []
    json_templates = [f for f in json_templates if f.endswith(".json")]
    check(
        "JSON video templates present (7_ASSETS/templates/*.json)",
        len(json_templates) > 0,
        f"{len(json_templates)} templates",
        "SV-INT-JSON-TEMPLATES",
        "P1",
    )

    asset_dirs = [
        ("7_ASSETS/audio/bgm", (".mp3", ".wav")),
        ("7_ASSETS/audio/sfx/pops", (".wav", ".mp3")),
        ("7_ASSETS/audio/sfx/transitions", (".wav", ".mp3")),
        ("7_ASSETS/brand/fonts", (".ttf", ".otf")),
    ]
    for relative_path, suffixes in asset_dirs:
        absolute = os.path.join(project_root, relative_path)
        files = []
        if os.path.isdir(absolute):
            files = [item for item in os.listdir(absolute) if item.lower().endswith(suffixes)]
        check(
            f"asset library: {relative_path}",
            bool(files),
            {"path": relative_path, "count": len(files)},
            "SV-INT-ASSET-LIBRARY",
            "P1",
        )

    config = _load_config(project_root)
    voice = (((config.get("profiles") or {}).get("seosona") or {}).get("voice") or {})
    required_gender = str(voice.get("required_gender", "")).lower()
    required_accent = str(voice.get("required_accent", "")).lower()
    fallback_voice = str(voice.get("fallback_voice", ""))
    reference_audio = str(voice.get("reference_audio", ""))
    check(
        "voice policy: male southern",
        required_gender == "male" and required_accent == "southern",
        {"required_gender": required_gender, "required_accent": required_accent},
        "SV-INT-VOICE-POLICY",
        "P1",
    )
    check(
        "voice fallback: Vietnamese male",
        fallback_voice == "vi-VN-NamMinhNeural",
        {"fallback_voice": fallback_voice},
        "SV-INT-VOICE-FALLBACK",
        "P1",
    )
    check(
        "voice reference: male southern sample",
        bool(reference_audio) and _exists(project_root, reference_audio),
        {"reference_audio": reference_audio},
        "SV-INT-VOICE-REFERENCE",
        "P1",
    )

    _sk = _read_text(seosona_skill_path).upper()
    check(
        "SEOSONA rules assimilated: text separate from pronunciation",
        # Language-robust: the SKILL may be VN ("phiên âm") or EN ("pronunciation"/"display").
        "TEXT" in _sk and any(t in _sk for t in ("PHIEN", "PHI", "PRONUNCIATION", "DISPLAY")),
        seosona_skill_path,
        "SV-INT-seosona-RULES",
        "P2",
    )

    hyperframes_readme = "\n".join(_read_text(path) for path in _hyperframes_readme_candidates(hyperframes_source))
    check(
        "HyperFrames source capability: HTML render video",
        (
            "Render video" in hyperframes_readme
            or "render video" in hyperframes_readme
            or "rendering HTML video" in hyperframes_readme
            or "web-page-to-video" in hyperframes_readme
        ),
        _hyperframes_readme_candidates(hyperframes_source),
        "SV-INT-HYPERFRAMES-CAPABILITY",
        "P2",
    )

    return {
        "schema": "seosona.video.integration_audit.v1",
        "ok": not issues,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_root": project_root,
        "sources": {
            "hyperframes_local": hyperframes_source,
            "seosona_skill": seosona_skill_path,
            "hermes_agent": "https://github.com/NousResearch/hermes-agent",
            "hyperframes_upstream": "https://github.com/heygen-com/hyperframes",
        },
        "checks": checks,
        "issues": issues,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Audit SEOSONA Video external integration readiness.")
    parser.add_argument("--project-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    parser.add_argument("--hyperframes-source", default=DEFAULT_HYPERFRAMES_SOURCE)
    parser.add_argument("--seosona-skill", default=DEFAULT_seosona_SKILL)
    args = parser.parse_args()

    result = run_integration_audit(args.project_root, args.hyperframes_source, args.seosona_skill)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
