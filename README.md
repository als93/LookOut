# LOOKOUT Studio — full private metadata snapshot

**This staged copy now contains all 622 history shards copied from your local archive.** It is not the 12-shard preview described in parts of the original README below. No original data was changed. Provider licensing and full Firefox integration are NOT cleared for public release. See `PRIVATE_DATA_RELEASE_GATE.md`.

# LOOKOUT Studio — private data-inclusive development preview

**v6.2 HISTORY v4.10.7 | private test snapshot | not a public release**

LOOKOUT is a map-first explorer for live/latest cameras, historical still imagery and provider video, with timelines, seeking, time-lapse playback, coverage visualization and available export controls. The **viewer HTML is byte-identical to v4.10.7**. This package changes only repository documentation, data files and offline data-preparation tooling.

## What is actually included

| Component | Available in this ZIP |
|---|---|
| `index.html` | Full v4.10.7 viewer — unchanged |
| `history-data/index.json` | **12-camera sample index** (not the complete archive) |
| `history-data/history-shards/` | 12 *complete* representative shards, 40,752 dated media references (40,694 stills and 58 OSU clips) |
| `docs/data/catalog-622.json` | 622-camera *catalog/index records*, **without 610 corresponding full shards**; not used by the viewer |
| `history-addons/hpwren-offline-events.json` | 217 HPWREN **event leads**, not 217 verified camera locations |
| `history-addons/hpwren-sample-frames.json` | Four 3-frame event samples; not complete event histories |
| `history-addons/uaf-video-leads.json` | 3,011 URL leads, not confirmed playable/rights-cleared videos |
| Provider media bodies | **Not included** — browser retrieves selected media from provider sites |
| Validation-controller state / journals | **Never included** |

**Full dataset:** the owner's local archival snapshot was reported as **622 shards + index / 5,113,750 URL references / ~505 MB metadata**. It is NOT in this download; the complete 610 remaining shards are on the owner's PC. The full index is stored separately as catalog reference material; presenting it as the active index without the missing shards would cause misleading 404s.

## Run this private preview

```bash
python3 tests/preflight.py
node tests/frameplayer_regressions.cjs index.html
python3 -m http.server 8878 --bind 127.0.0.1
```

Open **http://127.0.0.1:8878/** in Firefox. Use `http://`, not `file://`. The map, live provider streams and dependencies need network access. Selecting a provider sample downloads only the selected media. Please note this is a **sample preview** and does not expose all 622 cameras' history.

## Audit YOUR complete local archive (offline, read only)

The script **does not start scanning providers, download JPEGs, alter the archive, or access the validation controller**. It checks all 622 shard files and validates counts, IDs, checksums, relative paths, malformed rows and within-shard duplicate entries. The audit requires local disk reads; it does **not** re-check provider hosts or perform the older full cross-shard duplicate-URL audit.

```bash
python3 scripts/audit_full_archive.py \
  --source "$HOME/Downloads/LOOKOUT_V41_REPAIR_DRAFT/LOOKOUT_V41_PREVIEW/history-data" \
  --report "$HOME/Downloads/LOOKOUT-full-history-audit.json"
```

The output includes total metadata bytes, provider-specific reference counts, largest files and data consistency flags. If the original 622 shards are not there, the command **fails rather than silently claiming completeness**. No file is changed in the source archive.

## Make a complete PRIVATE data-inclusive repository copy

After a successful audit, use the **same script** with `--stage` to create a completely new directory containing the unchanged viewer **plus a copied full 623-file archive**. This requires available disk space for a separate ~505 MB copy; neither the source archive nor your original repo is overwritten.

```bash
python3 scripts/audit_full_archive.py \
  --source "$HOME/Downloads/LOOKOUT_V41_REPAIR_DRAFT/LOOKOUT_V41_PREVIEW/history-data" \
  --stage "$HOME/Projects/LOOKOUT-Studio-FULL-PRIVATE"

cd "$HOME/Projects/LOOKOUT-Studio-FULL-PRIVATE"
python3 tests/preflight.py --history history-data --require-complete
```

**No Git push is performed.** Staging is an independent snapshot; the tool refuses existing destinations and rechecks file hashes during copying. The `history-addons/` in the snapshot are the **partial bundled samples**, not your complete local HPWREN event manifests. Those require a separate guarded import/review.

## GitHub policy

This preview includes third-party metadata URL lists with **unresolved redistribution questions**. It is suitable for *local evaluation* and for **considering a private repo** after reviewing provider terms and upstream code origins; it is not approved as a publicly redistributed data package or public GitHub Pages site. Private GitHub is still a third-party upload, and the choice to upload is yours.

The repository contains **no software LICENSE** because authorship/merged-source rights are still under review and the project's license is the owner's decision. Provider licenses would remain separate in any case. See `docs/DATA_DISTRIBUTION_REVIEW.md` and `docs/RIGHTS_AND_ATTRIBUTION.md`.

Before a GitHub push, inspect `git status --short` and `git ls-files` and confirm you are not accidentally including other files from your PC. A Git staging test is included in `tests/preflight.py`. **Do not run `git add -f` on collection journals, downloaded media, or third-party data without approval.**

## Unchanged existing functionality and known limitations

The local viewer has not been modified. Fixture tests of v4.10.7 passed previously, but full Firefox regression of the integrated version remains open. Live/latest viewing, NIMS/PhenoCam timeline, HPWREN limited samples, OSU and UAF video integration, 3–12 FPS playback, fullscreen, CSV export and local WebM export should all be verified in Firefox before declaring a stable release. The 12-camera sample is **not representative of full archive completeness or provider use rights**.
