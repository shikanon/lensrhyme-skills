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

## Audio requests

Default model: `seed-audio-1.0`. The normal route is `POST /tasks/`, `entrypoint: studio`, `task_type: audio_generation`. The legacy synchronous `/audio/generation` schema is a different TTS surface; it does not accept this nested Seed Audio request. Do not send this body there.

`payload.json` (the `studio audio` command fills the model):
```json
{"seed_audio":{"kind":"seed_audio","text":"你好，欢迎来到灵韵创作空间。","text_prompt":"用自然、温暖、清晰的普通话朗读。","references":[],"audio_config":{"format":"wav","sample_rate":24000,"enable_subtitle":true}}}
```
```bash
python3 scripts/lensrhyme_api.py studio audio --json-file payload.json --out submitted.json
python3 scripts/lensrhyme_api.py wait TASK_ID --seconds 300 --out completed.json
```

This nested payload follows the Studio audio draft serializer and server Seed Audio DTO; task OpenAPI exposes `payload` as an opaque object. Do not infer Seed Audio fields from that generic object schema.

- `seed_audio.text`: required, nonempty spoken text. `text_prompt`: optional direction. Combined direction, text references and text must not exceed 3000 characters, including separator newlines.
- `references`: text `{ "kind":"text", "text":"..." }`; speaker `{ "kind":"speaker", "speaker":"supported speaker id" }`; audio `{ "kind":"audio", "resource_id":"..." }` or `{ "kind":"audio", "url":"https://..." }`; image uses `kind: image` with the same resource-or-URL source. A resource can include `resource_version_id`. Supply exactly one resource or URL per media reference, never a local path or inline base64. Discover speaker IDs rather than inventing them.
- Maximum three combined speaker/audio references OR one image reference; do not mix speaker/audio and image references. Media limits: 10 MB; audio up to 30 seconds. Images: JPEG/PNG/WebP. Audio: WAV/MP3/PCM/OGG Opus; PCM needs its actual sample rate.
- `audio_config.format`: wav, mp3, pcm or ogg_opus. `sample_rate`: 8000/16000/24000/32000/44100/48000. `speech_rate` and `loudness_rate`: -50..100; `pitch_rate`: -12..12; `enable_subtitle`: boolean. Defaults are WAV, 24000 Hz, zero rate adjustments and subtitles off.
- Maximum model output duration is 120 seconds; do not fabricate an unsupported `duration` parameter to force length. Split a longer script only within the user's intended generation scope.
- Optional `watermark`: `enabled`, `metadata_enabled`, and documented provenance fields. Do not pass frontend-only draft fields to the API.

The user supplies a LensRhyme Token Key, not a provider credential. If production reports a missing provider audio key or HTTP 402, report that exact blocker and preserve the task ID; do not request an unrelated API key or replace the model.
