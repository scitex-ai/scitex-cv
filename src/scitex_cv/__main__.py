#!/usr/bin/env python3
"""``python -m scitex_cv`` entry point — delegates to the CLI."""

from ._cli import main

if __name__ == "__main__":
    raise SystemExit(main())

# EOF
