---
name: lensrhyme-studio-video
description: "Generate standalone video clips in LensRhyme Studio from text, a first frame, first and last frames, or mixed media references. Use for independent video deliverables; Canvas node workflows and Workbench shot/project production belong to their project skills."
---

# LensRhyme Studio Video

## Routing

Use for independent clips in LensRhyme Studio. Example: “把这张产品图做成 5 秒展示视频”. For a still image use `lensrhyme-studio-image`. When a Canvas node, Workbench shot, episode or project is the destination, use its owning skill; do not create a standalone clip and lose the project association. A long story with episodes, cast continuity and a timeline belongs to Workbench; a reusable dependency graph belongs to Canvas.

## Default model

Use `doubao-seedance-2-0-fast-260128` unless the user explicitly chooses another compatible model. The bundled client fills this default for Studio tasks when `payload.model` is absent, null or blank. Preserve explicit overrides and never fall back on a provider/billing failure. For direct synchronous endpoints, supply this model explicitly. These skill defaults do not change account settings or Canvas/Workbench models.

## Workflow

1. Resolve duration, aspect ratio, model, prompt and references. Match the exact video mode to the available inputs.
2. Submit `POST /tasks/` with `entrypoint: "studio"`, `task_type: "video_generation"` and the payload in the guide; set `async_mode: true`.
3. Save `id`, poll `/tasks/{id}`, then verify the returned video URL and requested duration. Never treat a cover image or `task_id` as the final video.
4. Return the task ID, model, chosen settings, video and optional cover URL. If stalled or failed, preserve evidence and do not silently create a replacement job.

## Authentication and execution

Read [API guide](references/api.md) before calling the service. Use the user's API management Token Key through `LENSRHYME_API_KEY`; all operations use `Authorization: Bearer ltr_...`. Default API base is `https://lensrhyme.com/api/v1`, not the `/team` web page. Keep credentials out of prompts, command arguments, output, and Git. Do not rotate an existing key to solve a request failure. Honor the selected Workspace with `LENSRHYME_WORKSPACE_ID`.

Run `python3 <this-skill>/scripts/lensrhyme_api.py ...`; resolve `<this-skill>` from this installed SKILL.md location. Each skill is self-contained. Python 3.10+ and network access are required; no pip packages or application checkout are needed.

Before generation, inspect `/models/list` and `/models/parameters?modality=...&model=...` using the actual parameter names in the contract. Respect the requested model and verify its supported mode, references, dimensions, duration and account access. Use the smallest number of calls that fulfills the request. Do not substitute a model or repeat a paid request after a timeout without checking existing tasks. Persist each returned task ID immediately and poll it; a queued task is not a completed output. Inspect `status`, `error_code`, `error_message`, `result_url`, and `output`. Report task failure or pending state honestly; when completed, return the media URL and relevant project/task IDs. Fetch media without the API Authorization header and verify it is readable before claiming delivery.

For a parameter or endpoint not shown in the guide, run `schema /api/v1/... --method POST` to inspect the bundled production contract. The contract is a dated snapshot, not permission or proof of live availability. For changes after that date, fetch `/openapi.json` using the client and inspect the specific endpoint. Read only the relevant schemas. Never invent fields in the opaque task `payload`.
