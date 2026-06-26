#!/usr/bin/env python3
"""Runtime gate for scitex-cv's cross-package imports.

``scitex_cv._system_deps.provide()`` imports ``scitex_dev.system_deps``
lazily (so the package stays importable without scitex-dev). This gate
exercises that cross-package contract at test time, catching a broken or
renamed ``SystemDepSpec`` before it reaches the container build. Skipped
where scitex-dev is not installed.
"""

import pytest

_EXPECTED_PACKAGES = ["libxcb1", "libgl1", "libglib2.0-0"]


def test_system_deps_provider_resolves_scitex_dev_spec():
    # Arrange
    pytest.importorskip("scitex_dev.system_deps")
    from scitex_cv._system_deps import provide

    # Act
    packages = [spec.package for spec in provide()]
    # Assert
    assert packages == _EXPECTED_PACKAGES


def test_system_deps_provider_sets_provider_to_scitex_cv():
    # Arrange
    pytest.importorskip("scitex_dev.system_deps")
    from scitex_cv._system_deps import provide

    # Act
    providers = {spec.provider for spec in provide()}
    # Assert
    assert providers == {"scitex-cv"}

# EOF
