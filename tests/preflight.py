#!/usr/bin/env python3
"""Offline data-inclusive preflight. Does not contact providers or alter archives."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SHARD_RE = re.compile(r'history-data/history-shards/[0-9a-f]{24}\.json\Z')
PERMITTED_ADDONS = {
    'history-addons/hpwren-offline-events.json',
    'history-addons/hpwren-sample-frames.json',
    'history-addons/uaf-video-leads.json',
}
FORBIDDEN = {'collector', 'validation-controller', 'journals', 'scan-output',
             'validation-results', 'archives', 'PLAYBACK_RESULTS', 'downloads', 'logs'}

def check_data(history, complete):
    ix = history / 'index.json'
    if not ix.is_file() or ix.is_symlink():
        raise AssertionError(f'missing or linked history index: {ix}')
    d = json.loads(ix.read_text())
    assert d.get('schemaVersion') == 'lookout-timelapse-index-v4.1'
    cams = d.get('cameras')
    assert isinstance(cams, list) and d.get('cameraCount') == len(cams)
    assert len(cams) in (12, 622), 'Unexpected partially assembled history-data index'
    missing = []
    for c in cams:
        shard = c.get('shard')
        assert isinstance(shard, str) and re.fullmatch(r'history-shards/[0-9a-f]{24}\.json', shard), 'Invalid shard path'
        f = history / shard
        if not f.is_file() or f.is_symlink():
            missing.append(shard)
    assert not missing, f'{len(missing)} missing/linked shards in active index'
    if complete:
        assert len(cams) == 622, 'Complete index requested; this is only the 12-camera sample'
    print(f'PASS history-data index: {len(cams)} referenced shards present')

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history', type=Path, default=ROOT/'history-data')
    p.add_argument('--require-complete', action='store_true')
    args = p.parse_args()
    h = ROOT / 'index.html'
    source = h.read_bytes()
    assert len(source) > 100000 and b'persistent-canvas-v4105' in source, 'Unexpected viewer build'
    scripts = re.findall(rb'<script(?:\s[^>]*)?>([\s\S]*?)</script>', source, re.I)
    assert len(scripts) == 1
    with tempfile.TemporaryDirectory() as tmp:
        f = Path(tmp)/'viewer.js'; f.write_bytes(scripts[0]);
        subprocess.run(['node','--check',str(f)], check=True)
    assert (ROOT/'README.md').is_file() and (ROOT/'.gitignore').is_file()
    check_data(args.history, args.require_complete)
    status = json.loads((ROOT/'DATA_STATUS.json').read_text())
    if args.history.resolve() == (ROOT/'history-data').resolve():
        expected = 622 if status['dataMode'] == 'full_local_snapshot' else 12
        assert json.loads((ROOT/'history-data/index.json').read_text())['cameraCount'] == expected, 'DATA_STATUS mismatch'
    # Check tracked objects if git checkout; symlinks are forbidden for metadata.
    tracked = subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True)
    if tracked.returncode == 0:
        for raw in tracked.stdout.split(b'\0'):
            if not raw: continue
            relative = raw.decode()
            item = Path(relative)
            assert not (ROOT/item).is_symlink(), f'symlink tracked in git: {relative}'
            assert item.parts[0] not in FORBIDDEN, f'operational data tracked: {relative}'
            if item.parts[0] == 'history-data':
                assert relative == 'history-data/index.json' or SHARD_RE.fullmatch(relative), f'unknown history file tracked: {relative}'
            if item.parts[0] == 'history-addons':
                assert relative in PERMITTED_ADDONS, f'unreviewed add-on tracked: {relative}'
        print('PASS tracked paths: no journals/media/unreviewed add-ons or symlinks')
    else:
        print('Not a Git checkout: tracked-file safety check deferred')
    print('PASS JS syntax and viewer hash:', hashlib.sha256(source).hexdigest())

if __name__ == '__main__':main()
