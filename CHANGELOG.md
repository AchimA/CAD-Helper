# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.7.0] - 2025-11-20
### Added
- External `colormaps.json` with dynamic loading and caching.
- Procedural colormaps: `jet`, `turbo`, `cubehelix` retained as algorithmic fallbacks.
- Scene property `cad_vis_colormap` with live recolor update on change.
- Always-visible percentile filter (min/max) with real-time selection updates.

### Changed
- Visualization panel made more compact; filter operators replaced by live sliders.
- Alpha defaults (min/max) standardized to 0.5 and reset per visualization.
- Colormap enumeration now constructed dynamically from JSON + procedural set.

### Removed
- Legacy separate selection filter operators (now integrated into visualization workflow).
- Inline static colormap stop definitions (moved to external JSON).

### Maintenance
- Improved fallback behavior if JSON missing (procedural maps still function).
- Scene property cleanup ensured on unregister.

---
Format: Keep latest release at top. Use semantic versioning.
