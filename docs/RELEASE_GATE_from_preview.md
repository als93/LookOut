# v4.10.5 release gate — 2026-11-15

## Confirmed in this preparation pass

- The supplied v4.10.5 ZIP passed all its SHA-256 checks.
- The included guarded v4.10.5 builder reproduced the supplied viewer byte-for-byte (SHA-256 `ae39c546f15220a21f9dc46af5ded022db06209c4807b8692ae3291a8eb40d34`).
- The viewer's inline JavaScript passed Node.js v22 `--check`. All supplied Python scripts compiled.
- The sample history contains exactly 12 actual shards matched to 12 index entries, with both sparse and large sequences.
- **Independently reproduced 8/8 Chromium fixture tests** against the actual inline player code using a restricted sandbox variant (`tests/restricted_chromium_fixture_tests.py`). It loads the full HTML via `page.set_content`, replaces two location-derived metadata base URLs with fixture roots, and adds fixture-only cross-origin image permissions to allow pixel reading. Ordinary localhost/file/data navigation was blocked by browser administrator policy. This is not a real-origin/browser-provider test and does not prove deployed Firefox behavior.
- **3/3 additional Chromium integration DOM fixture checks passed:** one collection button, all 217 staged HPWREN events listed, search and a 3-frame sample, UAF 3,011 leads and 474 MP4 filter results, no UAF video requested before a click, clean modal close. This test deliberately does not load Leaflet, real media or Firefox.
- Earlier **individual media** tests confirmed Firefox decoding/playback of NIMS, PhenoCam, HPWREN, OSU and UAF samples. This does **not** validate the integrated v4.10.5 viewer.

## Blockers to a stable release

- [ ] Firefox 159 on Bazzite: run v4.10.5 NIMS Merced at 3, 8, and 12 FPS; no black frames, timestamps/counters remain accurate, sustained playback acceptable. Record any failures.
- [ ] Firefox: pause, rapid seek, invalid/empty date ranges, missing media, close while loading; no stale frames or post-close requests.
- [ ] Firefox: HPWREN 3-frame event, PhenoCam, UAF HTTPS MP4 and OSU MP4 all work inside **the integrated viewer**.
- [ ] Firefox: real Leaflet map renders, existing camera pins, history-only filter, full-screen, CSV, sparse and single-frame camera behavior preserved.
- [ ] Test with the **actual full local 622-shard** archive using `python3 tests/preflight.py --history /path/to/history-data --require-complete` first. Sample package alone cannot prove full coverage.
- [ ] Decide whether repository is code-only or public GitHub Pages, how indexed metadata will be distributed and whether rights permit it. Choose project code license intentionally.

## Known limitations, not silent failures

- Selecting 12 FPS does not imply 12 actual displayed frames/s: a 100 ms delay is scheduled **after** each image load/decode; independently measured **9.57 FPS** with 20ms synthetic frame latency, below the selector value. Treat as *target FPS* until fixed and measured on the user machine.
- `canvas` drawing of cross-origin images taints the surface; native right-click image saving isn't provided in this player. Frame URLs remain in CSV exports and provider links.
- The first successful decoded frame fixes the canvas backing dimensions (up to 4 MP). Later larger frames may be downsampled. Chrome verified sample; Firefox needs testing.
- Four of 217 HPWREN events have bundled 3-frame samples; the rest need `history-addons/hpwren-sequences/<eventId>.json` staging. They are events, not geolocated cameras.
- UAF 474 MP4 vs 2,537 MPEG leads: MP4 can be tested on demand, MPG not promoted to Firefox-playable; dates are labels, not known capture instants.
- 27 OSU index entries are not mapped to confirmed camera coordinates. No coordinates should be guessed.
- Sample historical index covers 12 cameras only. Provider-hosted media can disappear; signature verification isn't a guarantee of future availability or redistribution rights.

## Fast local checks

1. `python3 scripts/prepare_history.py --link-full /absolute/path/to/history-data` (if not already linked, only in a clean checkout).
2. `python3 tests/preflight.py --history history-data --require-complete`.
3. `python3 -m http.server 8878 --bind 127.0.0.1` and open `http://127.0.0.1:8878/` in Firefox.
4. In the history panel console, check `document.querySelector('.lookout-v41-history')?.dataset.renderer` equals `persistent-canvas-v4105`.
5. Capture/observe NIMS Merced at 12 FPS and verify real pixels, not just JavaScript state. Include network throttling.
6. Check each other provider, fullscreen, search, filters, map and all controls. Report errors and video timestamp.

## Go/no-go

**Go for a GitHub preview source repository** once the source contents and branding are reviewed. **No-go for stable release** until all Firefox and full-index regression gates pass. No changes to the authoritative archive/validation journals are needed.
