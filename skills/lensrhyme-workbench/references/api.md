# API usage

Contract snapshot: production `https://lensrhyme.com/api/v1/openapi.json`, 2026-09-21. `api-contract.json` includes only this skill's API surface and recursively referenced schemas. Studio payload details also follow the current application hooks. Models and access can change; query them live.

## Credentials and Workspace

Get your own Token Key from [API management](https://lensrhyme.com/api-management) (the [team page](https://lensrhyme.com/team) is the team entry). Supply it via the process environment or a secret manager as `LENSRHYME_API_KEY`. Do not paste it into the conversation. The client intentionally has no `--api-key` flag. `LENSRHYME_BASE_URL` optionally selects another HTTPS deployment, ending in `/api/v1`; only change this when the user intends that destination. List `/workspaces/`, then set `LENSRHYME_WORKSPACE_ID` to the intended accessible workspace. Never silently switch workspaces on a 403.

```bash
python3 scripts/lensrhyme_api.py request GET /workspaces/
python3 scripts/lensrhyme_api.py request GET /models/list
python3 scripts/lensrhyme_api.py schema /api/v1/models/parameters --method GET
python3 scripts/lensrhyme_api.py upload /absolute/path/reference.png --out upload.json
python3 scripts/lensrhyme_api.py request POST /tasks/ --json-file request.json --out submitted.json
python3 scripts/lensrhyme_api.py wait TASK_ID --seconds 300 --out finished.json
```

Paths above assume the skill directory as cwd. Task creation returns `id`; some module operations return `task_id` or a module-specific wrapper. Inspect the schema before choosing a polling endpoint. `--out` creates a private file and refuses to overwrite existing evidence; use a new filename per response. Poll timeout exits 2 and preserves the ID; continue polling the same task. Failed/canceled tasks also exit 2. The helper never retries mutations or follows redirects with credentials. Use exact trailing slashes, especially `/tasks/`, `/upload/`, `/workspaces/`, and `/workbench/projects` as declared by the live contract.

`upload` supports multipart `file`, plus `--fields-file fields.json` for endpoint-specific form fields; it can target a module upload with `--path`. Keep raw binaries out of JSON. Use the returned resource identifier or accessible URL accepted by the target field, not a local filesystem path. Respect per-model reference limits.

Completed tasks may return `resource:...` locators instead of HTTP URLs. Keep the resource identity for project bindings. To deliver media, resolve the locator with `POST /resource-locators/resolve` body `{ "locator":"resource:...", "usage_context":"skill_output", "expected_schema":2 }` if needed, then request `GET /resources/{resource_id}/download-url`. Inspect its response and use the returned download URL without attaching the API key. A `resource:` string is not a browser-playable URL. Preserve resource version IDs when supplied. Signed download URLs may expire.

401: missing/expired/revoked key. 402: insufficient credit or billing restriction; stop generation and report it, do not recharge or downgrade automatically. 403: user/Workspace/model/IP restrictions. 409: stale project or contract; re-read state before changing it. 422: inspect exact schema and capability constraints. 429: wait before another read; check task creation state before repeating a mutation. 5xx/network timeout: unknown outcome, reconcile existing tasks first. Never regenerate credentials, remove IP allowlists, change roles, or recharge as an automatic workaround.

## Workbench operations

Create project: `POST /workbench/projects` with `{ "name":"Short film", "aspect_ratio":"16:9" }`. Read the returned ID and settings.

Manual structure: `POST /workbench/projects/{p}/acts` with `{ "name":"Act 1" }`; `/scenes` with `{ "name":"Interior", "act_id":"ACT_ID" }`; `/shots` with `{ "name":"Opening", "act_id":"ACT_ID", "scene_id":"SCENE_ID", "duration":5, "video_prompt":"A ceramic cup on a desk, slow push-in" }`. Use returned IDs, not names, for relationships.

Script import: `upload /absolute/script.docx --path /workbench/projects/PROJECT_ID/script/import --out import.json`; read schema for optional form fields and actual task response. Use production file formats supported by this endpoint.

Read a shot, its `/versions` and `/assets`. `POST /workbench/projects/{p}/shots/{s}/generate` accepts `{ "prompt":"...", "reference_mode":"auto" }`; preflight may require `preflight_fingerprint` and trusted references. Inspect the corresponding preflight endpoint and response before submission. Never set `prompt_only` or discard references automatically to bypass a preflight failure. Existing active tasks should be followed instead of creating duplicates.

New storyboard workflows have `/storyboards/...` endpoints for planning, images, videos, bindings and versions. Inspect their schemas explicitly; payloads and preflight fingerprints differ from legacy shots. Use `/workbench/projects/{p}/tasks` to resolve the project task to its `real_task_id` when necessary, then `/tasks/{real_task_id}`. Re-read the project output after completion.

Timeline: `GET /workbench/projects/{p}/timeline`; `PUT` replaces the supplied track/item/transition arrays. Keep the existing IDs and timings. `POST /workbench/projects/{p}/timeline/export` creates an asynchronous export. Asset upload: multipart `/workbench/projects/{p}/assets/upload`. Reuse existing project resources rather than reuploading duplicates.
