"""Validate installable skill metadata and relative references without dependencies."""
from pathlib import Path
import json,re,sys
root=Path(__file__).resolve().parents[1]
for skill in sorted((root/'skills').iterdir()):
    text=(skill/'SKILL.md').read_text()
    assert text.startswith('---\n')
    header=text.split('---',2)[1]
    assert f'name: {skill.name}\n' in header
    assert re.fullmatch('[a-z0-9-]{1,64}',skill.name)
    description=json.loads(next(line.removeprefix('description: ') for line in header.splitlines() if line.startswith('description: ')))
    assert 0<len(description)<1024
    for doc in [skill/'SKILL.md',skill/'references/api.md']:
        for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if '://' not in link:assert (doc.parent/link).exists(),link
    print('Validated',skill.name)
