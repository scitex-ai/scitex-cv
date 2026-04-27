"""Quickstart for scitex_cv.

Generates a synthetic image, applies a few transforms, and round-trips
through `save` / `load`.
"""

import tempfile
from pathlib import Path

import numpy as np

import scitex_cv as scv


def main() -> int:
    # Synthetic 200x300 RGB gradient
    yy, xx = np.mgrid[0:200, 0:300].astype(np.float32)
    img = np.stack(
        [xx / xx.max() * 255, yy / yy.max() * 255, ((xx + yy) % 256)], axis=-1
    ).astype(np.uint8)
    print(f"input shape={img.shape} dtype={img.dtype}")

    # Resize to half, draw a green rectangle, then convert to grayscale.
    small = scv.resize(img, scale=0.5)
    boxed = scv.rectangle(
        small.copy(), pt1=(20, 20), pt2=(120, 80), color=(0, 255, 0), thickness=3
    )
    gray = scv.to_gray(boxed)
    print(f"resized -> {small.shape}, gray -> {gray.shape}")

    # Round-trip through disk
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "demo.png"
        scv.save(boxed, out)
        loaded = scv.load(out)
        print(
            f"saved {out.name} ({out.stat().st_size} bytes); reload shape={loaded.shape}"
        )
        assert loaded.shape == boxed.shape

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
