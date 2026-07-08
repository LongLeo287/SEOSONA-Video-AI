# KI: nextlevelbuilder/ui-ux-pro-max-skill

## Overview
Repository with 324 files across 56 directories. Primary language: Python (24 files).

## Tech Stack (from code)
- Python (24 files)
- TypeScript (11 files)
- **Total:** 324 files, 56 directories
- **File types:** .csv: 78, .md: 66, .ttf: 54, .json: 44, .txt: 29, .py: 24, .ts: 11, .cjs: 7

## File Structure
```
  .gitignore
  .releaserc.json
  CLAUDE.md
  CONTRIBUTING.md
  LICENSE
  README.md
  skill.json
  .claude/
    skills/
      banner-design/
        SKILL.md
        references/
          banner-sizes-and-styles.md
      brand/
        SKILL.md
        references/
          approval-checklist.md
          asset-organization.md
          brand-guideline-template.md
          color-palette-management.md
          consistency-checklist.md
          logo-usage-rules.md
          messaging-framework.md
          typography-specifications.md
          update.md
          visual-identity.md
          voice-framework.md
        scripts/
          extract-colors.cjs
          inject-brand-context.cjs
          sync-brand-to-tokens.cjs
          validate-asset.cjs
        templates/
          brand-guidelines-starter.md
      design/
        SKILL.md
        data/
          cip/
            deliverables.csv
            industries.csv
            mockup-contexts.csv
            styles.csv
          icon/
            styles.csv
          logo/
            colors.csv
            industries.csv
            styles.csv
        references/
          banner-sizes-and-styles.md
          cip-deliverable-guide.md
          cip-design.md
          cip-prompt-engineering.md
          cip-style-guide.md
          design-routing.md
          icon-design.md
          logo-color-psychology.md
          logo-design.md
          logo-prompt-engineering.md
          logo-style-guide.md
          slides-copywriting-formulas.md
          slides-create.md
          slides-html-template.md
          slides-layout-patterns.md
          slides-strategies.md
          slides.md
          social-photos-design.md
        scripts/
          cip/
            core.py
            generate.py
            render-html.py
            search.py
          icon/
            generate.py
          logo/
            core.py
            generate.py
            search.py
      design-system/
        SKILL.md
        dat
```

## Agent Configuration
### CLAUDE.md
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

UI UX Pro Max is an AI-powered design intelligence toolkit providing searchable databases of UI styles, color palettes, font pairings, chart types, and UX guidelines. It works as a skill/workflow for AI coding assistants (Claude Code, Windsurf, Cursor, etc.).

## Search Command

```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --domain <domain> [-n <max_results>]
```

**Domain search:**
- `product` - Product type recommendations (SaaS, e-commerce, portfolio)
- `style` - UI styles (glassmorphism, minimalism, brutalism) + AI prompts and CSS keywords
- `typography` - Font pairings with Google Fonts imports
- `color` - Color palettes by product type
- `landing` - Page structure and CTA strategies
- `chart` - Chart types and library recommendations
- `ux` - Best practices and anti-patterns

**Stack search:**
```bash
python3 src/ui-ux-pro-max/scripts/search.py "<query>" --stack <stack>
```
Available stacks: `html-tailwind` (default), `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`, `angular`, `laravel`, `javafx`

## Architecture

```
src/ui-ux-pro-max/                # Source of Truth
├── data/                         # Canonical CSV databases
│   ├── products.csv, styles.csv, colors.csv, typography.csv, ...
│   └── stacks/                   # Stack-s

## Analysis Method
> Factual code-based structural analysis. All data extracted directly from source files. No README. No assumptions.
