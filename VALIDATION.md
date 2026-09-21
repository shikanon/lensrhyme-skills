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
