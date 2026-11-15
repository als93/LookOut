# Changelog

## v4.10.7 — local FramePlayer lifecycle patch (not a stable release)

- Prevent superseded asynchronous playback callbacks from creating additional RAF loops after rapid Pause → Play.
- Prevent errors from a superseded frame from stopping the newly started playback session.
- Guarantee export-state and media-track cleanup even when `canvas.captureStream()` or stream setup throws.
- Expand offline regression tests to 6 cases; no provider/media URLs, archives, scan state, or historical player were changed.

# Changelog

## v4.10.6 — baseline stabilization candidate (not a stable release)

- Correct nominal historical FPS scheduling without downloading more frames.
- Pause now cancels in-flight local-frame draws via existing generation token.
- Export setup errors no longer hang waiting for `MediaRecorder.onstop` if recording never began.
- Add offline Node regression checks and document remaining Firefox, data, and rights gates.

Previous v4.10.5 review and provenance remain in `docs/`.
