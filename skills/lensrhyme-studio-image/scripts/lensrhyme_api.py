#!/usr/bin/env python3
"""Dependency-free LensRhyme API client. Credentials only come from environment."""
import argparse
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid


STUDIO_DEFAULT_MODELS = {
    'image': 'doubao-seedream-5-0-pro-260628',
    'video': 'doubao-seedance-2-0-fast-260128',
    'audio': 'seed-audio-1.0',
}
STUDIO_MODEL_ALIASES = {
    'doubao-seedream-5.0-pro': STUDIO_DEFAULT_MODELS['image'],
    'doubao-seedance-2.0-fast': STUDIO_DEFAULT_MODELS['video'],
}


def prepare_studio_body(method, path, body):
    """Default only Studio media tasks; never change project-bound requests."""
    if method != 'POST' or path != '/tasks/' or not isinstance(body, dict) or body.get('entrypoint') != 'studio':
        return body
    kind = next((k for k in STUDIO_DEFAULT_MODELS if body.get('task_type') == k + '_generation'), None)
    if kind is None:
        return body
    payload = body.get('payload')
    if not isinstance(payload, dict):
        raise ValueError('Studio task payload must be a JSON object')
    model = payload.get('model')
    if model is not None and not isinstance(model, str):
        raise ValueError('model must be a string')
    model = model.strip() if model else STUDIO_DEFAULT_MODELS[kind]
    model = STUDIO_MODEL_ALIASES.get(model, model) or STUDIO_DEFAULT_MODELS[kind]
    payload = {**payload, 'model': model}
    if kind == 'audio' and model == STUDIO_DEFAULT_MODELS['audio']:
        seed = payload.get('seed_audio')
        if not isinstance(seed, dict) or not isinstance(seed.get('text'), str) or not seed['text'].strip():
            raise ValueError('seed-audio-1.0 requires seed_audio.text, not the legacy top-level text/voice_id payload')
        if seed.get('model', model) != model:
            raise ValueError('Conflicting nested Seed Audio model')
    return {**body, 'payload': payload}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, base=None, token=None, workspace=None):
        self.base = (base or os.environ.get('LENSRHYME_BASE_URL', 'https://lensrhyme.com/api/v1')).rstrip('/')
        parsed = urllib.parse.urlsplit(self.base)
        if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.query or parsed.fragment or parsed.path != '/api/v1':
            raise ValueError('Base URL must be an HTTPS origin followed by /api/v1')
        self.token = token or os.environ.get('LENSRHYME_API_KEY', '')
        if not self.token.startswith('ltr_') or any(c.isspace() for c in self.token):
            raise ValueError('Set LENSRHYME_API_KEY to your API management Token Key (ltr_...)')
        self.workspace = workspace or os.environ.get('LENSRHYME_WORKSPACE_ID')
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method, path, body=None, content_type='application/json', timeout=60):
        decoded = urllib.parse.unquote(path)
        if not path.startswith('/') or path.startswith('//') or '\\' in decoded or '#' in path or any(x in ('.', '..') for x in decoded.split('/')) or any(ord(c) < 32 for c in path):
            raise ValueError('Use an API-relative path, not a URL or traversal')
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept': 'application/json'}
        if self.workspace:
            headers['X-Workspace-ID'] = self.workspace
        body = prepare_studio_body(method, path, body)
        data = body if isinstance(body, bytes) else json.dumps(body).encode() if body is not None else None
        if data is not None:
            headers['Content-Type'] = content_type
        req = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=timeout) as r:
                raw = r.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            # Never echo server bodies: they may contain credentials or private inputs.
            raise RuntimeError(f'HTTP {e.code}; check permissions, IP allowlist, model access and request schema. Mutations were not retried.') from None
        except (urllib.error.URLError, TimeoutError) as e:
            raise RuntimeError('Transport failed; submission outcome may be unknown. Inspect existing tasks before resubmitting.') from None

    def wait(self, task_id, seconds=300, interval=5):
        path = '/tasks/' + urllib.parse.quote(task_id, safe='')
        deadline = time.monotonic() + seconds
        while True:
            task = self.request('GET', path)
            if task.get('status') in {'completed', 'failed', 'cancelled', 'canceled', 'aborted', 'timeout', 'timed_out'}:
                return task
            if time.monotonic() >= deadline:
                return {'id': task_id, 'status': task.get('status'), 'poll_timeout': True, 'resume': 'Run wait again with the same task ID; do not submit again.'}
            time.sleep(min(interval, max(0, deadline - time.monotonic())))

    def upload(self, path, file, fields=None):
        boundary = 'lr-' + uuid.uuid4().hex
        parts = []
        for name, value in (fields or {}).items():
            if not re.fullmatch(r'[A-Za-z0-9_]+', name):
                raise ValueError('Invalid form field name')
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        f = Path(file)
        filename = re.sub(r'[^A-Za-z0-9_.-]', '_', f.name)
        mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        parts.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode(), f.read_bytes(), f'\r\n--{boundary}--\r\n'.encode()])
        return self.request('POST', path, b''.join(parts), 'multipart/form-data; boundary=' + boundary, timeout=180)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    r = sub.add_parser('request')
    r.add_argument('method', choices=['GET','POST','PUT','PATCH','DELETE'])
    r.add_argument('path'); r.add_argument('--json-file'); r.add_argument('--out')
    w = sub.add_parser('wait'); w.add_argument('task_id'); w.add_argument('--seconds', type=int, default=300); w.add_argument('--out')
    u = sub.add_parser('upload'); u.add_argument('file'); u.add_argument('--path', default='/upload/'); u.add_argument('--fields-file'); u.add_argument('--out')
    g = sub.add_parser('studio'); g.add_argument('kind', choices=sorted(STUDIO_DEFAULT_MODELS)); g.add_argument('--json-file', required=True); g.add_argument('--name'); g.add_argument('--out')
    s = sub.add_parser('schema'); s.add_argument('path'); s.add_argument('--method', default='POST')
    args = p.parse_args()
    if args.command == 'schema':
        contract = json.loads((Path(__file__).resolve().parents[1] / 'references' / 'api-contract.json').read_text())
        result = contract['paths'][args.path][args.method.lower()]
        refs = set()
        def collect(value):
            if isinstance(value, dict):
                if '$ref' in value:
                    name = value['$ref'].split('/')[-1]
                    if name not in refs:
                        refs.add(name); collect(contract['components']['schemas'][name])
                for v in value.values(): collect(v)
            elif isinstance(value, list):
                for v in value: collect(v)
        collect(result)
        print(json.dumps({'operation':result,'schemas':{n:contract['components']['schemas'][n] for n in sorted(refs)}},ensure_ascii=False,indent=2)); return
    c = Client()
    if args.command == 'request':
        body = json.loads(Path(args.json_file).read_text()) if args.json_file else None
        result = c.request(args.method, args.path, body)
    elif args.command == 'studio':
        payload = json.loads(Path(args.json_file).read_text())
        result = c.request('POST', '/tasks/', {'entrypoint': 'studio', 'task_type': args.kind + '_generation', 'name': args.name or 'Studio ' + args.kind, 'payload': payload})
    elif args.command == 'upload':
        fields = json.loads(Path(args.fields_file).read_text()) if args.fields_file else None
        result = c.upload(args.path, args.file, fields)
    else:
        if args.seconds < 0: p.error('--seconds must be nonnegative')
        result = c.wait(args.task_id, args.seconds)
    rendered = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        fd = os.open(args.out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd,'w') as f: f.write(rendered + '\n')
        print('Response saved to ' + args.out)
    else:
        print(rendered)
    if isinstance(result,dict) and (result.get('poll_timeout') or result.get('status') in {'failed','cancelled','canceled','aborted','timeout','timed_out'}):
        sys.exit(2)


if __name__ == '__main__':
    try: main()
    except (ValueError, RuntimeError, KeyError, OSError) as e:
        print(str(e), file=sys.stderr); sys.exit(1)
