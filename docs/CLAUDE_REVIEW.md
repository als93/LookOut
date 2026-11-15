# LOOKOUT v4.10.4 independent review → v4.10.5 test candidate

Evidence labels: **[CHROMIUM]** run by me in Chromium against the real viewer in the real app page (real CSS) ·
**[STATIC]** code reading only · **[UNVERIFIED]** needs Firefox on your machine. **Nothing here was run in Firefox.**

## 1. Verdict
- v4.10.4 is **safe to test in Firefox** (no data written, no archive/journal/controller access, diff is 3 small hunks vs v4.10.3, SHA-256s all verify).
- It is **not proven** to cure the flash. The author's "125 screenshots, 0 black" result has no discriminating power: the unfixed v4.10.3 `<img>` build also shows 0 dark frames under the same sampling in Chromium. [CHROMIUM]
- Recommendation: **REVISE (minor)** → test **v4.10.5** (one narrow fix) in Firefox. Proceed to production only if the Firefox checklist passes.

## 2. Confirmed findings (priority order)
| # | Sev | Finding | Evidence | In v4.10.5 |
|---|-----|---------|----------|-----------|
| 1 | Med | `fillRect` over the whole canvas runs *before* `drawImage`. If the draw throws, the canvas is left dark but still visible and still labelled as the previous frame. Contradicts the stated design (review Q4: "previous pixels must remain"). Injected failure → centre pixel (11,21,27). | [CHROMIUM] T2 fails on 4.10.4 | **Fixed**: draw first, then repaint only letterbox bars |
| 2 | Med (pre-existing) | "12 FPS" can never run at 12: `setTimeout(advance, Math.max(100, 1000/fps))`, and the delay starts *after* load+decode. Measured 9.2 fps at "12 FPS", 7.5 at "8 FPS". Your Firefox test is therefore a *gentler* test than the label says, and the label is wrong. | [STATIC]+[CHROMIUM] | Not changed (changes load profile; see §5) |
| 3 | Low | Test-suite weaknesses: stub CSS (no real fullscreen/simple-UI rules, which live in other IIFEs); screenshot cadence is unrelated to compositor frames; "pause" check is timing-flaky (it failed once for me because CDP latency exceeded the 160 ms fixture delay; driven in-page it passes); no baseline control. | [CHROMIUM] | Replaced by `tests/real_page_tests.py` |
| 4 | Low | Surface resolution is locked to the first decoded frame (after Apply = the *last* frame in range). A small first frame permanently down-scales later large ones (320×180 → stays 320×180). | [CHROMIUM] | Not changed; author's stated limitation |
| 5 | Low | Page `<title>` still read "Historical Viewer v4.9 CLAUDE TEST" (identity check by title was misleading). | [STATIC] | Fixed (cosmetic) |
| 6 | Info | Dead code left from the `<img>` design: `old!==still` in cache eviction, `image!==still` in the decode catch, `still.removeAttribute('src')` in cleanup. Harmless. | [STATIC] | Left alone to keep the diff auditable |
| 7 | Info | Right-click "Save image as" lost on the still (tainted canvas); no "open frame" link. CSV export unaffected. | [STATIC] | Optional, §5 |
| 8 | Info | Possible context/GPU surface loss in Firefox would leave a paused canvas blank until the next draw; not handled. Rare. | [STATIC] | Not changed |

## 3. What I checked and found sound
- Label, counter, scrubber and status are updated only after the draw, on the same task. 419–421 `requestAnimationFrame` samples at 12 FPS, **0** label/pixel mismatches, 0 dark. [CHROMIUM, same-origin fixture so pixels could be read]
- Stale/out-of-order responses: `gen`/`token`/`epoch` checks after both awaits; rapid seeks → latest wins; pause cancels pending advance. [CHROMIUM + STATIC]
- Cross-origin drawing works without CORS; canvas is tainted, nothing reads pixels back. [CHROMIUM]
- Layout in the real page CSS, normal and real fullscreen: canvas and old `<img>` render identically (circle aspect 1.186 vs 1.185 undistorted). [CHROMIUM]
- Mixed aspect ratios letterbox correctly with no stale bars. [CHROMIUM]
- Close during autoplay: panel removed, zero further requests, no page errors. [CHROMIUM]
- Frame URLs are allow-list validated in `lookoutV41MakeFrames` (no change). [STATIC]
- Memory: ≤2 pending + ≤8 cached decoded images + one ≤4 MP canvas (~16 MB); eviction removes `src`. [STATIC]
- The one structural win I can measure: with the old design Playwright element screenshots failed 21 times (node replaced under the sampler); with the canvas, 0. [CHROMIUM]

## 4. Is the persistent canvas the right long-term fix?
Plausible and architecturally sound, **but the cause is still a hypothesis.** My best explanation for Firefox is that a freshly mounted `<img>` still needs a raster decode at its *displayed* (down-scaled) size even after `decode()`, and paints nothing until that finishes. `drawImage` renders synchronously into a retained buffer that the compositor just scales, which removes that whole class of problem. That would also explain why DOM/decode-state tests passed. I could not reproduce the flash in Chromium at all, so I cannot confirm this. It does not merely hide the symptom: the old pixels are only replaced once new ones are drawn. Keep it if the Firefox checklist passes. The fallback (author's note) is two permanently mounted `<img>` elements swapped by `visibility`, not by DOM replacement.

## 5. Optional, kept out of the candidate
- **Real 12 FPS:** lower the clamp (e.g. `Math.max(60, ...)`) and schedule from the frame start, not after load. Raises request pressure; do it as its own change after the flash question is settled.
- Small "Open current frame" link beside the canvas to restore saving the image.
- Stage letterbox colour (#0b151b) differs slightly from the fullscreen stage (#05080b) on non-16:9 frames.
- UI polish ideas (separate from bug fixes): merge the repeated "Date range & playback" heading with the controls row; put the Play/Fullscreen buttons directly under the scrubber; show a quiet inline spinner instead of replacing the stage text with "Loading selected frame…"; show effective FPS next to the selector so the label is honest; keep sparse-archive notes in a collapsed "About this timeline" line.

## 6. Reproduce
`python3 source/build_v4105.py` (hash-guarded, refuses overwrite) ·
`python3 tests/real_page_tests.py <viewer.html> --chromium <chrome path>`
Results on this machine: v4.10.4 → 7/8 (T2 fails); v4.10.5 → 8/8. Chromium only.

## 7. Firefox regression checklist (v4.10.5)
1. Console: `document.querySelector('.lookout-v41-history').dataset.renderer` → `persistent-canvas-v4105`; tab title contains v4.10.5; use a fresh port/URL.
2. NIMS Merced, 120 frames, 12 FPS: record 30 s screen video; scrub the video frame-by-frame for any black stage. Repeat at 3 FPS and 8 FPS.
3. Pause/Play mid-run; drag the scrubber rapidly; seek to a missing frame, then a good one.
4. Apply a different date range during playback; Apply an invalid range.
5. Player fullscreen on/off during playback; resize the window.
6. Repeat on HPWREN and PhenoCam (same still path); open OSU and UAF (video paths, expected unchanged).
7. Close the player mid-playback; confirm no further image requests in the Network tab.
8. Check the console for "LOOKOUT history frame draw failed" warnings.
9. Single-frame and sparse cameras; CSV export still downloads.
If it still flashes: report the video timestamp and whether the **canvas itself** or the whole stage goes black. That decides between a compositor bug and a different cause.
