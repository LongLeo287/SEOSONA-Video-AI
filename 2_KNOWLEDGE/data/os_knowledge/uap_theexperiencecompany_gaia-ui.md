# KI: theexperiencecompany/gaia-ui

## Overview
A collection of production-ready UI components designed specifically for building AI assistants and chatbots. These are the components we use at GAIA, now available for anyone building conversational interfaces.

## Architecture & Tech Stack
- Node.js / TypeScript / JavaScript
- **Total files:** 124 files across 24 directories
- **File types:** .md: 48, .tsx: 36, .mjs: 13, .json: 9, .ts: 6, .js: 3, .yaml: 2

## Documentation Sections
- GAIA UI - Component Registry
- Why This Library?
- Our Philosophy
- Getting Started
- Alternative: Using shadcn CLI
- Base Components
- Documentation
- Current Status
- Community & Support
- Contributing
- Development
- Install dependencies
- Run dev server
- Build registry
- Type check
- Built With
- Star History
- License

## Core Structure
```
  .env.example
  .gitignore
  .npmrc
  AGENTS.md
  CHANGELOG.md
  CONTRIBUTING.md
  DESIGN.json
  DESIGN.md
  LICENSE
  PRODUCT.md
  README.md
  biome.json
  components.json
  mdx-components.tsx
  next.config.ts
  open-next.config.ts
  package.json
  pnpm-lock.yaml
  postcss.config.mjs
  registry.json
  skills-lock.json
  tsconfig.json
  wrangler.jsonc
  .agents/
    skills/
      impeccable/
        SKILL.md
        agents/
          openai.yaml
        reference/
          adapt.md
          animate.md
          audit.md
          bolder.md
          brand.md
          clarify.md
          cognitive-load.md
          color-and-contrast.md
          colorize.md
          craft.md
          critique.md
          delight.md
          distill.md
          document.md
          extract.md
          harden.md
          heuristics-scoring.md
          interaction-design.md
          layout.md
          live.md
          motion-design.md
          onboard.md
          optimize.md
          overdrive.md
          personas.md
          polish.md
          product.md
          quieter.md
          responsive-design.md
          shape.md
          spatial-design.md
          teach.md
          typeset.md
          typography.md
          ux-writing.md
        scripts/
          cleanup-deprecated.mjs
          command-metadata.json
          design-parser.mjs
          detect-csp.mjs
          is-generated.mjs
          live-accept.mjs
          live-browser.js
          live-inject.mjs
          live-poll.mjs
          live-server.mjs
          live-wrap.mjs
          live.mjs
          load-context.mjs
          modern-screenshot.umd.js
          pin.mjs
  .changeset/
    README.md
    config.json
    iphone-mockup-chat-demo.md
  .claude/
    skills/
      impeccable
  .github/
    CONTRIBUTING.md
    LICENSE.md
    REGISTRY.md
    ROADMAP.md
    workflows/
      changeset-check.yml
      publish.yml
  app/
    globals.css
    layout.tsx
    manifest.ts
    page.tsx
    robots.ts
    sitemap.ts
    api/
      og/
        route.tsx
    docs/
      layout.tsx
      [[...slug]]/
        page.tsx
  bin/
    gaia-ui.js
  components/
    core/
      code-block.tsx
      command-menu-client.tsx
      command-menu.tsx
      component-preview-client.tsx
      component-preview.tsx
      components-grid.tsx
      components-preview-card.tsx
      contributors-page.tsx
      copy-button.tsx
      doc-page-layout.tsx
      docs-sidebar-client.tsx
      docs-sidebar.tsx
      
```

## Quick Start
```bash
npx @heygaia/ui add navbar-menu
npx @heygaia/ui add raised-button chat-bubble tool-calls-section
npx shadcn@latest add https://ui.heygaia.io/r/navbar-menu.json
Then use namespace syntax:
This registry uses standard shadcn/ui base components. Install them separately:
```

## Agent Configuration

--- AGENTS.md ---
# AGENTS.md

Hey there! Welcome to the Gaia UI library. This guide will walk you through everything you need to know about adding new components, maintaining design consistency, and keeping things beautiful.

## Quick Start: Adding a New Component

When you add a new component, you'll need to touch a few places. Here's the checklist:

### 1. Create the Component File

Add your component to `registry/new-york/ui/your-component.tsx`. This is where the actual component code lives.

```
registry/
└── new-york/
    └── ui/
        └── your-component.tsx  ← Your new component
```

### 2. Register It

Open `registry.json` in the project root and add your component to the `items` array:

```json
{
  "name": "your-component",
  "type": "registry:ui",
  "title": "Your Component",
  "description": "A brief, compelling description of what this component does.",
  "dependencies": ["any-npm-packages"],
  "registryDependencies": ["icons", "other-gaia-components"],
  "files": [
    {
      "path": "registry/new-york/ui/your-component.tsx",
      "type": "registry:ui"
    }
  ]
}
```

### 3. Add Preview Components

Create preview examples in `components/previews/your-component/`:

```
components/
└── previews/
    └── your-component/
        ├── default.tsx          ← Basic usage example
        ├── with-variants.tsx    ← Different variants
        └── custom-example.tsx   ← Any other demos
```

### 4. Write the Documentation

Create a docs page at `content/docs/components/your-component.mdx`:

```mdx
---
title: Your Component
description: What it does and why someone would use it.
---

<ComponentPreview name="your-component/default" />

## Usage

Show how to use it.

## Installation

<Tabs defaultValue="automatic" className="mt-4">
  <!-- Add both automatic and manual installation options -->
</Tabs>

## Props

Document all the props in a table.
```

### 5. Update Navigation (if needed)

If you're adding a new category or the component needs special placement, update `lib/navigatio

--- CONTRIBUTING.md ---
# Contributing to GAIA UI

Thanks for your interest in contributing! GAIA UI is a registry of production-ready components for AI assistants and chat interfaces, built on [shadcn/ui](https://ui.shadcn.com/). This guide covers everything you need to add components, fix bugs, or improve documentation.

For deeper design and architectural guidance, see [AGENTS.md](./AGENTS.md).

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Ways to Contri

## Analysis Note
> This KI was generated by **enhanced local structural analysis** (no LLM API was available at generation time). It includes full tech stack detection, README parsing, dependency analysis, and feature extraction. For deeper semantic analysis, re-run with an active Gemini or OpenAI API key.
