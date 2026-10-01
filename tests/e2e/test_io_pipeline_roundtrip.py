"""E2E: save → load → resize pipeline on a real PNG file (PS-212).

No network, no mocks — drives the real I/O + transform helpers end to
end against a real file in the pytest tmp dir. Gated on ``RUN_E2E=1``
so the default unit run stays fast.
"""

from __future__ import annotations

import os

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.skipif(os.environ.get("RUN_E2E") != "1", reason="RUN_E2E!=1")]


def test_save_load_resize_pipeline_roundtrip(tmp_path) -> None:
    import numpy as np

    import scitex_cv as cv

    # Arrange
    src = tmp_path / "input.png"
    dst = tmp_path / "output.png"
    cv.save(np.zeros((20, 20, 3), dtype=np.uint8), src)

    # Act
    img = cv.load(src)
    img = cv.resize(img, scale=0.5)
    saved = cv.save(img, dst)

    # Assert
    assert (tuple(img.shape), saved.exists()) == ((10, 10, 3), True)
