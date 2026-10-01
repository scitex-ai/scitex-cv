"""Smoke: ``blur`` roundtrips an array in a subprocess (PS-211).

Subprocess-driven (``sys.executable -c ...``) so this proves the
installed package resolves its hard dependencies — an in-process call
would not. Hermetic: numpy + opencv are hard deps, no network, no
credentials, no writes outside tmp dirs.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.smoke

CODE = "\n".join(
    [
        "import numpy as np",
        "import scitex_cv as cv",
        "img = np.zeros((10, 10, 3), dtype=np.uint8)",
        "out = cv.blur(img, ksize=3)",
        "print(tuple(out.shape))",
    ]
)


def test_blur_roundtrip_in_subprocess() -> None:
    # Arrange
    argv = [sys.executable, "-c", CODE]

    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)

    # Assert
    assert (completed.returncode, completed.stdout.strip()) == (0, "(10, 10, 3)")
