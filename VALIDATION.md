# Validation — 2026-09-21

## Local checks

- `python3 -m unittest discover -s tests -v`: 10 passed. Checks Bearer/Workspace headers, JSON serialization, URL boundaries, redirect refusal, no mutation retry, polling completion/failure/timeout, multipart upload and independent package contents.
- `python3 scripts/validate_skills.py`: four packages passed metadata and relative-reference checks.
- Bundled `skill-creator/scripts/quick_validate.py` was attempted but could not run because the available Python runtimes lack PyYAML. The dependency-free repository validator was used instead; no environment packages were installed.
- Credential scan: no live API key, login token or test password in the published files.

## Public installation and CI

- Codex bundled `skill-installer/scripts/install-skill-from-github.py --repo shikanon/lensrhyme-skills --path skills/lensrhyme-studio-image skills/lensrhyme-studio-video skills/lensrhyme-canvas skills/lensrhyme-workbench --dest /tmp/lensrhyme-installed-skills`: all four installed from public GitHub.
- Each installed client ran `request GET` against its models/project endpoint with the production API key; all four passed. Each installed `schema /api/v1/tasks/` command also passed without application source dependencies.
- [Initial GitHub Actions validation](https://github.com/shikanon/lensrhyme-skills/actions/runs/35584016450): passed on commit `6c4281c`.
- Delivery requirement: [issue #1](https://github.com/shikanon/lensrhyme-skills/issues/1).

## Production API tests

Host: `https://lensrhyme.com/api/v1`. Account: the designated test account. Authentication for creative operations used its API management Token Key, not its login JWT. Test credentials and full response artifacts remain outside this public repository.

| Module | Evidence | Result |
| --- | --- | --- |
| Shared | Login, obtain/create missing API key, list Workspace and models | Passed |
| Studio Image | Submit real image task, wait for completed status, resolve resource to download URL, fetch PNG | Passed; HTTP 200, image/png, 768433 bytes; provider diagnostics report mocked=false |
| Studio Video | First catalog model reached a definitive provider error; an explicit second test used `doubao-seedance-2-0-fast-260128`, 4 seconds / 720p / 16:9 | Second task completed; HTTP 200 video/mp4, 867257 bytes, MP4 movie header reports 4.096 seconds for the requested 4-second clip; provider diagnostics report mocked=false. First model `doubao-seedance-1-0-pro-fast-251015` was rejected upstream as unknown; this was not silently treated as a success |
| Canvas | Create project, save image node, read back, generate real image task, create node artifact and query artifact list | Passed; task completed and one generated artifact linked to the original node |
| Workbench | Create project, act, scene and shot, read back parent associations | Passed |
| Workbench generation | Request native shot generation | HTTP 402; billing prevents end-to-end generation verification |

Testing did not change account balance, pricing, model configuration, IP allowlists or deployment. A previously absent test-account Token Key was created; no existing key was rotated. Test projects and their generation evidence were retained for inspection. The application working tree was not modified.

## Limits

These checks do not establish every model/mode, reference-image editing, script import, published Canvas workflow execution, multi-user graph concurrency, Workbench video writeback or timeline rendering. No browser UI regression suite or application build was run because the change is a separate skill repository. Model availability and billing remain deployment/account dependent; a successful skill install does not guarantee that a model can generate.

## Studio audio and executable defaults — follow-up (2026-09-21)

Requirement: [issue #2](https://github.com/shikanon/lensrhyme-skills/issues/2). A fifth skill, `lensrhyme-studio-audio`, now covers independent Studio audio generation. Default model selection executes in the shared client for Studio media tasks; explicit overrides and Canvas/Workbench requests remain unchanged. No production account default settings were modified.

Each real test used the designated `test_user` account's existing API management key. Input payload JSON intentionally omitted `model`. The CLI's `studio` command populated the model before submission; saved task payloads confirmed the intended model IDs. One task per modality was submitted, with no model fallback or generation retry.

| Skill | Default API ID confirmed in task | Production result |
| --- | --- | --- |
| Studio Audio | `seed-audio-1.0` | Completed; HTTP 200 WAV, 652844 bytes, 6.8 seconds, 24000 Hz, stereo, 16-bit PCM. RMS 2637.78 (non-silent); two subtitle segments match the requested narration. Provider reports volcengine with api_key authentication. |
| Studio Image | `doubao-seedream-5-0-pro-260628` | Completed; HTTP 200, 367673 bytes, decoded JPEG 2048×2048; visual inspection confirms the requested blue cup product image. Provider diagnostics: provider_called=true, mocked=false. |
| Studio Video | `doubao-seedance-2-0-fast-260128` | Completed; HTTP 200 MP4, 926427 bytes; movie header reports 4.096 seconds for the requested 4-second clip. Provider diagnostics confirm the configured model, provider_called=true and mocked=false. |

Image download response was labeled `image/png`, but file signature and decoder identify JPEG. The local artifact was saved as `.jpg`; media validation uses actual encoding rather than trusting the response header. Audio validation used WAV structure, non-silent samples and returned subtitles; no human listening study or separate ASR accuracy test was performed. Video validation checked task/provider status and the downloadable MP4 structure/duration, not every frame's creative quality.

Commands used for the live submissions (from each installed-format skill folder, with credentials only in the environment):

```bash
python3 scripts/lensrhyme_api.py studio audio --json-file audio-payload.json --name 'Default model acceptance audio' --out audio-submitted.json
python3 scripts/lensrhyme_api.py studio image --json-file image-payload.json --name 'Default model acceptance image' --out image-submitted.json
python3 scripts/lensrhyme_api.py studio video --json-file video-payload.json --name 'Default model acceptance video' --out video-submitted.json
```

The subsequent test runner read `/tasks/{id}`, resolved `/resources/{resource_id}/download-url`, downloaded without API credentials, and inspected binary headers, audio samples and subtitles. Full responses and generated files are in the ignored local `artifacts/default-model-test/` directory, not in this public repository. Existing test-account keys were reused and were not rotated.

Local checks: `python3 -m unittest discover -s tests -v` — 18 passed; `python3 scripts/validate_skills.py` — all five skills passed; `git diff --check` — passed; credential scan — passed. Tests cover actual serialized defaults, CLI behavior, aliases, overrides, project isolation, wrong Seed Audio payload rejection and nested model conflicts. The previously documented PyYAML limitation still applies to the external quick validator. No application build, deployment, or browser UI regression test was needed for this skill-only change.

Public installation was re-tested with Codex's bundled installer:

```bash
python3 /path/to/skill-installer/scripts/install-skill-from-github.py --repo shikanon/lensrhyme-skills --path skills/lensrhyme-studio-audio skills/lensrhyme-studio-image skills/lensrhyme-studio-video --dest /tmp/lr-default-model-installed
```

All three installed. Each installed package passed its default selection check, bundled `schema /api/v1/tasks/` command and `wait TASK_ID --seconds 0` read of its completed production test. No extra generation was issued for the installation check. [Implementation CI](https://github.com/shikanon/lensrhyme-skills/actions/runs/35588468026) passed on `9491f2a`.
