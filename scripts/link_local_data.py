#!/usr/bin/env python3
"""Link existing local LOOKOUT history/metadata only. Never reads content or downloads media.

Paths are created only if absent. Original target directories are never modified.
"""
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parent.parent

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--history', type=Path, help='Existing history-data with index.json')
    p.add_argument('--addons', type=Path, help='Existing history-addons (from a trusted review package)')
    a=p.parse_args()
    if a.history is None and a.addons is None:
        p.error('Specify --history and/or --addons')
    planned=[]
    for name, source, required in [('history-data',a.history,'index.json'),('history-addons',a.addons,'hpwren-offline-events.json')]:
        if source is None: continue
        target=ROOT/name
        if target.exists() or target.is_symlink():p.error(f'{target} already exists. No replacement performed.')
        real=source.expanduser().resolve(strict=True)
        if not real.is_dir() or not (real/required).is_file():p.error(f'{real} is not an expected {name} directory (missing {required})')
        planned.append((target,real))
    for target,real in planned:
        target.symlink_to(real,target_is_directory=True)
        print(f'Created ignored local link {target} -> {real}; target content unchanged')

if __name__=='__main__':main()
