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

## Video requests

```json
{"entrypoint":"studio","task_type":"video_generation","name":"Product clip","payload":{"mode":"text_to_video","prompt":"A ceramic cup on a desk, gentle camera push-in, warm morning light","duration":5,"resolution":"720p","ratio":"16:9","async_mode":true}}
```
Modes (exact wire values):
- `text_to_video`: `prompt`.
- `image_to_video_first_frame`: `prompt`, `first_frame` URL/reference.
- `image_to_video_first_last_frame`: `prompt`, `first_frame`, `last_frame`.
- `free`: `content` array. Text entry `{ "type":"text", "text":"..." }`; image entry `{ "type":"image_url", "image_url":{"url":"https://..."}, "role":"reference_image" }`; video/audio entries use `video_url`/`audio_url` with `reference_video`/`reference_audio` respectively.

All modes may include model, duration, ratio, resolution, async_mode. Optional audio/watermark parameters must be supported by the chosen model. Reference roles are not interchangeable with first/last frame. Model capability constraints override example dimensions/durations.

`POST /video/generation` accepts the same mode fields directly and returns `task_id` for async or `video_url` for sync. `/video/text_to_video` is the text-only convenience endpoint. Prefer `/tasks/` for Studio history. `/video/optimize-prompt` is an optional model-backed rewrite, not video generation; inspect its schema and preserve the user's content before using it.

## Executable default

The default is `doubao-seedance-2-0-fast-260128`. Use `python3 scripts/lensrhyme_api.py studio video --json-file payload.json --out submitted.json` where the file contains only the generation payload (not a task envelope). The equivalent `request POST /tasks/` applies defaults only for `entrypoint: studio`. Explicit models remain unchanged; display aliases for the configured image/video model resolve to their exact API IDs. Direct synchronous API calls must specify the model themselves.
