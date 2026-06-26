#!/usr/bin/env python3
"""Tests for scitex_cv._system_deps (apt-dep SSoT + ecosystem provider)."""

import pytest

from scitex_cv import _system_deps

_EXPECTED_PACKAGES = ["libxcb1", "libgl1", "libglib2.0-0"]


def _system_deps_installed() -> bool:
    """True iff scitex_dev.system_deps is importable.

    ``find_spec`` raises ``ModuleNotFoundError`` (not returns None) when
    the *parent* package ``scitex_dev`` is absent, so guard for it.
    """
    import importlib.util

    try:
        return importlib.util.find_spec("scitex_dev.system_deps") is not None
    except ModuleNotFoundError:
        return False


class TestAptDataLayer:
    def test_apt_packages_are_the_cv2_runtime_libs(self):
        # Arrange
        expected = _EXPECTED_PACKAGES
        # Act
        actual = _system_deps.apt_packages()
        # Assert
        assert actual == expected

    def test_every_dep_has_a_nonempty_purpose(self):
        # Arrange
        deps = _system_deps.apt_deps()
        # Act
        purposes = [dep.purpose for dep in deps]
        # Assert
        assert all(p.strip() for p in purposes)

    def test_apt_deps_default_apt_repo_is_none(self):
        # Arrange
        deps = _system_deps.apt_deps()
        # Act
        repos = [dep.apt_repo for dep in deps]
        # Assert
        assert repos == [None] * len(_EXPECTED_PACKAGES)

    def test_apt_deps_returns_a_copy_not_the_internal_list(self):
        # Arrange
        first = _system_deps.apt_deps()
        # Act
        first.clear()
        # Assert
        assert _system_deps.apt_packages() == _EXPECTED_PACKAGES

    def test_provider_name_is_the_owning_leaf(self):
        # Arrange
        expected = "scitex-cv"
        # Act
        actual = _system_deps.PROVIDER
        # Assert
        assert actual == expected

    def test_module_imports_without_scitex_dev(self):
        # Arrange
        module = _system_deps
        # Act
        has_provide = hasattr(module, "provide")
        # Assert
        assert has_provide


class TestProviderEntryPoint:
    """provide() returns real SystemDepSpec objects once the keystone
    (scitex_dev.system_deps) is installed; skipped until then."""

    def test_provide_packages_match_the_data_layer(self):
        # Arrange
        pytest.importorskip("scitex_dev.system_deps")
        # Act
        packages = [spec.package for spec in _system_deps.provide()]
        # Assert
        assert packages == _EXPECTED_PACKAGES

    def test_provide_sets_provider_to_scitex_cv(self):
        # Arrange
        pytest.importorskip("scitex_dev.system_deps")
        # Act
        providers = {spec.provider for spec in _system_deps.provide()}
        # Assert
        assert providers == {"scitex-cv"}

    @pytest.mark.skipif(
        _system_deps_installed(),
        reason="scitex_dev.system_deps is installed",
    )
    def test_provide_raises_cleanly_when_scitex_dev_absent(self):
        # Arrange
        ctx = pytest.raises(ImportError)
        # Act
        call = _system_deps.provide
        # Assert
        with ctx:
            call()

# EOF
