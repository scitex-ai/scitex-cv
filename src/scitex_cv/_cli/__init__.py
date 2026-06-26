#!/usr/bin/env python3
"""Minimal command-line interface for scitex-cv.

Exposes the ecosystem-uniform ``scitex-cv dev system-deps {list,install}``
verb so the container build can ask each leaf for its OS-level apt
dependencies (see :mod:`scitex_cv._system_deps`). Kept intentionally
small — scitex-cv is a library first; this CLI exists for the dev/build
control plane, not end-user image processing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from typing import List, Optional

from .. import __version__
from .._system_deps import apt_deps, apt_packages


def _cmd_system_deps(args: argparse.Namespace) -> int:
    if args.system_deps_action == "install":
        return _install_apt(apt_packages(), assume_yes=args.yes)
    # default / "list": native apt list — one package name per line so the
    # output pipes straight into `xargs apt-get install`.
    if args.verbose:
        for dep in apt_deps():
            print(f"{dep.package}\t{dep.purpose}")
    else:
        for pkg in apt_packages():
            print(pkg)
    return 0


def _install_apt(packages: List[str], *, assume_yes: bool) -> int:
    if not packages:
        return 0
    apt_get = shutil.which("apt-get")
    if apt_get is None:
        print(
            "scitex-cv: apt-get not found; cannot install system deps "
            "(this is a Debian/Ubuntu build-time action).",
            file=sys.stderr,
        )
        return 1
    cmd = [apt_get, "install", "--no-install-recommends"]
    if assume_yes:
        cmd.append("-y")
    cmd.extend(packages)
    print("scitex-cv: " + " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scitex-cv",
        description="scitex-cv developer/build CLI.",
    )
    parser.add_argument(
        "--version", action="version", version=f"scitex-cv {__version__}"
    )
    sub = parser.add_subparsers(dest="group", required=True)

    dev = sub.add_parser("dev", help="Developer / build control-plane verbs.")
    dev_sub = dev.add_subparsers(dest="dev_command", required=True)

    sysdeps = dev_sub.add_parser(
        "system-deps",
        help="Show or install scitex-cv's OS-level apt dependencies.",
    )
    sysdeps.add_argument(
        "system_deps_action",
        nargs="?",
        choices=["list", "install"],
        default="list",
        help="list (default): print apt package names; install: apt-get them.",
    )
    sysdeps.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="With 'list': also print each package's purpose (TSV).",
    )
    sysdeps.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="With 'install': pass -y to apt-get (non-interactive).",
    )
    sysdeps.set_defaults(func=_cmd_system_deps)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

# EOF
