---
name: lensrhyme-studio-image
description: "Generate or edit standalone images in LensRhyme Studio: text-to-image, reference image variations, character sheets and scene top views. Use for image deliverables without a Canvas node or Workbench shot target; project-bound generation belongs to that project skill."
---

# LensRhyme Studio Image

## Routing

Use for standalone posters, illustrations, character references, product images, or image edits requested in LensRhyme Studio. Example: “在 Studio 用这张参考图生成三张角色海报”. Video output uses `lensrhyme-studio-video`. A specified Canvas node or Workbench asset/storyboard stays under `lensrhyme-canvas` or `lensrhyme-workbench`, even if the result is an image. Do not create a project just to generate a standalone image.

## Default model

Use `doubao-seedream-5-0-pro-260628` unless the user explicitly chooses another compatible model. The bundled client fills this default for Studio tasks when `payload.model` is absent, null or blank. Preserve explicit overrides and never fall back on a provider/billing failure. For direct synchronous endpoints, supply this model explicitly. These skill defaults do not change account settings or Canvas/Workbench models.

## Workflow

1. Resolve prompt, references, model and output dimensions; upload local inputs when needed.
2. Submit `POST /tasks/` with `entrypoint: "studio"`, `task_type: "image_generation"` and a supported image payload from the API guide. This is the normal Studio path, preserving task history. For batches, create only the requested count and record every returned ID.
3. Poll `/tasks/{id}`, verify the returned image and report its URL. Editing means model generation; when the user requires exact pixel preservation, use an appropriate local pixel tool instead of claiming this model path preserves pixels.
4. For specialized character sheets/top views, use the dedicated synchronous image endpoint documented in the guide when requested; label the resulting image and note that this path returns `url` directly rather than a Studio task.

## Authentication and execution

Read [API guide](references/api.md) before calling the service. Use the user's API management Token Key through `LENSRHYME_API_KEY`; all operations use `Authorization: Bearer ltr_...`. Default API base is `https://lensrhyme.com/api/v1`, not the `/team` web page. Keep credentials out of prompts, command arguments, output, and Git. Do not rotate an existing key to solve a request failure. Honor the selected Workspace with `LENSRHYME_WORKSPACE_ID`.

Run `python3 <this-skill>/scripts/lensrhyme_api.py ...`; resolve `<this-skill>` from this installed SKILL.md location. Each skill is self-contained. Python 3.10+ and network access are required; no pip packages or application checkout are needed.

Before generation, inspect `/models/list` and `/models/parameters?modality=...&model=...` using the actual parameter names in the contract. Respect the requested model and verify its supported mode, references, dimensions, duration and account access. Use the smallest number of calls that fulfills the request. Do not substitute a model or repeat a paid request after a timeout without checking existing tasks. Persist each returned task ID immediately and poll it; a queued task is not a completed output. Inspect `status`, `error_code`, `error_message`, `result_url`, and `output`. Report task failure or pending state honestly; when completed, return the media URL and relevant project/task IDs. Fetch media without the API Authorization header and verify it is readable before claiming delivery.

For a parameter or endpoint not shown in the guide, run `schema /api/v1/... --method POST` to inspect the bundled production contract. The contract is a dated snapshot, not permission or proof of live availability. For changes after that date, fetch `/openapi.json` using the client and inspect the specific endpoint. Read only the relevant schemas. Never invent fields in the opaque task `payload`.
