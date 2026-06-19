# Video Templates

Directory for extending video template types beyond the default Tech News Faceless format.

## Current Templates

| Template | File | Description |
|:---------|:-----|:------------|
| Tech News Faceless | `moviepy_wrapper/tech_news_template.py` | Faceless tech/SEO news video |

## How to Create a New Template

1. Create a new `.py` file in `moviepy_wrapper/`.
2. Inherit the structure from `TechNewsTemplate`:
   - Constructor accepts `brand` and reads `system_config.yaml`.
   - Method `render(data, output_path)` handles the full pipeline.
3. Register the template in `pipeline_manager.py`.

## Future Template Ideas

- **Tutorial Template**: Step-by-step guides with screen recording overlay.
- **Review Template**: Side-by-side product comparison (split screen).
- **Comparison Template**: VS format (A vs B) with charts.
- **Quote Template**: Inspirational quote overlay, ideal for Reels/Shorts.
