"""Refresh only dependency hashes in same-repository Dependabot pull requests."""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.parse import quote

DEPENDENCY_FILES = {'pyproject.toml', 'requirements-build.txt', 'requirements-dev.txt'}


def api(repository, path, method='GET', data=None):
    command = ['gh', 'api', '--method', method, f'repos/{repository}/{path}']
    if data is not None:
        command.extend(['--input', '-'])
    result = subprocess.run(command, input=None if data is None else json.dumps(data),
                            text=True, encoding='utf-8', capture_output=True, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


def blob_bytes(repository, entry):
    if entry['type'] != 'blob' or entry['mode'] != '100644':
        raise ValueError('Inventory inputs must be regular, non-executable files')
    blob = api(repository, f"git/blobs/{entry['sha']}")
    if blob['encoding'] != 'base64':
        raise ValueError('Expected base64 Git blob')
    return base64.b64decode(blob['content'])


def refresh_manifest(original, current, dependencies):
    """Preserve all metadata and non-dependency records, including prior approvals."""
    baseline = json.loads(original)
    manifest = json.loads(current)
    normalized = copy.deepcopy(manifest)
    for name in dependencies:
        if name not in DEPENDENCY_FILES:
            raise ValueError('Unsupported dependency path')
        for field in ('bytes', 'sha256'):
            normalized['files'][name][field] = baseline['files'][name][field]
    if normalized != baseline:
        raise ValueError('Manifest changes outside dependency sizes and hashes require review')
    for name, contents in dependencies.items():
        manifest['files'][name]['bytes'] = len(contents)
        manifest['files'][name]['sha256'] = hashlib.sha256(contents).hexdigest()
    return (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


def update_inventory(event, repository):
    run = event['workflow_run']
    if (event['repository']['full_name'] != repository
            or run['event'] != 'pull_request' or run['conclusion'] != 'failure'
            or run['head_repository']['full_name'] != repository
            or run['actor']['login'] != 'dependabot[bot]'):
        return 'skipped: not a failed same-repository Dependabot PR run'
    # workflow_run.pull_requests can be empty, including on genuine Dependabot runs.
    head_query = quote(repository.split('/')[0] + ':' + run['head_branch'], safe='')
    candidates = api(repository, f'pulls?state=open&base=main&head={head_query}&per_page=100')
    if len(candidates) != 1:
        return 'skipped: no unique open PR for the run branch'
    number = candidates[0]['number']
    pr = api(repository, f'pulls/{number}')
    if (pr['state'] != 'open' or pr['user']['login'] != 'dependabot[bot]'
            or pr['user']['type'] != 'Bot' or pr['base']['ref'] != 'main'
            or pr['head']['repo']['full_name'] != repository
            or not pr['head']['ref'].startswith('dependabot/')
            or pr['head']['sha'] != run['head_sha']):
        return 'skipped: PR closed, out of scope, or updated since the failed run'
    changes = api(repository, f'pulls/{number}/files?per_page=100')
    if (len(changes) != pr['changed_files']
            or any(item['status'] != 'modified'
                   or item['filename'] not in DEPENDENCY_FILES | {'MANIFEST.json'}
                   or 'previous_filename' in item for item in changes)):
        return 'skipped: changes outside existing dependency files and inventory'
    changed_dependencies = {item['filename'] for item in changes} & DEPENDENCY_FILES
    if not changed_dependencies:
        return 'skipped: no dependency changes'

    head = pr['head']['sha']
    comparison = api(repository, f"compare/{pr['base']['sha']}...{head}")
    base = comparison['merge_base_commit']['sha']
    original = api(repository, f'contents/MANIFEST.json?ref={base}')
    if original['type'] != 'file' or original['encoding'] != 'base64':
        raise ValueError('Expected a regular baseline manifest')
    commit = api(repository, f'git/commits/{head}')
    tree = api(repository, f"git/trees/{commit['tree']['sha']}")
    if tree.get('truncated'):
        raise ValueError('Incomplete Git tree')
    entries = {entry['path']: entry for entry in tree['tree']}
    current = blob_bytes(repository, entries['MANIFEST.json'])
    dependencies = {name: blob_bytes(repository, entries[name])
                    for name in sorted(changed_dependencies)}
    updated = refresh_manifest(base64.b64decode(original['content']), current, dependencies)
    if updated == current:
        return 'unchanged: inventory already matches'

    # Recheck before writing; the final non-force ref update also rejects a raced push.
    latest = api(repository, f'pulls/{number}')
    if latest['state'] != 'open' or latest['head']['sha'] != head:
        return 'skipped: PR changed during inventory calculation'
    blob = api(repository, 'git/blobs', 'POST',
               {'content': updated.decode('utf-8'), 'encoding': 'utf-8'})
    new_tree = api(repository, 'git/trees', 'POST', {
        'base_tree': commit['tree']['sha'],
        'tree': [{'path': 'MANIFEST.json', 'mode': '100644',
                  'type': 'blob', 'sha': blob['sha']}],
    })
    new_commit = api(repository, 'git/commits', 'POST', {
        'message': 'Refresh inventory for Dependabot dependency update',
        'tree': new_tree['sha'], 'parents': [head],
    })
    branch = pr['head']['ref']
    api(repository, f'git/refs/heads/{quote(branch, safe="/")}', 'PATCH',
        {'sha': new_commit['sha'], 'force': False})
    # Token-authored pushes do not reliably start CI; dispatch the read-only checks.
    api(repository, 'actions/workflows/ci.yml/dispatches', 'POST', {'ref': branch})
    return f"updated: PR #{number}; CI dispatched for {new_commit['sha']}"


if __name__ == '__main__':
    payload = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    print(update_inventory(payload, os.environ['GITHUB_REPOSITORY']))
