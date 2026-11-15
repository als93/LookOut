# v4.10.7 — focused FramePlayer lifecycle review

## Scope

Input: exact v4.10.6 baseline (`2fab777754bb1bc04d829fbd54b3ee95e6c295de718efcaee1c29d54d4aa3a7d`).
Output: proposed v4.10.7 clone (`c7710561d938eb91c9f1e3eea693184bfb3d48178873a3395a2d375f48405f7f`).
This is a **test candidate, not a stable release**. No archive, provider source, scanner, journal, historical player, camera map or UI layout was changed.

## Verified defects in v4.10.6

1. **Rapid Pause → Play:** an old `tick()` callback resumes after a pending `draw()` and sees `this.playing === true` from a newer session; it schedules a second RAF loop. If that old draw rejects, its error handler also pauses the newer playback session.
2. **Capture setup failure:** `canvas.captureStream(fps)` runs after `exporting=true` but outside the `try/finally`. A thrown error leaves `exporting` locked. Stream `getVideoTracks` failure was similarly outside cleanup.

## Narrow fixes

- `FramePlayer.playRun` is an integer session token. `play()` captures its session; `pause()` invalidates the session. Both the old callback's `catch` and its next-RAF scheduling check that token. No additional timers, queues, or helpers are introduced.
- Create the stream and query its track inside the existing `record()` `try`, with a nullable stream in `finally`; the existing error path and restoration are retained. The former `MediaRecorder.start`/first-decode cleanup fixes remain unchanged.

## Reproduction and test evidence

Run `node tests/frameplayer_regressions.cjs index.html` from `repo/`. The six checks include the original three v4.10.6 regressions plus (a) duplicate-loop race, (b) late failure pausing newer playback, and (c) captureStream throw and no-track retry. The same six-case test file on v4.10.6 reproduces **3 failures**; the patched candidate passes **6/6**.

Additional static checks: `python3 tests/preflight.py`, JavaScript parse and ZIP hash checks. The prior historical Chromium fixture was **not repeated for this narrow edit**; the historical player function is unchanged. No real Firefox/live-provider check in this package.

## Firefox verification still required

Use the full archive and Firefox locally: local-image import → Play → rapid Pause/Play while loading → final paused frame accuracy; then WebM export on supported Firefox encoders, including a forced failure. Also repeat NIMS 3/8/12 FPS, date range/seek, and provider video integration before public release.

## Publication gates

Safe for review in a **private source repository** after inspecting Git staging. Not a verified stable release. Provider redistribution permissions, code provenance and public license still need review.
