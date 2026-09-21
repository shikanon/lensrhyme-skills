---
name: lensrhyme-canvas
description: "Create and operate LensRhyme Canvas node graphs, node-bound generation and artifacts, reusable workflow templates and invocations. Use when a canvas, node, graph dependency or reusable visual workflow is the target; standalone media and structured Workbench episodes/shots are excluded."
---

# LensRhyme Canvas

## Routing

Use for visual node graphs, linked text/image/video/audio steps, reusable workflows, node outputs and project delivery packages. Example: “在画布里连接角色图和视频节点，并生成这个节点”. A Canvas project/node ID takes priority over media type. For standalone media use the Studio image/video skill; for script/episode/act/scene/shot production and timelines use Workbench. If a request explicitly crosses modules, keep one owner per phase and pass only verified resource IDs/URLs to the next phase.

## Workflow

1. List `/canvas/projects`; select the intended project or create one. GET its full detail before editing. Preserve all unrelated node IDs, positions, data, edges and resource bindings; PUT graph arrays are whole replacements. Re-read before saving and stop/reconcile concurrent changes rather than overwrite another editor. Do not clear a graph implicitly.
2. For a new graph, use `/canvas/templates` and `apply-template`, or construct documented node data. For a single node generation, use the Canvas task context in the guide, not a Studio task. Confirm that project and node exist first.
3. Persist the task ID and poll. Query project artifacts and generation records; if no artifact was linked, create one for the original node with the returned resource/task ID. Do not invent a resource ID. Select an output only when the user requested it and the artifact is valid; read back the project/artifact association.
4. For reusable server execution, inspect the workflow template's published revision and input contract, then invoke that revision. Keep revision and idempotency key stable across recovery. Inspect invocation detail and its run/task state; HTTP 201 alone is not completion.
5. Export only when requested. An exported manifest/package is not necessarily a rendered video; return the actual output type.

The durable `/runs` API has a manifest contract and scheduling modes. Default `shadow` is not proof of autonomous execution. Do not claim a graph ran from a bare `selected_node_ids` request. Prefer a published template invocation for headless graph execution; use raw runs only after reading the manifest and revision contract in the production API and obtaining a valid execution package from the supported Canvas workflow.

## Authentication and execution

Read [API guide](references/api.md) before calling the service. Use the user's API management Token Key through `LENSRHYME_API_KEY`; all operations use `Authorization: Bearer ltr_...`. Default API base is `https://lensrhyme.com/api/v1`, not the `/team` web page. Keep credentials out of prompts, command arguments, output, and Git. Do not rotate an existing key to solve a request failure. Honor the selected Workspace with `LENSRHYME_WORKSPACE_ID`.

Run `python3 <this-skill>/scripts/lensrhyme_api.py ...`; resolve `<this-skill>` from this installed SKILL.md location. Each skill is self-contained. Python 3.10+ and network access are required; no pip packages or application checkout are needed.

Before generation, inspect `/models/list` and `/models/parameters?modality=...&model=...` using the actual parameter names in the contract. Respect the requested model and verify its supported mode, references, dimensions, duration and account access. Use the smallest number of calls that fulfills the request. Do not substitute a model or repeat a paid request after a timeout without checking existing tasks. Persist each returned task ID immediately and poll it; a queued task is not a completed output. Inspect `status`, `error_code`, `error_message`, `result_url`, and `output`. Report task failure or pending state honestly; when completed, return the media URL and relevant project/task IDs. Fetch media without the API Authorization header and verify it is readable before claiming delivery.

For a parameter or endpoint not shown in the guide, run `schema /api/v1/... --method POST` to inspect the bundled production contract. The contract is a dated snapshot, not permission or proof of live availability. For changes after that date, fetch `/openapi.json` using the client and inspect the specific endpoint. Read only the relevant schemas. Never invent fields in the opaque task `payload`.
