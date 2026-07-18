#!/usr/bin/env python3
# Timestamp: 2026-07-18
# File: src/scitex_cv/_ocr.py
"""Optical character recognition (image -> text) using EasyOCR.

OCR is a natural CV primitive: it maps an image (a file path or a cv2/numpy
array) to recognized text. The heavy engine (EasyOCR, which pulls in torch)
is imported **lazily inside** :func:`ocr` so that ``import scitex_cv`` stays
light and free of the optional dependency.

PDF handling deliberately lives elsewhere (scitex-io owns PDF -> image);
this module only ever sees images, keeping separation of concerns clean.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Sequence, Tuple, Union

import numpy as np

_OCR_EXTRA_HINT = (
    "EasyOCR is required for scitex_cv.ocr but is not installed. "
    "Install it with the 'ocr' extra: pip install 'scitex-cv[ocr]'"
)


@lru_cache(maxsize=None)
def _get_reader(languages: Tuple[str, ...]):
    """Build and cache an EasyOCR ``Reader`` for a language set.

    The reader is cached per language tuple because model load is slow.
    EasyOCR is imported here (never at module top) so that torch is only
    pulled in when OCR is actually requested.
    """
    easyocr = _import_easyocr()
    return easyocr.Reader(list(languages))


def _import_easyocr():
    """Import easyocr lazily, raising an actionable error when absent."""
    try:
        import easyocr
    except ImportError as exc:  # dependency genuinely absent
        raise ImportError(_OCR_EXTRA_HINT) from exc
    return easyocr


def ocr(
    image: Union[str, Path, np.ndarray],
    languages: Sequence[str] = ("ja", "en"),
    detail: bool = False,
) -> Union[str, List[Tuple]]:
    """Recognize text in an image.

    Parameters
    ----------
    image : str, Path, or np.ndarray
        A path to an image file, or an in-memory image array. Arrays may be
        BGR (cv2's native order, as produced by :func:`scitex_cv.load`) or
        RGB / grayscale — EasyOCR handles any of these numpy inputs directly.
    languages : sequence of str
        Language codes to recognize (EasyOCR codes, e.g. ``"en"``, ``"ja"``).
        Defaults to Japanese + English. The set is used as the cache key for
        the underlying model, so the same tuple reuses one loaded ``Reader``.
    detail : bool
        If False (default), return the recognized text pieces concatenated
        into a single string. If True, return the raw list of
        ``(bbox, text, confidence)`` tuples EasyOCR yields.

    Returns
    -------
    str or list
        Concatenated recognized text (``detail=False``) or the list of
        ``(bbox, text, confidence)`` tuples (``detail=True``).

    Raises
    ------
    TypeError
        If ``image`` is neither a path-like nor a numpy array.
    ImportError
        If EasyOCR is not installed (install ``scitex-cv[ocr]``).
    """
    if isinstance(image, np.ndarray):
        target: Union[str, np.ndarray] = image
    elif isinstance(image, (str, Path)):
        target = str(image)
    else:
        raise TypeError(
            "ocr(image): image must be a file path (str/Path) or a numpy "
            f"array, got {type(image).__name__}"
        )

    reader = _get_reader(tuple(languages))
    results = reader.readtext(target)

    if detail:
        return results
    return " ".join(text for _bbox, text, _conf in results)


__all__ = ["ocr"]

# EOF
