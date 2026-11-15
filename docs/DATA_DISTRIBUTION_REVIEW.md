# Historical metadata distribution / rights gate

This is an **evidence-based staging assessment, not an authorization to distribute third-party content**. Last reviewed 2026-11-15.

## Inventory

- The active viewer sample has 12 complete shards: 40,694 still references + 58 dated OSU clip references = **40,752** total references.
- The original 622-camera index has been preserved for comparison in `docs/data/catalog-622.json` but is deliberately **not** served as the sample's active index.
- The owner holds an estimated 623-file, 504,919,500-byte archival metadata snapshot on their PC (previous handoff report); this package does **not** contain it.
- `history-addons/` contains partial staging: 217 HPWREN events, 4 sampled events with 3 frames each, and 3,011 UAF leads. Event leads are not geolocated camera pins, and URL leads are not Firefox verification or rights permission.
- **No JPEG, MP4, MPEG, collection journals, passwords, tokens or controllers are packaged.**

## Provider-specific evidence and next decision

| Provider | Terms/evidence | Decision for public data publication |
|---|---|---|
| HPWREN FIgLib archive | Archived imagery/data (>24h old): CC BY-NC 4.0 with required credit and FIgLib paper citation; real-time imagery has additional automated retrieval/embedding requirements | Retain noncommercial distinction and attribution. Do not imply this allows live re-broadcast or commercial republishing |
| PhenoCam | Network archive fair-use policy 2024: CC BY 4.0, acknowledgement required | Document exact attribution + site-level conditions if present |
| USGS NIMS | USGS-authored data generally public domain; exceptions for third-party assets | Verify specific NIMS source and acknowledge USGS. Do not assume every image is USGS-owned |
| OSU webcams | Provider page explains how clips are made, but no clear general redistribution license found for video history dataset | **Unresolved:** hold public data packaging pending clarification |
| UAF Geophysical Institute Optics | Public archive access confirmed; no clear current redistribution terms found for the collected MPEG/MP4 URL inventory | **Unresolved:** hold public data packaging pending clarification |
| Leaflet, hls.js, other merged code | External dependencies may have distinct software licenses; bundled code-origin audit not complete | Preserve notices and audit merged modules before choosing a project LICENSE |

## What can be published now?

A **private experimental source-only repo** (with no provider metadata) is the lowest-risk initial GitHub path. This data-inclusive ZIP is intentionally a **private testing candidate**; GitHub is a third party even for private repositories, so source rights and contractual restrictions still matter. Public data sharing or site deployment should wait for a provider-by-provider license/attribution decision. Metadata URLs are not necessarily copyrighted images, but a curated compilation or automated access may still carry terms/contractual obligations.

For a deployable public service, also check each provider's hotlink, automated collection, and live-camera embedding rules. No completed signature test grants any redistribution rights.

## Official references

- HPWREN: https://www.hpwren.ucsd.edu/cc.html
- PhenoCam: https://zenodo.org/records/14854980/files/Fair-use_Statement.pdf?download=1
- USGS: https://www.usgs.gov/information-policies-and-instructions/copyrights-and-credits
- OSU webcams: https://webcam.oregonstate.edu/about/events
- UAF GI Optics portal: https://optics.gi.alaska.edu/optics/realtime/
- GitHub file limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

## Remaining mechanical checks

- Run `scripts/audit_full_archive.py` with the owner's 623-file dataset. Confirm byte sizes, counts, within-shard duplicates, present files and any 50/100 MiB file-size restrictions.
- If available, inspect separate older cross-shard duplicate URL report and relevant collector provenance (no provider re-scans).
- Inspect upstream JS module provenance and dependency licenses.
- Verify all five providers in real Firefox on the full version.
- Keep rare single-frame histories, gaps, timestamps and uncertain provenance intact.
