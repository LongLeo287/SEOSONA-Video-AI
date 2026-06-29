# KI: imskyleen/animate-ui

## Overview
Visit [animate-ui.com](https://animate-ui.com/docs) to view the documentation.

## Architecture & Tech Stack
- Node.js / TypeScript / JavaScript
- **Total files:** 111 files across 37 directories
- **File types:** .tsx: 50, .mdx: 26, .json: 9, .md: 5, .ts: 5, .yml: 4, .mjs: 3
- **Dev dependencies:** @commitlint/cli, @commitlint/config-conventional, @eslint/js, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom, @workspace/eslint-config

## Documentation Sections
- Documentation
- Contributing
- Code of Conduct
- License

## Available Commands
- `npm run build` -- turbo build
- `npm run dev` -- turbo dev
- `npm run lint` -- turbo lint
- `npm run format` -- prettier --write "**/*.{ts,tsx,md}"
- `npm run format:write` -- prettier --write "**/*.{ts,tsx,mdx}" --cache
- `npm run format:check` -- prettier --check "**/*.{ts,tsx,mdx}" --cache
- `npm run registry:build` -- pnpm --filter animate-ui registry:build
- `npm run prepare` -- husky

## Core Structure
```
  .gitignore
  .npmrc
  .prettierrc
  CODE_OF_CONDUCT.md
  CONTRIBUTING.md
  LICENSE.md
  README.md
  commitlint.config.mjs
  package.json
  pnpm-lock.yaml
  pnpm-workspace.yaml
  tsconfig.json
  turbo.json
  .cursor/
    mcp.json
  .github/
    FUNDING.yml
    ISSUE_TEMPLATE/
      1.bug_report.yml
      2.feature_request.yml
      3.documentation.yml
  .husky/
    commit-msg
    pre-push
  .vscode/
    settings.json
  apps/
    www/
      .gitignore
      README.md
      eslint.config.js
      mdx-components.tsx
      next.config.mjs
      package.json
      postcss.config.mjs
      source.config.ts
      tsconfig.json
      __registry__/
        index.tsx
      app/
        favicon.ico
        globals.css
        layout.config.tsx
        layout.tsx
        (home)/
          page.tsx
        api/
          search/
            route.ts
        docs/
          layout.tsx
          [[...slug]]/
            page.tsx
        docs-og/
          [...slug]/
            route.tsx
        examples/
          layout.tsx
          demo-components-radix-sidebar/
            page.tsx
        llms-full.txt/
          route.ts
        llms.mdx/
          [[...slug]]/
            route.ts
        static.json/
          route.ts
      components/
        features.tsx
        footer.tsx
        header.tsx
        hero-background.tsx
        hero.tsx
        icon-logo.tsx
        logo.tsx
        animate/
          tabs.tsx
          theme-switcher.tsx
        backgrounds/
          bubble.tsx
        buttons/
          copy.tsx
        docs/
          callout.tsx
          changelog.tsx
          code-tabs.tsx
          codeblock.tsx
          component-installation.tsx
          component-manual-installation.tsx
          component-preview.tsx
          component-wrapper.tsx
          docs-author.tsx
          docs-breadcrumb.tsx
          dynamic-codeblock.tsx
          external-link.tsx
          icon-showcase.tsx
          icons-fallback.tsx
          icons.tsx
          iframe.tsx
          motion-grid-editor.tsx
          nav.tsx
          page-actions.tsx
          sidebar.tsx
        effects/
          motion-effect.tsx
          motion-highlight.tsx
        icons/
          blocks.tsx
          components.tsx
          lucide-icons.tsx
          primitives.tsx
        radix/
          switch.tsx
          tabs.tsx
        texts/
          splitting.tsx
      content/
        docs/
          accessibility.mdx
          changelog.mdx
          index.mdx
          i
```

## Agent Configuration

--- CONTRIBUTING.md ---
# Contributing to Animate UI

Thank you for your interest in **contributing to Animate UI**! Your support is highly appreciated, and we look forward to your contributions. This guide will help you understand the project structure and provide detailed instructions for adding a new component to Animate UI.

## Introduction

This repository is a monorepo.

- We use [pnpm](https://pnpm.io) and [workspaces](https://pnpm.io/workspaces) for development.
- We use [Turborepo](https://turbo.build/repo) as our build system.

## Structure

This repository is structured as follows:

```
apps
└── www
    ├── app
    ├── components
    ├── content
    ├── lib
    └── registry
        ├── components
        │   ├── animate (Animate UI Components)
        │   ├── backgrounds
        │   ├── base (Base UI Components)
        │   ├── buttons
        │   ├── community (Community Components)
        │   ├── headless (Headless UI Components)
        │   └── radix (Radix UI Components)
        ├── demo
        │   ├── components
        │   └── primitives
        ├── hooks
        ├── icons
        ├── lib
        └── primitives
            ├── animate (Animate UI Primitives)
            ├── base (Base UI Primitives)
            ├── buttons
            ├── effects
            ├── headless (Headless UI Primitives)
            ├── radix (Radix UI Primitives)
            └── texts
packages
├── eslint-config
├── typescript-config
└── ui (Internal UI components)
```

## Getting Started

### Fork and Clone the Repository

#### 1. Fork the Repository

Click [here](https://github.com/imskyleen/animate-ui/fork) to fork the repository.

#### 2. Clone your Fork to Your Local Machine

```bash
  git clone https://github.com/<YOUR_USERNAME>/animate-ui.git
```

#### 3. Navigate to the Project Directory

```bash
cd animate-ui
```

#### 4. Create a New Branch for Your Changes

```bash
git checkout -b my-branch
```

#### 5. Install Dependencies

```bash
pnpm i
```

#### 6. Run the Project

```bash
pnpm dev


## Analysis Note
> This KI was generated by **enhanced local structural analysis** (no LLM API was available at generation time). It includes full tech stack detection, README parsing, dependency analysis, and feature extraction. For deeper semantic analysis, re-run with an active Gemini or OpenAI API key.
