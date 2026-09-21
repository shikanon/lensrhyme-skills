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

## Image requests

Studio text-to-image body:
```json
{"entrypoint":"studio","task_type":"image_generation","name":"Character poster","payload":{"mode":"text_to_image","prompt":"A friendly original character in a quiet sunlit room","size":"2K","ratio":"1:1"}}
```
Reference editing: change `payload.mode` to `image_to_image` and add `image_urls: ["https://..."]`. Choose `size`/`ratio` from live model parameters; omit `model` only when accepting the user's configured default. Prompt, reference fidelity and count are part of user intent. Do not use a video endpoint for a still image.

Dedicated synchronous endpoints: `/image/text_generation` (prompt, model?, size?); `/image/image_generation` (prompt, image_urls, model?, size?); `/image/character_design` (prompt, image_urls?, model?, size?, preset?); `/image/scene_topdown` (prompt, image_urls?, model?, size?). They return `{ "url": "..." }` and can charge immediately. Character presets are schema-defined. Do not pass Studio-only `ratio` or `entrypoint` to these request bodies.
