---
name: heygen-native-api
description: Native SEOSONA Video skill for interacting directly with HeyGen API v2 (Video, Avatar, Translation) via REST API without relying on external plugins.
---

# SKILL: HeyGen Native API Integration

This skill empowers SEOSONA Video to natively generate Avatar Videos, translate videos, and interact with the HeyGen REST API. This operates entirely through direct HTTP calls (via Node/Python) and uses a custom Agent architecture backed by our internal HeyGen Knowledge Base.

## When to use this skill
- When the user asks to "tạo video avatar", "dịch video sang ngôn ngữ khác bằng AI", or "sử dụng HeyGen API".
- When a video pipeline requires a photorealistic talking head instead of faceless animation.
- When generating video directly from raw text using HeyGen's TTS and Avatars.

## Architecture

This skill defines two specialized sub-agents and a pipeline script:
1. **`heygen-rest-architect`**: An agent that acts as a Payload Designer. It reads the requirements, searches the local `references/` directory for the exact API schema (e.g., `reference_create-video.md`), and outputs a validated JSON payload.
2. **`heygen-pipeline-worker`**: An agent that executes the workflow. It uses `scripts/heygen_client.py` (or Node equivalent) to dispatch the payload, poll for `processing` -> `completed` status, and download the resulting MP4 file to the workspace.

## Required Environment
- `HEYGEN_API_KEY`: Must be defined in the `.env` file of the SEOSONA Video project.

## Execution Flow
1. **Agent Invocation**: The primary orchestrator invokes `heygen-rest-architect` to prepare the API payload.
2. **Validation**: The payload is verified against limits (e.g., credit costs, character counts).
3. **Dispatch & Polling**: The primary orchestrator (or `heygen-pipeline-worker`) runs `scripts/heygen_client.py` with the payload.
4. **Handoff**: The MP4 result is retrieved and passed back to the user or downstream pipelines (like `graphic-overlays`).
