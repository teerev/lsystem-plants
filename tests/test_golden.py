from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from lsystem.core import expand
from lsystem.presets import get_preset
from lsystem.render_svg import render_svg
from lsystem.turtle import Segment, interpret


def normalize_segments(segments: list[Segment]) -> list[dict[str, list[float]]]:
    return [
        {
            "start": [round(s.start[0], 2), round(s.start[1], 2)],
            "end": [round(s.end[0], 2), round(s.end[1], 2)],
        }
        for s in segments
    ]


def _canonical_segments_json(normalized: list[dict[str, list[float]]]) -> str:
    # Stable serialization for hashing/comparison.
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, obj: Any) -> None:
    _ensure_parent(path)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    _ensure_parent(path)
    path.write_text(text, encoding="utf-8")


def _generate_for_preset(preset_name: str) -> tuple[list[dict[str, list[float]]], str, str]:
    preset = get_preset(preset_name)
    expanded = expand(preset.system, preset.iterations)
    segments = interpret(expanded, angle=preset.angle, step=preset.step)
    normalized = normalize_segments(segments)
    canonical = _canonical_segments_json(normalized)
    seg_hash = _sha256_text(canonical)
    svg = render_svg(segments)
    return normalized, seg_hash, svg


def _compare_or_update_json(path: Path, actual_obj: Any, *, update: bool) -> Any:
    if update or not path.exists():
        _write_json(path, actual_obj)
        return actual_obj
    expected = _read_json(path)
    assert actual_obj == expected
    return expected


def _compare_or_update_text(path: Path, actual_text: str, *, update: bool) -> str:
    if update or not path.exists():
        _write_text(path, actual_text)
        return actual_text
    expected = path.read_text(encoding="utf-8")
    assert actual_text == expected
    return expected


@pytest.mark.parametrize("preset_name", ["weed", "fern", "bush"])
def test_preset_segments_match_golden(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    normalized, seg_hash, _svg = _generate_for_preset(preset_name)

    seg_path = golden_dir / f"{preset_name}_segments.json"
    hash_path = golden_dir / f"{preset_name}_segments.sha256"

    _compare_or_update_json(seg_path, normalized, update=update_golden)
    _compare_or_update_text(hash_path, seg_hash + "\n", update=update_golden)


@pytest.mark.parametrize("preset_name", ["weed", "fern", "bush"])
def test_preset_svg_is_created_and_non_empty(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    _normalized, _seg_hash, svg = _generate_for_preset(preset_name)

    svg_path = golden_dir / f"{preset_name}.svg"
    saved = _compare_or_update_text(svg_path, svg, update=update_golden)

    assert isinstance(saved, str)
    assert saved.strip().startswith("<svg")
    assert "<line" in saved or "</svg>" in saved
    assert len(saved.strip()) > 20


@pytest.mark.parametrize("preset_name", ["weed", "fern", "bush"])
def test_golden_hash_matches_canonical_json(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    normalized, seg_hash, _svg = _generate_for_preset(preset_name)
    canonical = _canonical_segments_json(normalized)
    expected_hash = _sha256_text(canonical) + "\n"

    hash_path = golden_dir / f"{preset_name}_segments.sha256"

    if update_golden or not hash_path.exists():
        _write_text(hash_path, expected_hash)
    else:
        assert hash_path.read_text(encoding="utf-8") == expected_hash

    assert seg_hash + "\n" == expected_hash
