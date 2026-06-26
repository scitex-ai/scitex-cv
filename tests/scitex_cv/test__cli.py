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
    def test_install_defaults_to_dry_run(self, capsys):
        # Default install must NOT touch apt — it prints the command only.
        rc = main(["dev", "system-deps", "install"])
        captured = capsys.readouterr()
        assert rc == 0
        assert "[dry-run]" in captured.out
        for pkg in _EXPECTED_PACKAGES:
            assert pkg in captured.out

    def test_dry_run_overrides_yes(self, monkeypatch, capsys):
        # Even with --yes, --dry-run keeps it safe: apt-get is never called.
        import scitex_cv._cli as cli

        def _boom(*_a, **_k):  # pragma: no cover - must not be reached
            raise AssertionError("subprocess.call must not run under --dry-run")

        monkeypatch.setattr(cli.subprocess, "call", _boom)
        rc = main(["dev", "system-deps", "install", "--yes", "--dry-run"])
        assert rc == 0
        assert "[dry-run]" in capsys.readouterr().out

    def test_install_yes_without_apt_get_reports_error(self, monkeypatch, capsys):
        # `--yes` on a non-Debian host (no apt-get) must fail loudly, not
        # silently no-op. Pointing shutil.which at "missing" exercises a
        # real boundary (PATH lookup), not a mock of our own logic.
        import scitex_cv._cli as cli

        monkeypatch.setattr(cli.shutil, "which", lambda _name: None)
        rc = main(["dev", "system-deps", "install", "--yes"])
        assert rc == 1
        assert "apt-get not found" in capsys.readouterr().err
