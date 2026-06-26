#!/usr/bin/env python3
"""Runtime gate for scitex-cv's cross-package imports.

``scitex_cv._system_deps.provide()`` imports ``scitex_dev.system_deps``
lazily (so the package stays importable without scitex-dev). This gate
exercises that cross-package contract at test time, catching a broken or
renamed ``SystemDepSpec`` before it reaches the container build. Skipped
where scitex-dev is not installed.
"""

import pytest

#: Every cross-package (`scitex_*`) module that scitex-cv's source imports.
#: The PS-140 audit gate compares this against the imports it finds in
#: ``src/`` and fails on drift — keep it in sync when adding/removing
#: cross-package imports.
CROSS_PACKAGE_IMPORTS = ["scitex_dev.system_deps"]

_EXPECTED_PACKAGES = ["libxcb1", "libgl1", "libglib2.0-0"]


def test_scitex_dev_system_deps_is_importable():
    # Arrange
    pytest.importorskip("scitex_dev.system_deps")
    # Act
    import scitex_dev.system_deps as system_deps
    # Assert
    assert hasattr(system_deps, "SystemDepSpec")


def test_system_deps_provider_resolves_scitex_dev_spec():
    # Arrange
    pytest.importorskip("scitex_dev.system_deps")
    from scitex_cv._system_deps import provide

    # Act
    packages = [spec.package for spec in provide()]
    # Assert
    assert packages == _EXPECTED_PACKAGES

# EOF
