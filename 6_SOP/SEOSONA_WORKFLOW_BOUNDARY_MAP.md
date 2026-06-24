# SEOSONA Workflow Boundary Map

Updated: 2026-06-21

This document is the routing contract for SEOSONA Video. It separates image
production from video production so agents do not mix post images, thumbnails,
template cloning, news videos, and course videos inside one ambiguous pipeline.

## Canonical Workflows

| Workflow | Purpose | Entrypoint | Brand | Primary Output |
| --- | --- | --- | --- | --- |
| Clone Video To Template | Analyze an existing video and export a reusable HyperFrames template package. | `npm run template:clone -- <video_path> <template_name>` | SEOSONA or CQA | `5_FRAMEWORK/<template>/`, `7_ASSETS/video_templates/<template>/` |
| Post Image | Create static social post or carousel image assets. | `npm run post:image -- <text_or_file>` | Auto-detected SEOSONA or CQA | `8_WORKSPACE/Social_Campaigns/<campaign>/` PNG + caption |
| Thumbnail | Create video cover images only. | `npm run thumbnail:create -- <title_or_hook>` | Auto-detected SEOSONA or CQA | `8_WORKSPACE/Video_Thumbnails/<project>/` PNG |
| SEOSONA News Video | Create a complete Vietnamese SEOSONA news video. | `npm run video:news -- <script_or_file_or_url> [project_name] [aspect_ratio]` | SEOSONA | `8_WORKSPACE/<project>/` MP4 + SRT + thumbnail |
| CQA Course Video | Create a complete Chi Quyet Academy knowledge or course video. | `npm run video:course -- <script_or_file> [project_name] [aspect_ratio]` | CQA | `8_WORKSPACE/<project>/` MP4 + SRT + thumbnail |

## Hard Boundaries

1. Post Image and Thumbnail are image workflows. They must not render MP4 files,
   call TTS, create SRT files, or invoke HyperFrames video rendering.
2. News Video and Course Video are video workflows. They must always produce an
   MP4, SRT, thumbnail, voice track, BGM/SFX where available, and a production
   manifest when the renderer supports it.
3. Clone Video To Template is a template factory workflow. It may produce a
   preview render and thumbnail for validation, but it must not be treated as
   final content publishing.
4. `4_BRAIN/pipeline_manager.py` is reserved for video workflows. The legacy
   `carousel` path is blocked at runtime and should not be used as an entrypoint.
5. Generic HyperFrames skills are vendor capabilities. SEOSONA production
   workflows must go through the canonical entrypoints above.
6. **Supergraph Architecture:** All video workflows (`video:news`, `video:course`) are now routed through the `Supergraph DAG`. The legacy `pipeline_manager.py` acts as a `MAIN_PIPELINE` node wrapped by the `OODA Loop` for auto-correction. All workflows MUST terminate at the `EVALUATE_NODE` for generating Machine Learning feedback reports.

## Ownership

| Area | Owner Files |
| --- | --- |
| Routing & Supergraph | `4_BRAIN/workflow_router.py`, `4_BRAIN/graph_executor.py`, `package.json` |
| Video rendering | `4_BRAIN/pipeline_manager.py`, `4_BRAIN/news_video_standards.py`, HyperFrames templates |
| Auto-Correction (OODA) | `4_BRAIN/ooda_loop.py`, `1_AGENTS/editor_agent/editor.py` |
| Machine Learning / Audit | `1_AGENTS/analytics_feedback_agent/feedback_generator.py`, `scripts/seosona-project-audit.cjs` |
| Template cloning | `4_BRAIN/video_template_factory.py`, `scripts/export-video-template.py` |
| Post images | `scripts/workflow_social_post.py`, `1_AGENTS/carousel_writer_agent/`, `2_SKILLS/carousel_maker/` |
| Thumbnails | `scripts/workflow_thumbnail.py`, `2_SKILLS/thumbnail_maker/` |

## Operating Notes

- Use `video:news` for SEOSONA news. Do not pass `brand=cqa` to news videos.
- Use `video:course` for Chi Quyet Academy knowledge and course content. Do not
  reuse news scene logic unless the content is intentionally a news explainer.
- Use `post:image` for Facebook, LinkedIn, TikTok image posts, carousels, and
  campaign images.
- Use `thumbnail:create` for cover images attached to a video package.
- If a workflow needs both a video and a post image, run the video workflow first,
  then run the image workflow from the final title, hook, or script summary.
