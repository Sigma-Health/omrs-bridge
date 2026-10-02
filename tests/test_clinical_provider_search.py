"""Unit tests for clinical provider name search helpers."""

from app.crud.provider import build_like_pattern, escape_like_pattern


def test_escape_like_pattern_escapes_wildcards():
    assert escape_like_pattern("100%") == "100\\%"
    assert escape_like_pattern("a_b") == "a\\_b"


def test_build_like_pattern_wraps_substring():
    assert build_like_pattern("na") == "%na%"
    assert build_like_pattern("  Annah  ") == "%Annah%"


def test_build_like_pattern_preserves_escaped_wildcards():
    assert build_like_pattern("na%") == "%na\\%%"
