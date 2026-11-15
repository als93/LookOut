# Build provenance

This snapshot is a byte-identical copy of the `candidate/LOOKOUT-Studio-map-v6.2-HISTORY-v4.10.5-PERSISTENT-CANVAS-TEST.html` from the user-provided `LOOKOUT_v4.10.5_review.zip`, renamed to `index.html` for source-repository convenience.

SHA-256 of `index.html`:

`ae39c546f15220a21f9dc46af5ded022db06209c4807b8692ae3291a8eb40d34`

The supplied guarded `build_v4105.py` was independently run against its v4.10.4 baseline in a temporary copy, yielding the identical SHA-256. Neither baseline nor complete review source is included in this GitHub staging snapshot to avoid duplicating a 2.46 MB monolithic build; preserve the original review ZIP separately for audit/rollback.

This staging operation changed NO executable code and does not claim to fix the playback-speed issue. `history-addons` JSON files are copied verbatim from the review package. `examples/history-data` was made by filtering the earlier handoff's exact 622-camera index to the 12 bundled shards; its note/cameraCount were explicitly changed so the demo doesn't pretend to be complete.

A separate, clearly instrumented Chromium test harness independently reproduced the reviewer's **8/8** fixture checks after avoiding the sandbox navigation restriction. It is included as `tests/restricted_chromium_fixture_tests.py`. This test harness injects fixture-only CORS behavior; the shipped viewer's source and hash are unchanged.

## v4.10.6 audit amendment

- Input v4.10.5 SHA-256: `ae39c546f15220a21f9dc46af5ded022db06209c4807b8692ae3291a8eb40d34`.
- Audited v4.10.6 SHA-256: `2fab777754bb1bc04d829fbd54b3ee95e6c295de718efcaee1c29d54d4aa3a7d`.
- The v4.10.5 viewer remains unchanged in the source package. This candidate changes only `FramePlayer.pause`, `FramePlayer.record` error cleanup, historical `advance()` scheduling and the document title.
- The v4.10.6 patch is separately reviewed in `docs/BASELINE_AUDIT.md`.

## v4.10.7 lifecycle amendment

- Input v4.10.6 SHA-256: `2fab777754bb1bc04d829fbd54b3ee95e6c295de718efcaee1c29d54d4aa3a7d`.
- Candidate v4.10.7 SHA-256: `c7710561d938eb91c9f1e3eea693184bfb3d48178873a3395a2d375f48405f7f`.
- Build: `audit/build_v4107.py` requires the exact v4.10.6 hash and refuses to overwrite output.
- Changes: only the local `FramePlayer` session/RAF lifecycle, `captureStream` setup cleanup, and document title. The NIMS/PhenoCam/HPWREN historical still player and all provider access code remain byte-identical.
- Added Node tests demonstrate failures on v4.10.6 and passes on v4.10.7; no real Firefox session was performed in this environment.
