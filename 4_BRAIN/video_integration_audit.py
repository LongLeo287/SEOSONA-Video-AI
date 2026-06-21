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
DEFAULT_LOHA_SKILL = None


def _exists(root: str, relative_path: str) -> bool:
    return os.path.exists(os.path.join(root, relative_path))


def _read_text(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


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
        drive_downloads / "hyperframes-main",
        home_downloads / "hyperframes-main",
    ])

    loha_candidates = [
        Path(os.environ["SEOSONA_LOHA_SKILL"]).expanduser()
    ] if os.environ.get("SEOSONA_LOHA_SKILL") else []
    loha_candidates.extend([
        drive_downloads / "loha-video-maker_SKILL.md",
        home_downloads / "loha-video-maker_SKILL.md",
    ])

    return {
        "hyperframes_source": _first_existing_path(hyperframes_candidates),
        "loha_skill_path": _first_existing_path(loha_candidates),
    }


def run_integration_audit(
    project_root: str,
    hyperframes_source: str = DEFAULT_HYPERFRAMES_SOURCE,
    loha_skill_path: str = DEFAULT_LOHA_SKILL,
) -> Dict[str, Any]:
    project_root = os.path.abspath(project_root)
    defaults = _default_external_sources(project_root)
    hyperframes_source = hyperframes_source or defaults["hyperframes_source"]
    loha_skill_path = loha_skill_path or defaults["loha_skill_path"]
    checks: List[Dict[str, Any]] = []
    issues: List[Dict[str, Any]] = []

    def check(name: str, ok: bool, detail: Any, issue_id: str = "", severity: str = "P2") -> None:
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        if not ok and issue_id:
            issues.append({"id": issue_id, "severity": severity, "area": name, "detail": detail})

    hyperframes_source = os.path.abspath(hyperframes_source)
    loha_skill_path = os.path.abspath(loha_skill_path)

    check(
        "HyperFrames local source",
        os.path.isdir(hyperframes_source)
        and os.path.exists(os.path.join(hyperframes_source, "package.json"))
        and os.path.exists(os.path.join(hyperframes_source, "README.md")),
        hyperframes_source,
        "SV-INT-HYPERFRAMES-SOURCE",
        "P1",
    )
    check(
        "LoHa source skill",
        os.path.isfile(loha_skill_path),
        loha_skill_path,
        "SV-INT-LOHA-SOURCE",
        "P1",
    )

    required_project_files = [
        (".agents/skills/hyperframes/SKILL.md", "SV-INT-HYPERFRAMES-SKILL"),
        (".agents/skills/loha-video-maker/SKILL.md", "SV-INT-LOHA-SKILL"),
        ("6_SOP/HYPERFRAMES_INTEGRATION.md", "SV-INT-HYPERFRAMES-SOP"),
        ("6_SOP/tech_news_faceless_sop.md", "SV-INT-NEWS-SOP"),
        ("4_BRAIN/news_video_standards.py", "SV-INT-NEWS-STANDARDS"),
        ("4_BRAIN/video_template_factory.py", "SV-INT-TEMPLATE-FACTORY"),
    ]
    for relative_path, issue_id in required_project_files:
        check(f"project artifact: {relative_path}", _exists(project_root, relative_path), relative_path, issue_id, "P1")

    template_dirs = [
        "5_FRAMEWORK/news_spatial_hyperframes",
        "5_FRAMEWORK/news_loop_path_hyperframes",
    ]
    for relative_path in template_dirs:
        check(
            f"HyperFrames template: {relative_path}",
            _exists(project_root, os.path.join(relative_path, "index.html")),
            relative_path,
            "SV-INT-HYPERFRAMES-TEMPLATE",
            "P1",
        )

    asset_dirs = [
        ("7_ASSETS/bgm", (".mp3", ".wav")),
        ("7_ASSETS/sfx/pops", (".wav", ".mp3")),
        ("7_ASSETS/sfx/transitions", (".wav", ".mp3")),
        ("7_ASSETS/fonts", (".ttf", ".otf")),
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

    loha_text = _read_text(loha_skill_path)
    check(
        "LoHa rules assimilated: text separate from pronunciation",
        "TEXT" in loha_text.upper() and ("PHIEN" in loha_text.upper() or "PHI" in loha_text.upper()),
        loha_skill_path,
        "SV-INT-LOHA-RULES",
        "P2",
    )

    hyperframes_readme = _read_text(os.path.join(hyperframes_source, "README.md"))
    check(
        "HyperFrames source capability: HTML render video",
        "Render video" in hyperframes_readme or "render video" in hyperframes_readme,
        os.path.join(hyperframes_source, "README.md"),
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
            "loha_skill": loha_skill_path,
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
    parser.add_argument("--loha-skill", default=DEFAULT_LOHA_SKILL)
    args = parser.parse_args()

    result = run_integration_audit(args.project_root, args.hyperframes_source, args.loha_skill)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
