#!/usr/bin/env python3
"""Tests for scitex_cv._cli (the `dev system-deps` verb group)."""

import pytest

import scitex_cv._cli as cli
from scitex_cv._cli import main

_EXPECTED_PACKAGES = ["libxcb1", "libgl1", "libglib2.0-0"]


def _must_not_run(*_args, **_kwargs):  # pragma: no cover - guard
    raise AssertionError("apt-get must not run during a dry-run")


class TestSystemDepsList:
    def test_list_prints_apt_packages_one_per_line(self, capsys):
        # Arrange
        argv = ["dev", "system-deps", "list"]
        # Act
        main(argv)
        # Assert
        assert capsys.readouterr().out.splitlines() == _EXPECTED_PACKAGES

    def test_list_exits_zero(self, capsys):
        # Arrange
        argv = ["dev", "system-deps", "list"]
        # Act
        rc = main(argv)
        # Assert
        assert rc == 0

    def test_list_is_the_default_action(self, capsys):
        # Arrange
        argv = ["dev", "system-deps"]
        # Act
        main(argv)
        # Assert
        assert capsys.readouterr().out.splitlines() == _EXPECTED_PACKAGES

    def test_verbose_list_keeps_package_names_in_first_column(self, capsys):
        # Arrange
        main(["dev", "system-deps", "list", "--verbose"])
        # Act
        names = [
            line.split("\t", 1)[0]
            for line in capsys.readouterr().out.splitlines()
        ]
        # Assert
        assert names == _EXPECTED_PACKAGES

    def test_verbose_list_includes_a_purpose_column(self, capsys):
        # Arrange
        main(["dev", "system-deps", "list", "--verbose"])
        # Act
        purposes = [
            line.split("\t", 1)[1]
            for line in capsys.readouterr().out.splitlines()
        ]
        # Assert
        assert all(p.strip() for p in purposes)


class TestSystemDepsInstall:
    def test_install_defaults_to_dry_run_marker(self, capsys):
        # Arrange
        argv = ["dev", "system-deps", "install"]
        # Act
        main(argv)
        # Assert
        assert "[dry-run]" in capsys.readouterr().out

    def test_install_dry_run_lists_every_package(self, capsys):
        # Arrange
        main(["dev", "system-deps", "install"])
        # Act
        out = capsys.readouterr().out
        # Assert
        assert all(pkg in out for pkg in _EXPECTED_PACKAGES)

    def test_install_dry_run_exits_zero(self, capsys):
        # Arrange
        argv = ["dev", "system-deps", "install"]
        # Act
        rc = main(argv)
        # Assert
        assert rc == 0

    def test_dry_run_flag_overrides_yes(self, monkeypatch):
        # Arrange
        monkeypatch.setattr(cli.subprocess, "call", _must_not_run)
        # Act
        rc = main(["dev", "system-deps", "install", "--yes", "--dry-run"])
        # Assert
        assert rc == 0

    def test_install_yes_without_apt_get_exits_one(self, monkeypatch, capsys):
        # Arrange
        monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
        # Act
        rc = main(["dev", "system-deps", "install", "--yes"])
        # Assert
        assert rc == 1

    def test_install_yes_without_apt_get_warns_on_stderr(
        self, monkeypatch, capsys
    ):
        # Arrange
        monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
        # Act
        main(["dev", "system-deps", "install", "--yes"])
        # Assert
        assert "apt-get not found" in capsys.readouterr().err


class TestCliErrors:
    def test_no_subcommand_exits(self):
        # Arrange
        argv = []
        # Act
        ctx = pytest.raises(SystemExit)
        # Assert
        with ctx:
            main(argv)

    def test_unknown_system_deps_action_rejected(self):
        # Arrange
        argv = ["dev", "system-deps", "frobnicate"]
        # Act
        ctx = pytest.raises(SystemExit)
        # Assert
        with ctx:
            main(argv)

    def test_version_flag_exits_zero(self):
        # Arrange
        code = None
        # Act
        try:
            main(["--version"])
        except SystemExit as exc:
            code = exc.code
        # Assert
        assert code == 0

# EOF
