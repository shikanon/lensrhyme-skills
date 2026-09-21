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

## Canvas operations

`POST /canvas/projects` body `{ "name":"Creative board", "description":"..." }` returns project `id`. `GET /canvas/projects/{id}` includes full `nodes` and `edges`. `PUT` accepts name/description/cover_url/nodes/edges; graph arrays replace current arrays. Template application body is schema-defined; inspect it before mutation.

Single node image task (node must already be in that project):
```json
{"entrypoint":"canvas","context":{"project_id":"PROJECT_ID","node_id":"NODE_ID"},"task_type":"image_generation","name":"Canvas image","payload":{"mode":"text_to_image","prompt":"A ceramic cup in warm light","size":"2K"}}
```
Video uses `task_type: video_generation`, e.g. `payload: {"mode":"text_to_video","prompt":"...","duration":5,"resolution":"720p","ratio":"16:9","async_mode":true}`. Reference image/video task fields follow Studio's wire format but must retain `entrypoint: canvas` and project/node context. For text/audio/3D or playlist tasks, inspect the actual supported contract rather than guessing payloads.

Read `/canvas/projects/{id}/artifacts` and `/generation-records`. If linking is needed, `POST /canvas/nodes/{node_id}/artifacts` with `{ "project_id":"...", "kind":"image", "url":"...", "task_id":"...", "resource_id":"..." }` (omit absent optional values). `PATCH /canvas/artifacts/{artifact_id}` controls artifact state; inspect the schema, then verify readback. Do not fabricate completion by attaching a reference input as generated output.

Reusable workflow: `GET /canvas/workflow-templates`, GET chosen template and `/revisions/{revision_id}`. `POST /canvas/workflow-templates/{template_id}/invocations` body `{ "revision_id":"...", "inputs":{}, "execution_mode":"production", "source":"agent", "idempotency_key":"unique-logical-request-id" }`; populate inputs from the published contract. Follow `/canvas/invocations/{invocation_id}` as declared in the contract. New publication and archive are separate user-visible mutations; do not publish or archive just to execute an existing workflow.

For briefs, exports, packages, bindings and graph trial-runs, inspect the specific bundled schema. `trial` can still execute billable generation; it does not mean free or dry-run.
