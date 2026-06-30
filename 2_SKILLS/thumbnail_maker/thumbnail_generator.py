"""Back-compat shim. The thumbnail logic now lives in thumbnail_maker.py (one module,
one entry point: make_thumbnail). This thin wrapper keeps older callers that import
`generate_html_thumbnail` working until they migrate.

Safe to delete once 4_BRAIN/video_engine.py is committed — its working-tree version
already calls make_thumbnail directly.
"""
from .thumbnail_maker import make_thumbnail, _render_html  # noqa: F401


def generate_html_thumbnail(output_path, top_label, main_title, hook, cta,
                            portrait_path=None, manual_title=None, manual_cta=None,
                            aspect_ratio="9:16", brand="seosona", subtext_italic="",
                            layout_type="auto"):
    """Legacy signature → delegates to the consolidated renderer."""
    return _render_html(output_path, top_label, main_title, hook, cta, portrait_path,
                        manual_title, manual_cta, aspect_ratio, brand, subtext_italic,
                        layout_type)
