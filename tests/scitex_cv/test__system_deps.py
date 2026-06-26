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
        assert _system_deps.apt_packages() == _EXPECTED_PACKAGES

    def test_every_dep_has_a_nonempty_purpose(self):
        assert all(dep.purpose.strip() for dep in _system_deps.apt_deps())

    def test_apt_deps_default_apt_repo_is_none(self):
        assert all(dep.apt_repo is None for dep in _system_deps.apt_deps())

    def test_apt_deps_returns_a_copy_not_internal_list(self):
        first = _system_deps.apt_deps()
        first.clear()
        assert _system_deps.apt_packages() == _EXPECTED_PACKAGES

    def test_provider_name_is_the_owning_leaf(self):
        assert _system_deps.PROVIDER == "scitex-cv"

    def test_module_imports_without_scitex_dev(self):
        # Importing this module must never require scitex-dev — the spec
        # import in provide() is lazy. The import at module top proves it.
        assert hasattr(_system_deps, "provide")


class TestProviderEntryPoint:
    """provide() returns real SystemDepSpec objects once the keystone
    (scitex_dev.system_deps) is installed; skipped until then."""

    def test_provide_returns_specs_matching_the_data_layer(self):
        pytest.importorskip("scitex_dev.system_deps")
        specs = _system_deps.provide()
        assert [s.package for s in specs] == _EXPECTED_PACKAGES
        assert all(s.provider == "scitex-cv" for s in specs)

    def test_provide_raises_cleanly_when_scitex_dev_absent(self):
        if _system_deps_installed():
            pytest.skip("scitex_dev.system_deps is installed")
        with pytest.raises(ImportError):
            _system_deps.provide()
