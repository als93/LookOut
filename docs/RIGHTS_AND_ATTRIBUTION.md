# Provider, map, and dependency rights — public-release checklist

**This file documents external terms identified on 2026-11-15. It is not legal advice, a complete compliance audit, or permission to redistribute datasets.** This private preview includes 12 sample history shards and partial HPWREN/UAF URL metadata, but not the 5.1-million-reference full archive. No public redistribution clearance is claimed.

| Component | Known public terms | Work remaining before public deployment |
|---|---|---|
| HPWREN FIgLib / archived imagery | Archived data >24h under **CC BY-NC 4.0** with credit and FIgLib publication citation; real-time data has separate restrictions, including automatic retrieval and embedding | Verify actual use, archive age, official data attribution, noncommercial status/permissions. Do not assume approval for real-time integrations |
| PhenoCam | PhenoCam Network Fair Use Data Policy (2024) states **CC BY 4.0** with source acknowledgement | Credit network and any site-level requirements for used imagery |
| UAF GI Optics | Public pages demonstrate access; a definitive redistribution license was **not established** | Review UAF rights before releasing metadata packs or mirroring clips |
| NIMS / USGS | Media provided by USGS, site-specific rights and data provenance not audited here | Review the relevant USGS media and data terms |
| OSU | Provider-hosted videos; redistribution terms not established in this review | Review OSU terms for clips and bulk metadata distribution |
| Leaflet | **BSD-2-Clause**; linked from CDN rather than vendored | Retain notices/credits if redistributing code |
| hls.js | **Apache-2.0**; loaded dynamically from CDN, not vendored | Preserve dependency attribution |
| OpenStreetMap tiles | Tiles are subject to the OSMF tile policy (not identical to ODbL map data license) | Visible attribution, valid referrer/caching, no bulk tile downloads; reassess production scale |

Official sources:
- HPWREN: https://www.hpwren.ucsd.edu/cc.html
- PhenoCam: https://zenodo.org/records/14854980/files/Fair-use_Statement.pdf?download=1
- Leaflet license: https://github.com/Leaflet/Leaflet/blob/main/LICENSE
- hls.js package: https://github.com/video-dev/hls.js/blob/master/package.json
- OSM tile policy: https://operations.osmfoundation.org/policies/tiles/
- GitHub license guidance: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository

## Attribution and merged-source audit

The 2.46 MB `index.html` inlines project modules into one script and links external Leaflet CSS and optional hls.js assets. An automated string search did not establish authorship, provenance, or licensing of **every** merged segment. Audit upstream origins and preserve relevant notices before selecting a public project license. The viewer's existing on-map provider credits must remain visible.

Not included: the full 5.1M URL-reference shard set, downloaded media, collector, budgets, and journals. Included for *private testing*: a 12-camera sample index with its shards, the 622-record catalog-only index, HPWREN event leads and sample frames, and UAF video leads. These provider datasets are **not** covered by any future project software `LICENSE`. Read `DATA_DISTRIBUTION_REVIEW.md` before any public upload or hosting.
