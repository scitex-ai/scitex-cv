#!/usr/bin/env python3
"""Tests for scitex_cv._cli (the `dev system-deps` verb group)."""

import pytest

from scitex_cv._cli import main

_EXPECTED_PACKAGES = ["libxcb1", "libgl1", "libglib2.0-0"]


class TestSystemDepsList:
    def test_list_prints_one_apt_package_per_line(self, capsys):
        rc = main(["dev", "system-deps", "list"])
        out = capsys.readouterr().out
        assert rc == 0
        assert out.splitlines() == _EXPECTED_PACKAGES

    def test_list_is_the_default_action(self, capsys):
        rc = main(["dev", "system-deps"])
        out = capsys.readouterr().out
        assert rc == 0
        assert out.splitlines() == _EXPECTED_PACKAGES

    def test_verbose_list_includes_purpose_as_tsv(self, capsys):
        rc = main(["dev", "system-deps", "list", "--verbose"])
        out = capsys.readouterr().out
        assert rc == 0
        lines = out.splitlines()
        assert len(lines) == len(_EXPECTED_PACKAGES)
        for line, pkg in zip(lines, _EXPECTED_PACKAGES):
            name, _, purpose = line.partition("\t")
            assert name == pkg
            assert purpose.strip()


class TestCliErrors:
    def test_no_subcommand_exits_nonzero(self):
        with pytest.raises(SystemExit) as exc:
            main([])
        assert exc.value.code != 0

    def test_unknown_system_deps_action_rejected(self):
        with pytest.raises(SystemExit) as exc:
            main(["dev", "system-deps", "frobnicate"])
        assert exc.value.code != 0

    def test_version_flag(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        assert "scitex-cv" in capsys.readouterr().out


class TestSystemDepsInstall:
    def test_install_without_apt_get_reports_error(self, monkeypatch, capsys):
        # On a non-Debian host (no apt-get) install must fail loudly, not
        # silently no-op. We point shutil.which at "missing" — this is a
        # real boundary (PATH lookup), not a mock of our own code.
        import scitex_cv._cli as cli

        monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
        rc = main(["dev", "system-deps", "install"])
        assert rc == 1
        assert "apt-get not found" in capsys.readouterr().err
