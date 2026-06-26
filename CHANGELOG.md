# Changelog

All notable changes to `scitex-cv` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] — 2026-06-27

- **BREAKING(deps): switch `opencv-python` → `opencv-python-headless`.** The headless wheel is self-contained (bundles ffmpeg/libpng/openblas/…) and pulls in no X11/OpenGL/GLib system libraries, so scitex-cv installs and imports on a minimal/headless base with **no apt packages required**. scitex-cv uses no GUI cv2 (`imshow` etc.); if you need it, install `opencv-python` yourself.
- feat(system-deps): register a `scitex_dev.system_deps` provider so the SciTeX container build discovers scitex-cv's OS-level needs via the ecosystem aggregator instead of hardcoding them. With headless OpenCV the verified apt set is **empty**, so the provider returns no packages (earlier dev revisions declared `libxcb1`/`libgl1`/`libglib2.0-0` for full opencv-python; headless drops all three).
- perf(import): defer the cv2 import — `import scitex_cv` (and the system-deps provider module) no longer pulls in cv2 at package load (PEP 562 lazy attributes); public functions import cv2 on first use, unchanged.
- test(integration): add a lazy-import gate proving the package and the provider module import without cv2.

## [0.1.5] — 2026-05-26

- test(quality): rewrite tests for PA-307 TQ001/002/003/007 conformance
- ci(codecov): disable PR comments to stop email noise
- ci(quality): replace broken ecosystem-clone template with single-package audit-all
- ci(docs): make sphinx_html commit-back step non-fatal
- docs(sphinx_html): refresh from CI build

## [0.1.4] — 2026-05-19

- quality: subprocess coverage wiring + [dev] completeness
- fix(workflows): resync integrated release pipeline from scitex-dev v0.11.20
- fix(workflows): standardize to scitex-dev canonical set
- ci(release): sync publish-pypi.yml fix
- ci: sync GitHub Releases with PyPI publish
- ci: sync-main.yml — auto-FF main on v\* tag push
- chore(deps): bump scitex-dev pin floor to 0.11.7
- docs: add CHANGELOG.md + CONTRIBUTING.md
- docs(readme): add Architecture + Demo sections
- docs: add skills leaves per SK105-107 standard template
- docs: various documentation improvements

## [0.1.3] — 2025-11-15

- audit: clear all 11 audit warnings
- fix(release-safety): opt-in publish-pypi.yml (workflow_dispatch only)
- fix(skills): strip trailing `<!-- EOF -->` (SK211)
- fix(api): PA501/PA201/PA203 hygiene
- chore(version): switch `__version__` to importlib.metadata

## [0.1.2]

- Initial CHANGELOG entry — see git log for prior history.
