---
name: lensrhyme-studio-audio
description: "Generate standalone audio, narration and voiceovers in LensRhyme Studio with Seed Audio and optional references. Use for independent audio deliverables; not ASR, music composition, native video sound, Canvas node or Workbench project-bound generation."
---

# LensRhyme Studio Audio

## Routing

Use for standalone LensRhyme Studio narration, voiceovers, spoken dialogue and generative audio with text, speaker, audio or image references. Example: “用 Seed Audio 生成这段中文旁白”. Keep a specified Canvas node or Workbench project/shot under its owning skill. Standalone images use `lensrhyme-studio-image`; video clips use `lensrhyme-studio-video`. Video with native sound remains a video request unless the user separately asks for an audio file. Transcription/ASR is recognition, not generation; music composition uses the separate music workflow, not this audio task payload.

## Default model and workflow

1. Unless the user explicitly selects another compatible audio model, use `seed-audio-1.0`. Read [API guide](references/api.md) for its nested `seed_audio` payload. Do not use legacy top-level `text`/`voice_id` parameters with Seed Audio.
2. Prepare the exact spoken text and optional direction/references. Preserve the user's script. Check reference count/type, input duration and output encoding constraints before submitting.
3. Run `studio audio --json-file payload.json --out submitted.json` using the bundled script. It creates `entrypoint: studio`, `task_type: audio_generation` and fills the default model. Explicit compatible models are preserved; missing model access or billing errors do not authorize fallback.
4. Save the task ID, poll `/tasks/{id}`, and resolve the returned resource to a downloadable audio URL. Verify media format, nonzero duration and audible content before claiming delivery. Report available subtitles/timestamps only if returned.
5. Existing Canvas/Workbench projects own their audio bindings. Do not label an independent Studio audio task as a project-bound result.

## Authentication and execution

Read [API guide](references/api.md) before calling the service. Use the user's API management Token Key through `LENSRHYME_API_KEY`; all operations use `Authorization: Bearer ltr_...`. Default API base is `https://lensrhyme.com/api/v1`, not the `/team` web page. Keep credentials out of prompts, command arguments, output, and Git. Do not rotate an existing key to solve a request failure. Honor the selected Workspace with `LENSRHYME_WORKSPACE_ID`.

Run `python3 <this-skill>/scripts/lensrhyme_api.py ...`; resolve `<this-skill>` from this installed SKILL.md location. Each skill is self-contained. Python 3.10+ and network access are required; no pip packages or application checkout are needed.

Before generation, inspect `/models/list` and `/models/parameters?modality=...&model=...` using the actual parameter names in the contract. Respect the requested model and verify its supported mode, references, dimensions, duration and account access. Use the smallest number of calls that fulfills the request. Do not substitute a model or repeat a paid request after a timeout without checking existing tasks. Persist each returned task ID immediately and poll it; a queued task is not a completed output. Inspect `status`, `error_code`, `error_message`, `result_url`, and `output`. Report task failure or pending state honestly; when completed, return the media URL and relevant project/task IDs. Fetch media without the API Authorization header and verify it is readable before claiming delivery.

For a parameter or endpoint not shown in the guide, run `schema /api/v1/... --method POST` to inspect the bundled production contract. The contract is a dated snapshot, not permission or proof of live availability. For changes after that date, fetch `/openapi.json` using the client and inspect the specific endpoint. Read only the relevant schemas. Never invent fields in the opaque task `payload`.
