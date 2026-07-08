# KI: swagger-api/swagger-ui

## Overview
[Swagger UI](https://swagger.io/tools/swagger-ui/) allows anyone — be it your development team or your end consumers — to visualize and interact with the API’s resources without having any of the implementation logic in place. It’s automatically generated from your OpenAPI (formerly known as Swagger) Specification, with the visual documentation making it easy for back end implementation and client side consumption.

## Architecture & Tech Stack
- Node.js / TypeScript / JavaScript
- **Total files:** 117 files across 28 directories
- **File types:** .md: 27, .js: 21, .jsx: 18, .yml: 11, .json: 8, .yaml: 4, .sh: 4

## Documentation Sections
- <img src="https://raw.githubusercontent.com/swagger-api/swagger.io/wordpress/images/assets/SWU-logo-clr.png" width="300">
- Introduction
- General
- Compatibility
- Anonymized analytics
- Documentation
- Browser support
- Known Issues
- Security contact
- License

## Core Structure
```
  .agignore
  .browserslistrc
  .commitlintrc.json
  .dockerignore
  .editorconfig
  .eslintignore
  .eslintrc.js
  .gitattributes
  .gitignore
  .lintstagedrc
  .npmignore
  .npmrc
  .nvmrc
  .prettierrc.yaml
  .releaserc
  CLAUDE.md
  Dockerfile
  LICENSE
  NOTICE
  README.md
  SECURITY.md
  babel.config.js
  composer.json
  cypress.config.js
  package-lock.json
  package.json
  snapcraft.yaml
  stylelint.config.js
  .claude/
    SKILL_USAGE_EXAMPLE.md
    skills/
      README.md
      add-oas-support.md
  .github/
    dependabot.yaml
    lock.yml
    pull_request_template.md
    ISSUE_TEMPLATE/
      Bug_report.md
      Feature_request.md
      Support.md
    workflows/
      codeql.yml
      dependabot-merge.yml
      docker-build-push-unstable.yml
      docker-build-push.yml
      docker-image-check.yml
      nodejs.yml
      release-swagger-ui-dist.yml
      release-swagger-ui-packagist.yml
      release-swagger-ui-react.yml
      release-swagger-ui.yml
  .husky/
    commit-msg
    pre-commit
  config/
    .eslintrc
    jest/
      jest.artifact.config.js
      jest.unit.config.js
  dev-helpers/
    dev-helper-initializer.js
    index.html
    oauth2-redirect.html
    oauth2-redirect.js
    style.css
  docker/
    cors.conf
    default.conf.template
    embedding.conf
    configurator/
      helpers.js
      index.js
      oauth.js
      translator.js
      variables.js
    docker-entrypoint.d/
      40-swagger-ui.sh
  docs/
    README.md
    book.json
    customization/
      add-plugin.md
      custom-layout.md
      overview.md
      plug-points.md
      plugin-api.md
    development/
      scripts.md
      setting-up.md
    images/
      swagger-ui2.png
      swagger-ui3.png
    samples/
      webpack-getting-started/
        README.md
        _sample_package.json
        index.html
        webpack.config.js
        src/
          index.js
          swagger-config.yaml
    usage/
      configuration.md
      cors.md
      deep-linking.md
      installation.md
      limitations.md
      oauth2.md
      version-detection.md
  flavors/
    swagger-ui-react/
      README.md
      index.jsx
      release/
        create-manifest.js
        run.sh
        template.json
  release/
    .release-it.json
    check-for-breaking-changes.sh
    get-changelog.sh
  src/
    .eslintrc
    index.js
    core/
      index.js
      oauth2-authorize.js
      system.js
      window.js
      assets/
        rolling-load.svg
      components/
        app.jsx
        cle
```

## Quick Start
```bash
{
"scarfSettings": {
"enabled": false
}
}
```

## Agent Configuration

--- CLAUDE.md ---
# CLAUDE.md - Swagger UI Codebase Guide

> **Last Updated:** 2026-02-24
> **Version:** 5.32.0 (in development)
> **Purpose:** Comprehensive guide for AI assistants working with the Swagger UI codebase

---

## Table of Contents

1. [Repository Overview](#repository-overview)
2. [Project Architecture](#project-architecture)
3. [Development Setup](#development-setup)
4. [Build System](#build-system)
5. [Testing Infrastructure](#testing-infrastructure)
6. [Code Style & Conventions](#code-style--conventions)
7. [Git Workflow](#git-workflow)
8. [Plugin Architecture](#plugin-architecture)
9. [Key Files & Directories](#key-files--directories)
10. [Common Workflows](#common-workflows)
11. [Important Guidelines](#important-guidelines)

---

## Repository Overview

### What is Swagger UI?

Swagger UI is a tool that allows developers to visualize and interact with API resources without having implementation logic in place. It's automatically generated from OpenAPI (formerly Swagger) Specification documents.

### Multi-Package Monorepo Structure

This repository publishes **three different npm packages**:

1. **swagger-ui** (main package)
   - Traditional npm module for single-page applications
   - Entry: `dist/swagger-ui.js`
   - ES Module: `dist/swagger-ui-es-bundle-core.js`
   - Includes dependency resolution via Webpack/Browserify

2. **swagger-ui-dist** (distribution package)
   - Dependency-free module for server-side projects
   - Published separately via GitHub workflow
   - Template location: `swagger-ui-dist-package/`

3. **swagger-ui-react** (React component)
   - React wrapper component
   - Location: `flavors/swagger-ui-react/`
   - Uses React hooks
   - Released separately via GitHub workflow

### OpenAPI Specification Compatibility

- **Current Support:** OpenAPI 2.0, 3.0.x, 3.1.x
- **Latest Version:** v5.31.0 (supports up to OpenAPI 3.1.2)

### License

Apache 2.0 - See LICENSE and NOTICE files for details.

---

## Project Architecture

### Technology Stack

*


## Analysis Note
> This KI was generated by **enhanced local structural analysis** (no LLM API was available at generation time). It includes full tech stack detection, README parsing, dependency analysis, and feature extraction. For deeper semantic analysis, re-run with an active Gemini or OpenAI API key.
