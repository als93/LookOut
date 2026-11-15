#!/usr/bin/env python3
"""Offline metadata consistency checks for either the bundled sample or staged full snapshot."""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def main():
    root = ROOT / 'history-data'
    index = json.loads((root/'index.json').read_text())
    records = index['cameras']
    rows = clips = 0
    provider = collections.Counter()
    for c in records:
        d = json.loads((root / c['shard']).read_text())
        assert d['id'] == c['id'] and d['schemaVersion'] == 'lookout-timeline-shard-v4.1'
        assert len(d['rows']) == c['frameCount']
        assert len(d['datedVideos']) == c['datedVideoCount']
        rows += len(d['rows']); clips += len(d['datedVideos']); provider[c['provider']] += 1
    status = json.loads((ROOT/'DATA_STATUS.json').read_text())
    assert len(records) == status['sampleCameraCount']
    assert rows + clips == status['sampleHistoryReferences']
    assert len(records) in (12, 622)
    full_catalog = json.loads((ROOT/'docs/data/catalog-622.json').read_text())
    assert len(full_catalog['cameras']) == 622
    assert {c['id'] for c in records}.issubset({c['id'] for c in full_catalog['cameras']})
    h = json.loads((ROOT/'history-addons/hpwren-offline-events.json').read_text())
    sample = json.loads((ROOT/'history-addons/hpwren-sample-frames.json').read_text())
    u = json.loads((ROOT/'history-addons/uaf-video-leads.json').read_text())
    assert len(h['events']) == 217 and len(sample['sequences']) == 4 and len(u['videos']) == 3011
    assert len({e['id'] for e in h['events']}) == 217
    print(f'PASS {len(records)} camera shards, {rows} still references, {clips} dated clips, '
          f'{len(h["events"])} HPWREN leads, {len(sample["sequences"])} event samples, {len(u["videos"])} UAF leads')

if __name__ == '__main__':
    main()
