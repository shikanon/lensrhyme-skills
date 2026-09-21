# Validation — 2026-09-21

## Local checks

- `python3 -m unittest discover -s tests -v`: 10 passed. Checks Bearer/Workspace headers, JSON serialization, URL boundaries, redirect refusal, no mutation retry, polling completion/failure/timeout, multipart upload and independent package contents.
- `python3 scripts/validate_skills.py`: four packages passed metadata and relative-reference checks.
- Bundled `skill-creator/scripts/quick_validate.py` was attempted but could not run because the available Python runtimes lack PyYAML. The dependency-free repository validator was used instead; no environment packages were installed.
- Credential scan: no live API key, login token or test password in the published files.

## Production API tests

Host: `https://lensrhyme.com/api/v1`. Account: the designated test account. Authentication for creative operations used its API management Token Key, not its login JWT. Test credentials and full response artifacts remain outside this public repository.

| Module | Evidence | Result |
| --- | --- | --- |
| Shared | Login, obtain/create missing API key, list Workspace and models | Passed |
| Studio Image | Submit real image task, wait for completed status, resolve resource to download URL, fetch PNG | Passed; HTTP 200, image/png, 768433 bytes; provider diagnostics report mocked=false |
| Studio Video | Submit a catalog-listed video model task and poll terminal state | The first model was rejected by upstream with unknown-model error; authentication/task submission worked |
| Canvas | Create project, save image node, read back, generate real image task, create node artifact and query artifact list | Passed; task completed and one generated artifact linked to the original node |
| Workbench | Create project, act, scene and shot, read back parent associations | Passed |
| Workbench generation | Request native shot generation | HTTP 402; billing prevents end-to-end generation verification |

Testing did not change account balance, pricing, model configuration, IP allowlists or deployment. A previously absent test-account Token Key was created; no existing key was rotated. Test projects and their generation evidence were retained for inspection. The application working tree was not modified.

## Limits

These checks do not establish every model/mode, reference-image editing, script import, published Canvas workflow execution, multi-user graph concurrency, Workbench video writeback or timeline rendering. No browser UI regression suite or application build was run because the change is a separate skill repository. Model availability and billing remain deployment/account dependent; a successful skill install does not guarantee that a model can generate.
