#!/usr/bin/env python3
"""Tests for scitex_cv._ocr (ocr image -> text).

Interface/dispatch tests run without the heavy engine. The real OCR path
(and anything that must build an EasyOCR ``Reader``) is gated behind
``easyocr`` actually being importable — no mocks, no monkeypatch (PA-306).
"""

import importlib.util

import numpy as np
import pytest

from scitex_cv._ocr import _get_reader, ocr

_EASYOCR = importlib.util.find_spec("easyocr") is not None
_needs_no_easyocr = pytest.mark.skipif(
    _EASYOCR, reason="easyocr installed — cannot exercise the missing-dep path"
)


@pytest.fixture(autouse=True)
def _clear_reader_cache():
    # Keep the lru_cache from leaking Reader instances across tests.
    _get_reader.cache_clear()
    yield
    _get_reader.cache_clear()


@pytest.fixture
def word_image():
    """A real white image with the known word 'HELLO' drawn on it."""
    img = np.full((80, 320, 3), 255, dtype=np.uint8)
    import cv2

    cv2.putText(
        img, "HELLO", (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 0), 4
    )
    return img


class TestDispatch:
    def test_integer_input_raises_type_error(self):
        # Arrange
        bad_input = 12345
        # Act
        ctx = pytest.raises(TypeError)
        # Assert
        with ctx:
            ocr(bad_input)

    def test_none_input_raises_type_error(self):
        # Arrange
        bad_input = None
        # Act
        ctx = pytest.raises(TypeError)
        # Assert
        with ctx:
            ocr(bad_input)

    def test_type_error_names_the_offending_type(self):
        # Arrange
        bad_input = [1, 2, 3]
        # Act
        ctx = pytest.raises(TypeError, match="list")
        # Assert
        with ctx:
            ocr(bad_input)


class TestMissingDependency:
    @_needs_no_easyocr
    def test_missing_easyocr_raises_actionable_import_error(self):
        # Arrange
        img = np.full((32, 64, 3), 255, dtype=np.uint8)
        # Act
        ctx = pytest.raises(ImportError, match=r"scitex-cv\[ocr\]")
        # Assert
        with ctx:
            ocr(img)


class TestReaderCache:
    def test_same_languages_return_identical_reader(self):
        # Arrange
        pytest.importorskip("easyocr")
        langs = ("en",)
        # Act
        first = _get_reader(langs)
        second = _get_reader(langs)
        # Assert
        assert first is second


class TestRealOcr:
    def test_recovers_known_word_from_drawn_image(self, word_image):
        # Arrange
        pytest.importorskip("easyocr")
        source = word_image
        # Act
        recognized = ocr(source, languages=("en",))
        # Assert
        assert "hello" in recognized.lower()

    def test_detail_true_returns_a_list(self, word_image):
        # Arrange
        pytest.importorskip("easyocr")
        source = word_image
        # Act
        recognized = ocr(source, languages=("en",), detail=True)
        # Assert
        assert isinstance(recognized, list)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])

# EOF
