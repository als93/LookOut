# Full application Firefox regression gate

Check against the **complete local** 622-shard archive served by HTTP, not an isolated media probe or Chromium fixture. Mark results with Firefox version/date and screenshots or short recordings for failures. No provider bulk scans are required.

- [ ] Map loads; pins, existing layers/filters and history-only toggle show expected cameras.
- [ ] NIMS Merced: 3, 8, 12 FPS playback (including slow network); **no black/flashing frames**, no misleading timestamps or counters.
- [ ] Initial load, play/pause, stop, rapid seek, stale/out-of-order requests, date range changes and invalid/empty ranges.
- [ ] Missing frame: unavailable state rather than wrong cached image; next valid frame recovers.
- [ ] Coverage, FPS/date controls, single/sparse archives, 40,600-frame Merced timeline and CSV export.
- [ ] Fullscreen enter/exit/Esc, browser resize, phone-width layout, no canvas stage jumping.
- [ ] PhenoCam historical playback with provider-local unspecified timestamps (not incorrectly labelled UTC).
- [ ] OSU daily MP4, seek, bad-clip official-page fallback, history filter.
- [ ] HPWREN 3-frame sample events and event-page links; 217 listed events without inventing map pins.
- [ ] UAF HTTPS MP4 on-demand, seek, stop on dialog close; `.mpg` listed only as unsupported leads.
- [ ] 622/622 shard existence locally and representative deep inspection of large/small timelines.
- [ ] Browser Console free of release-blocking errors; playback memory stabilized after open/close cycles.
- [ ] Owner chooses code license and completes rights/attribution review **before public GitHub/Pages launch**.

Acceptance distinction: **private source push** requires only inspected files and correct gitignore; **public preview** additionally needs attribution/rights decisions and honest status messaging; **stable release** requires all functionality above.
