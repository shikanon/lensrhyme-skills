---
name: lensrhyme-workbench
description: "Manage LensRhyme Workbench production projects: scripts, episodes, acts, scenes, shots/storyboards, consistent assets, shot generation, versions and timeline export. Use for project-bound structured production; standalone Studio clips/images and Canvas node graphs are excluded."
---

# LensRhyme Workbench

## Routing

Use when the deliverable belongs to a structured production project, episode, act, scene, shot/storyboard, asset library or timeline. Example: “导入这个剧本，按场景拆分镜头并生成第一个镜头”. An existing Workbench project/shot ID takes priority over image/video modality. Canvas owns node graphs and reusable visual workflows; Studio owns independent media generation. Never create a second project or standalone Studio task to sidestep a failed project generation.

## Workflow

1. List/select or create the intended `/workbench/projects` project. Read project settings, assets and relevant script structure; preserve aspect ratio, style and existing IDs. Respect owner/editor/viewer permissions.
2. Import a user-provided script through the multipart script endpoint, then follow its task to completion before reading the resulting structure. For manual structure, create episode (if needed), act, scene, then shot using returned parent IDs. Do not replace a populated structure with an empty parse.
3. Resolve characters/scenes and bind actual resource IDs to assets/shot references. Read existing versions and model settings. Use native shot/storyboard preflight and generation endpoints so continuity, billing and project results remain connected. Do not route project generation through standalone Studio tasks.
4. Poll the returned task using the declared module/global task ID mapping. Re-read the shot/storyboard versions and verify its output URL; global task completion alone does not prove project writeback.
5. Read the entire timeline before updating its tracks/items/transitions. Export only after checking source media and timings, then follow the export task and verify the downloadable result. Preserve the user's cut and existing tracks.

Keep single-shot generation scoped; batch operations affect all selected/project shots and can multiply cost. Use batch generation only for the requested scope. Storyboard endpoints and legacy shot endpoints have distinct schemas and IDs; do not interchange them merely because the UI calls both “镜头”.

## Authentication and execution

Read [API guide](references/api.md) before calling the service. Use the user's API management Token Key through `LENSRHYME_API_KEY`; all operations use `Authorization: Bearer ltr_...`. Default API base is `https://lensrhyme.com/api/v1`, not the `/team` web page. Keep credentials out of prompts, command arguments, output, and Git. Do not rotate an existing key to solve a request failure. Honor the selected Workspace with `LENSRHYME_WORKSPACE_ID`.

Run `python3 <this-skill>/scripts/lensrhyme_api.py ...`; resolve `<this-skill>` from this installed SKILL.md location. Each skill is self-contained. Python 3.10+ and network access are required; no pip packages or application checkout are needed.

Before generation, inspect `/models/list` and `/models/parameters?modality=...&model=...` using the actual parameter names in the contract. Respect the requested model and verify its supported mode, references, dimensions, duration and account access. Use the smallest number of calls that fulfills the request. Do not substitute a model or repeat a paid request after a timeout without checking existing tasks. Persist each returned task ID immediately and poll it; a queued task is not a completed output. Inspect `status`, `error_code`, `error_message`, `result_url`, and `output`. Report task failure or pending state honestly; when completed, return the media URL and relevant project/task IDs. Fetch media without the API Authorization header and verify it is readable before claiming delivery.

For a parameter or endpoint not shown in the guide, run `schema /api/v1/... --method POST` to inspect the bundled production contract. The contract is a dated snapshot, not permission or proof of live availability. For changes after that date, fetch `/openapi.json` using the client and inspect the specific endpoint. Read only the relevant schemas. Never invent fields in the opaque task `payload`.
