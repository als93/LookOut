# LOOKOUT Studio v4.10.6 — independent double/triple baseline audit

## Scope and methodology

Source: byte-for-byte v4.10.5 private GitHub starter (`index.html`, 4,984 physical lines / 2.46 MB), plus merged modules and their overlay wrappers, code-only repo scripts, and the previously successful Firefox provider-media probe. This audit assessed source structure, media lifecycle, failure paths, cleanup, URL validation, export/recording, indexed history, metadata integration, and Git staging. It is a **targeted code-path and regression audit**, not a mathematical guarantee that every branch is bug-free; no connected/live-provider requests or production server were run.

Three passes: (1) source structure, parsing, code paths, and repository layout; (2) adversarial state transitions: asynchronous playback, pause, failed draw, early recorder failure, cache/cleanup; (3) regressions against real class/functions and representative local metadata and an independent read of the minimal diff.

## Confirmed defects and minimal corrections

| Priority | Defect in v4.10.5 | v4.10.6 correction | Evidence |
|---|---|---|---|
| P1 | `FramePlayer.record()` creates the completion Promise before the first drawing and `recorder.start()`. On an error while recorder is still inactive, `catch` awaits a `stop` event that will never fire and hangs. | Await the completion Promise during error cleanup **only when an active recorder is actually stopped**. | Actual `FramePlayer` test: two timeout failures before patch, two explicit rejections after. |
| P2 | `FramePlayer.pause()` stopped animation frames but did not invalidate an asynchronous `draw()`, so an in-flight local frame could appear after Pause. | Increment the existing `pending` generation token on pause. | Actual `FramePlayer` test reproduces unwanted advance before patch; passes after. |
| P2 | Historical 12 FPS used `max(100, 1000/FPS)` **after** waiting for the frame to load/decode. | Use the selected frame period minus elapsed work, with zero minimum delay; slow frames remain load-bound (no fabricated frames). | The same Chromium fixture measured 9.61 FPS before, 12.23 FPS after. |

No UI restructuring, provider integration edits, source URL changes, archive mutations, scanner changes, or permission changes were made. The public `index.html` title changes to identify this candidate.

## Test outcomes (candidate)

- **PASS:** Node inline-JavaScript syntax (`tests/preflight.py`); Python compilation of helpers.
- **PASS:** 3/3 deliberately adversarial tests against extracted **actual** `FramePlayer` code: mid-decode Pause, first-frame recorder failure, `MediaRecorder.start()` failure. Original v4.10.5 failed all three.
- **PASS:** 8/8 Chromium historical-player tests with synthetic JPEGs and measured pixels: timestamp/pixel agreement at 12 FPS, injected draw failure preserving previous frame, pause-during-load, variable aspect ratio, fullscreen, and cleanup. Zero dark frames/mismatches in the sampling test.
- **PASS:** 3/3 Chromium collection DOM integration checks using **locally staged** HPWREN/UAF fixture metadata: 217 events, searchable 3-frame sample, 3,011 UAF leads/474 MP4s, no UAF network access until clicked, close cleanup. This metadata is **not** included in the repo package.
- **PASS:** representative actual NIMS shard of **40,600 indexed references** parsed by source function into 40,600 rows and sampled into 500 time-spaced preview references (roughly 201 ms parsing and 1 ms sampling in this runner). No media fetched.
- **PASS:** root `.gitignore` and Git staging dry run, including local `history-data` and `history-addons` symlinks; they must remain untracked.

## Known limits, not quietly described as fixed

1. **P1 before stable release:** Real Firefox v4.10.6 end-to-end test with your **complete** 622-shard local archive, especially NIMS Merced 3/8/12 FPS and the full map, is not performed here. Previous Firefox probe verifies real provider samples, **not** the integrated app.
2. **P2:** The historical canvas uses the first decoded frame's resolution (max 4MP), so later larger images cannot raise the display buffer resolution during that player session. This preserves stable pixels at a possible sharpness cost. Don't resize it mid-play without a non-flickering regression test.
3. **P2:** The historical `load()` holds at most two in-flight images; a burst of new seeks may wait for stale requests to settle rather than immediately prioritizing the latest. Test on slow connections before changing concurrency/abort behavior.
4. **P2:** The historical canvas is tainted by non-CORS cross-origin provider images. It is a playback surface, **not** a capture/export surface. Existing local file/blob WebM export remains a distinct workflow.
5. **P2:** HPWREN has a small number of bundled sample sequences; most event manifests need local staging. UAF lead format and capture dates remain uncertain. Never convert unlocated events/leads into map pins automatically.
6. **P2 for public GitHub:** Merged source provenance, dependency notices, provider rights and optional public software license are not resolved by this code audit. Private GitHub is appropriate; public release requires decisions and review.
7. **P3:** The single HTML contains several generations of wrapper/monkeypatch layers and overlapping media flows. Modularization can improve maintainability but is **high regression risk** until baseline Firefox behavior and end-to-end export tests pass. Avoid speculative rearchitecture now.
8. **P3:** CI is offline source and local-player safety checks, **not** full browser/provider validation. The optional Chromium fixture runner may require local browser access; in this restricted sandbox the equivalent tested harness used intercepted media with no network.

## Release recommendation

**GO for an experimental, code-only private GitHub branch** after reviewing the exact files staged. **NOT a verified stable public release** until the complete Firefox and full-history checks pass. Keep archives, provider lists, controller budgets, and journals separate and unchanged.

## Minimal source change policy

This build intentionally leaves working retrieval, indexing, UI, and the persistent renderer alone. `docs/BUILD_PROVENANCE.md` identifies the original and candidate SHA-256. Compare the `audit/PATCH.diff` before merging. Do not stack another copy of these patches on top of this candidate.
