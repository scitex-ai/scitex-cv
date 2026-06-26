#!/usr/bin/env python3
"""OS-level (apt) system dependencies for scitex-cv.

scitex-cv is the single source of truth for the native shared libraries
its cv2 (``opencv-python``) backend needs at the OS level. Historically
these were hardcoded in sac's ``apptainer-scitex.def``; this module makes
scitex-cv own them so the container build can discover them through the
``scitex_dev.system_deps`` ecosystem entry-point group.

Decoupling
----------
The apt-dep list lives here as a plain local table (:data:`_APT_DEPS`) so
the ``scitex-cv dev system-deps`` CLI can read it with **no** dependency
on scitex-dev. The entry-point provider (:func:`provide`) adapts that
table into real ``scitex_dev.system_deps.SystemDepSpec`` instances, and
imports the spec class **lazily** — it is only ever called inside
scitex-dev's aggregator, where scitex-dev is installed. Importing
``scitex_cv._system_deps`` therefore never requires scitex-dev.
"""

from __future__ import annotations

from typing import List, NamedTuple, Optional

#: Owning leaf package — used as ``SystemDepSpec.provider`` so the
#: aggregator's ``--provider`` filter can select scitex-cv's deps.
PROVIDER = "scitex-cv"


class AptDep(NamedTuple):
    """A single OS-level apt dependency (scitex-cv-local representation)."""

    package: str
    purpose: str
    apt_repo: Optional[str] = None


#: cv2 (opencv-python) loads these shared objects at import time. Without
#: them ``import scitex`` -> ``scitex_cv`` -> ``cv2`` raises e.g.
#: ``ImportError: libGL.so.1: cannot open shared object file`` (the silent
#: cv2 import-fallback the container build is meant to prevent).
_APT_DEPS: List[AptDep] = [
    AptDep(
        "libxcb1",
        "cv2 runtime: provides libxcb.so.1 (X C Binding) — without it "
        "`import scitex_cv` -> cv2 raises 'libxcb.so.1: cannot open "
        "shared object file'",
    ),
    AptDep(
        "libgl1",
        "cv2 runtime: provides libGL.so.1 (OpenGL) required by "
        "opencv-python's image ops",
    ),
    AptDep(
        "libglib2.0-0",
        "cv2 runtime: provides libgthread-2.0.so.0 / libglib-2.0.so.0 "
        "(GLib) linked by opencv-python",
    ),
]


def apt_deps() -> List[AptDep]:
    """Return scitex-cv's OS-level apt dependencies (local representation)."""
    return list(_APT_DEPS)


def apt_packages() -> List[str]:
    """Return just the apt package names, in declaration order."""
    return [dep.package for dep in _APT_DEPS]


def provide() -> "List":
    """Entry-point for the ``scitex_dev.system_deps`` group.

    Returns a list of ``scitex_dev.system_deps.SystemDepSpec``. The spec
    class is imported lazily so this module stays importable without
    scitex-dev; the aggregator that calls this always runs with
    scitex-dev installed.
    """
    from scitex_dev.system_deps import SystemDepSpec

    return [
        SystemDepSpec(
            package=dep.package,
            purpose=dep.purpose,
            provider=PROVIDER,
            apt_repo=dep.apt_repo,
        )
        for dep in _APT_DEPS
    ]


__all__ = ["AptDep", "PROVIDER", "apt_deps", "apt_packages", "provide"]

# EOF
