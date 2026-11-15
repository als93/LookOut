#!/usr/bin/env python3
"""Offline, read-only LOOKOUT metadata audit and optional private-copy staging.

No provider requests, controller access, journal reading, deletion, or writes to SOURCE.
Default: inspect only. --stage OUTPUT creates a NEW independent repo copy after checks.
"""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent.parent
SHARD_RE = re.compile(r"history-shards/[0-9a-f]{24}\.json\Z")
MAX_GIT_FILE = 100 * 1024 * 1024


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def audit(source):
    source = source.expanduser().resolve(strict=True)
    if not source.is_dir():
        raise ValueError("source must be a history-data directory")
    ix = source / "index.json"
    if not ix.is_file() or ix.is_symlink():
        raise ValueError("source index.json missing or is a symbolic link")
    first_hash = sha256(ix)
    index = json.loads(ix.read_text(encoding="utf-8"))
    cams = index.get("cameras")
    if index.get("schemaVersion") != "lookout-timelapse-index-v4.1" or not isinstance(cams, list):
        raise ValueError("incompatible index schema")
    if index.get("cameraCount") != len(cams):
        raise ValueError("index cameraCount mismatch")
    if len(cams) != 622:
        raise ValueError(f"expected full 622-record index, found {len(cams)}: no staging")

    sizes = []
    paths = set()
    ids = set()
    by_provider = collections.Counter()
    seen_rows = 0
    seen_clips = 0
    duplicate_rows = 0
    total_size = ix.stat().st_size
    shard_hashes = {}
    for c in cams:
        id_ = c.get("id")
        shard = c.get("shard", "")
        if not isinstance(id_, str) or id_ in ids:
            raise ValueError(f"duplicate/invalid camera ID {id_!r}")
        ids.add(id_)
        if not isinstance(shard, str) or not SHARD_RE.fullmatch(shard) or shard in paths:
            raise ValueError(f"unexpected/duplicate shard path: {shard!r}")
        paths.add(shard)
        f = source / shard
        if f.is_symlink() or not f.is_file():
            raise ValueError(f"missing or linked shard: {shard}")
        before = f.stat()
        blob = f.read_bytes()  # one bounded shard at a time (largest original ~few MB)
        after = f.stat()
        if (before.st_ino, before.st_size, before.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
            raise ValueError(f"shard changed while auditing: {shard}")
        if len(blob) >= MAX_GIT_FILE:
            raise ValueError(f"shard exceeds GitHub 100 MiB hard limit: {shard}")
        data = json.loads(blob)
        if data.get("id") != id_ or data.get("schemaVersion") != "lookout-timeline-shard-v4.1":
            raise ValueError(f"shard identity/schema mismatch: {shard}")
        rows, videos = data.get("rows"), data.get("datedVideos")
        if not isinstance(rows, list) or not isinstance(videos, list):
            raise ValueError(f"unexpected row/video format: {shard}")
        if len(rows) != c.get("frameCount") or len(videos) != c.get("datedVideoCount"):
            raise ValueError(f"index/shard count mismatch: {id_}")
        # Exact duplicates within each shard; global URL duplicates need a separate deep audit.
        signatures = set()
        for r in rows:
            if not isinstance(r, list) or len(r) < 2:
                raise ValueError(f"invalid frame row: {id_}")
            key = (r[0], r[1])
            if key in signatures:
                duplicate_rows += 1
            signatures.add(key)
        seen_rows += len(rows)
        seen_clips += len(videos)
        by_provider[str(c.get("provider", "unknown"))] += len(rows) + len(videos)
        sizes.append((len(blob), shard))
        total_size += len(blob)
        shard_hashes[shard] = hashlib.sha256(blob).hexdigest()
    if first_hash != sha256(ix):
        raise ValueError("index changed during audit")
    result = {
        "schemaVersion": "lookout-full-history-local-audit-v1",
        "mode": "read-only-offline",
        "complete": True,
        "cameraRecords": len(cams),
        "shardFiles": len(paths),
        "frameReferences": seen_rows,
        "datedClipReferences": seen_clips,
        "allReferences": seen_rows + seen_clips,
        "metadataBytes": total_size,
        "withinShardDuplicateFrameRows": duplicate_rows,
        "crossShardExactURLDuplicates": "not recomputed; separate legacy audit reported zero",
        "byProviderReferences": dict(by_provider),
        "largestShards": [{"bytes": n, "path": s} for n, s in sorted(sizes, reverse=True)[:5]],
        "indexSha256": first_hash,
        "fileSizeWarning50MiB": any(n >= 50*1024*1024 for n, _ in sizes),
        "rightsStatus": "UNVERIFIED for OSU/UAF and certain other provider material; private use only",
        "note": "No remote requests. Completeness means files/accounting, not provider archival completeness or media playability.",
    }
    return result, shard_hashes


def stage(source, target, result, shard_hashes):
    source = source.expanduser().resolve(strict=True)
    target = target.expanduser().absolute()
    parent = target.parent.resolve(strict=True)
    if target.exists() or target.is_symlink():
        raise ValueError("destination exists: refusing to replace any files")
    if parent == source or parent.is_relative_to(source):
        raise ValueError("destination must be outside original history-data")
    if parent == ROOT or parent.is_relative_to(ROOT):
        raise ValueError("stage outside the source repository, into a NEW directory")
    tmp = Path(tempfile.mkdtemp(prefix=".lookout-private-stage-", dir=parent))
    try:
        # Small explicit repository parts only. Never copy .git, journals, captures, or media.
        for item in ["index.html", ".gitignore", "README.md", "CHANGELOG.md", "DATA_STATUS.json"]:
            shutil.copy2(ROOT / item, tmp / item)
        for folder in [".github", "docs", "scripts", "tests", "history-addons"]:
            shutil.copytree(ROOT / folder, tmp / folder, symlinks=False)
        # Only canonical index and 622 referenced shards, never arbitrary source files.
        (tmp / "history-data" / "history-shards").mkdir(parents=True)
        shutil.copy2(source / "index.json", tmp / "history-data" / "index.json")
        if sha256(tmp / "history-data" / "index.json") != result["indexSha256"]:
            raise ValueError("index changed while copying")
        # The staged catalog follows the owner's CURRENT complete snapshot, not the earlier 622-record preview catalog.
        shutil.copy2(tmp / "history-data" / "index.json", tmp / "docs" / "data" / "catalog-622.json")
        for shard, expected in shard_hashes.items():
            destination = tmp / "history-data" / shard
            shutil.copy2(source / shard, destination)
            if sha256(destination) != expected:
                raise ValueError(f"source changed / copy hash mismatch: {shard}")
        status = json.loads((tmp / "DATA_STATUS.json").read_text())
        status.update({"dataMode": "full_local_snapshot", "sampleCameraCount": 622,
                       "sampleHistoryReferences": result["allReferences"], "fullArchiveShardsNotBundled": 0,
                       "metadataBytes": result["metadataBytes"], "rights": "PRIVATE ONLY. Review provider data rights before publication."})
        (tmp / "DATA_STATUS.json").write_text(json.dumps(status, indent=2) + "\n")
        readme = tmp / "README.md"
        readme.write_text(
            "# LOOKOUT Studio — full private metadata snapshot\n\n"
            "**This staged copy now contains all 622 history shards copied from your local archive.** "
            "It is not the 12-shard preview described in parts of the original README below. "
            "No original data was changed. Provider licensing and full Firefox integration "
            "are NOT cleared for public release. See `PRIVATE_DATA_RELEASE_GATE.md`.\n\n"
            + readme.read_text()
        )
        (tmp / "PRIVATE_DATA_RELEASE_GATE.md").write_text(
            "# Private full-history staging copy\n\n"
            "This is a complete **local metadata snapshot**, not a cleared public release. "
            "It contains third-party provider URL metadata; provider rights and upstream licenses "
            "need review before publication. This staging run did not contact providers or modify "
            "the original archive/controller/journals. Run `python3 tests/preflight.py --history "
            "history-data --require-complete` and review `docs/RIGHTS_AND_ATTRIBUTION.md`.\n")
        os.rename(tmp, target)
    except BaseException:
        shutil.rmtree(tmp)
        raise


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True, help="owner's EXISTING history-data folder (read only)")
    p.add_argument("--report", type=Path, help="optional NEW JSON report path, outside the source")
    p.add_argument("--stage", type=Path, help="optional NEW private repo folder outside source/repo (copies ~505MB)")
    a = p.parse_args()
    result, checksums = audit(a.source)
    print(json.dumps(result, indent=2))
    if a.report:
        output = a.report.expanduser().absolute()
        if output.exists() or output.is_symlink():
            p.error("report path exists: refusing overwrite")
        if output.parent.resolve().is_relative_to(a.source.expanduser().resolve(strict=True)):
            p.error("report path cannot be under source archive")
        with output.open("x", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
            f.write("\n")
        print(f"Created read-only audit report: {output}")
    if a.stage:
        stage(a.source, a.stage, result, checksums)
        print(f"Created independent PRIVATE full-data repository copy: {a.stage}")


if __name__ == "__main__":
    main()
