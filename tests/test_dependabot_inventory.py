"""Exercise the privileged updater with synthetic data and no network access."""
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dependabot_inventory',
                                              ROOT / 'examples/dependabot_inventory.py')
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)
REPOSITORY = 'example/font'
HEAD = 'a' * 40
BASE = 'b' * 40


def manifest_bytes(document):
    return (json.dumps(document, ensure_ascii=False, indent=2) + '\n').encode('utf-8')


@pytest.fixture
def scenario(monkeypatch):
    manifest = {'approval': 'preserved', 'files': {
        name: {'bytes': 3, 'sha256': hashlib.sha256(b'old').hexdigest(), 'license': 'MIT'}
        for name in updater.DEPENDENCY_FILES | {'src/font.py'}
    }}
    event = {'repository': {'full_name': REPOSITORY}, 'workflow_run': {
        'event': 'pull_request', 'conclusion': 'failure',
        'actor': {'login': 'dependabot[bot]'}, 'head_repository': {'full_name': REPOSITORY},
        'head_sha': HEAD, 'head_branch': 'dependabot/pip/example-2', 'pull_requests': [],
    }}
    pr = {'number': 7, 'state': 'open', 'user': {'login': 'dependabot[bot]', 'type': 'Bot'},
          'base': {'ref': 'main', 'sha': BASE}, 'changed_files': 1,
          'head': {'sha': HEAD, 'ref': 'dependabot/pip/example-2',
                   'repo': {'full_name': REPOSITORY}}}
    changes = [{'filename': 'requirements-build.txt', 'status': 'modified'}]
    blob_data = {'manifest': manifest_bytes(manifest), 'dependency': b'package==2\n'}
    tree = {'tree': [
        {'path': 'MANIFEST.json', 'type': 'blob', 'mode': '100644', 'sha': 'manifest'},
        {'path': 'requirements-build.txt', 'type': 'blob', 'mode': '100644', 'sha': 'dependency'},
    ]}
    calls = []
    state = {'manifest': manifest, 'event': event, 'pr': pr, 'changes': changes,
             'blobs': blob_data, 'tree': tree, 'calls': calls, 'raced': False,
             'candidates': [{'number': 7}], 'reject_push': False}

    def fake_api(repository, path, method='GET', data=None):
        assert repository == REPOSITORY
        calls.append((method, path, copy.deepcopy(data)))
        if method != 'GET':
            if path.startswith('git/refs/') and state['reject_push']:
                raise subprocess.CalledProcessError(1, ['gh', 'api'])
            return {'sha': 'new-' + path.split('/')[-1]}
        if path.startswith('pulls?'):
            return state['candidates']
        if path == 'pulls/7':
            result = copy.deepcopy(pr)
            if state['raced'] and sum(p == path for _, p, _ in calls) > 1:
                result['head']['sha'] = 'c' * 40
            return result
        if path == 'pulls/7/files?per_page=100':
            return changes
        if path.startswith('compare/'):
            return {'merge_base_commit': {'sha': BASE}}
        if path == f'contents/MANIFEST.json?ref={BASE}':
            return {'type': 'file', 'encoding': 'base64',
                    'content': base64.b64encode(manifest_bytes(manifest)).decode()}
        if path == f'git/commits/{HEAD}':
            return {'tree': {'sha': 'original-tree'}}
        if path == 'git/trees/original-tree':
            return tree
        if path.startswith('git/blobs/'):
            return {'encoding': 'base64',
                    'content': base64.b64encode(blob_data[path.split('/')[-1]]).decode()}
        raise AssertionError(path)

    monkeypatch.setattr(updater, 'api', fake_api)
    return state


def writes(scenario):
    return [(method, path, data) for method, path, data in scenario['calls'] if method != 'GET']


def test_updates_only_manifest_and_dispatches_ci(scenario):
    result = updater.update_inventory(scenario['event'], REPOSITORY)
    assert result.startswith('updated: PR #7')
    mutations = writes(scenario)
    assert [path for _, path, _ in mutations] == [
        'git/blobs', 'git/trees', 'git/commits',
        'git/refs/heads/dependabot/pip/example-2', 'actions/workflows/ci.yml/dispatches']
    updated = json.loads(mutations[0][2]['content'])
    expected = copy.deepcopy(scenario['manifest'])
    contents = scenario['blobs']['dependency']
    expected['files']['requirements-build.txt'].update(
        bytes=len(contents), sha256=hashlib.sha256(contents).hexdigest())
    assert updated == expected
    assert mutations[1][2]['base_tree'] == 'original-tree'
    assert mutations[1][2]['tree'] == [
        {'path': 'MANIFEST.json', 'mode': '100644', 'type': 'blob', 'sha': 'new-blobs'}]
    assert mutations[2][2]['parents'] == [HEAD]
    assert mutations[3][2] == {'sha': 'new-commits', 'force': False}
    assert mutations[4][2] == {'ref': 'dependabot/pip/example-2'}


@pytest.mark.parametrize('field,value', [
    ('event', 'push'), ('event', 'workflow_dispatch'), ('conclusion', 'success'),
    ('actor', {'login': 'contributor'}), ('head_repository', {'full_name': 'other/fork'}),
])
def test_unrelated_runs_do_not_access_repository(scenario, field, value):
    scenario['event']['workflow_run'][field] = value
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert scenario['calls'] == []


@pytest.mark.parametrize('change', ['closed', 'author', 'fork', 'stale', 'branch', 'base'])
def test_out_of_scope_pr_is_not_written(scenario, change):
    pr = scenario['pr']
    if change == 'closed':
        pr['state'] = 'closed'
    elif change == 'author':
        pr['user']['login'] = 'contributor'
    elif change == 'fork':
        pr['head']['repo']['full_name'] = 'other/fork'
    elif change == 'stale':
        pr['head']['sha'] = 'c' * 40
    elif change == 'branch':
        pr['head']['ref'] = 'main'
    else:
        pr['base']['ref'] = 'release'
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


@pytest.mark.parametrize('filename,status', [
    ('.github/workflows/ci.yml', 'modified'), ('src/font.py', 'modified'),
    ('requirements-build.txt', 'added'), ('requirements-build.txt', 'removed'),
    ('requirements-build.txt', 'renamed'),
])
def test_other_changes_require_manual_review(scenario, filename, status):
    scenario['changes'][:] = [{'filename': filename, 'status': status}]
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


def test_truncated_file_list_is_rejected(scenario):
    scenario['pr']['changed_files'] = 101
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


@pytest.mark.parametrize('mode', ['120000', '100755', '040000'])
def test_symlink_executable_and_directory_are_rejected(scenario, mode):
    scenario['tree']['tree'][1]['mode'] = mode
    with pytest.raises(ValueError, match='regular, non-executable'):
        updater.update_inventory(scenario['event'], REPOSITORY)
    assert writes(scenario) == []


@pytest.mark.parametrize('change', ['approval', 'source_hash', 'license', 'unchanged_dependency'])
def test_manifest_cannot_promote_other_changes(scenario, change):
    modified = copy.deepcopy(scenario['manifest'])
    if change == 'approval':
        modified['approval'] = 'changed'
    elif change == 'source_hash':
        modified['files']['src/font.py']['sha256'] = 'changed'
    elif change == 'unchanged_dependency':
        modified['files']['requirements-dev.txt']['sha256'] = 'changed'
    else:
        modified['files']['requirements-build.txt']['license'] = 'changed'
    scenario['blobs']['manifest'] = manifest_bytes(modified)
    with pytest.raises(ValueError, match='require review'):
        updater.update_inventory(scenario['event'], REPOSITORY)
    assert writes(scenario) == []


def test_already_updated_inventory_is_idempotent(scenario):
    scenario['changes'].append({'filename': 'MANIFEST.json', 'status': 'modified'})
    scenario['pr']['changed_files'] = 2
    original = manifest_bytes(scenario['manifest'])
    scenario['blobs']['manifest'] = updater.refresh_manifest(
        original, original, {'requirements-build.txt': scenario['blobs']['dependency']})
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('unchanged:')
    assert writes(scenario) == []


def test_raced_head_is_not_written(scenario):
    scenario['raced'] = True
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


def test_rejected_ref_update_does_not_dispatch_ci(scenario):
    scenario['reject_push'] = True
    with pytest.raises(subprocess.CalledProcessError):
        updater.update_inventory(scenario['event'], REPOSITORY)
    assert writes(scenario)[-1][1].startswith('git/refs/')


def test_no_open_pr_does_not_write(scenario):
    scenario['candidates'] = []
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


def test_multiple_open_prs_do_not_write(scenario):
    scenario['candidates'].append({'number': 8})
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert writes(scenario) == []


def test_wrong_repository_event_does_not_access_repository(scenario):
    scenario['event']['repository']['full_name'] = 'other/fork'
    assert updater.update_inventory(scenario['event'], REPOSITORY).startswith('skipped:')
    assert scenario['calls'] == []
