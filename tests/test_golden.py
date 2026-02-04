from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from lsystem.core import expand
from lsystem.presets import get_preset, list_presets
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


def canonical_segments_json(normalized: list[dict[str, list[float]]]) -> str:
    # Canonical: sorted keys, minimal whitespace, UTF-8
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _paths_for(golden_dir: Path, preset: str) -> tuple[Path, Path, Path]:
    seg_path = golden_dir / f"{preset}_segments.json"
    svg_path = golden_dir / f"{preset}.svg"
    sha_path = golden_dir / f"{preset}_segments.sha256"
    return seg_path, svg_path, sha_path


def _generate_for_preset(preset_name: str) -> tuple[list[dict[str, list[float]]], str, str]:
    preset = get_preset(preset_name)
    instructions = expand(preset.system, preset.iterations)
    segments = interpret(instructions, angle=preset.angle, step=preset.step)
    normalized = normalize_segments(segments)
    canonical = canonical_segments_json(normalized)
    svg = render_svg(segments)
    digest = sha256_hex(canonical)
    return normalized, svg, digest


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_or_compare(path: Path, content: str, update_golden: bool) -> None:
    if update_golden or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return
    assert path.read_text(encoding="utf-8") == content


def _ensure_or_compare_json(path: Path, data: object, update_golden: bool) -> None:
    content = json.dumps(data, indent=2, sort_keys=True) + "\n"
    _ensure_or_compare(path, content, update_golden=update_golden)


@pytest.mark.parametrize("preset_name", ["fern", "bush", "weed"])
def test_segments_match_golden(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    normalized, _svg, _digest = _generate_for_preset(preset_name)
    seg_path, _svg_path, _sha_path = _paths_for(golden_dir, preset_name)

    _ensure_or_compare_json(seg_path, normalized, update_golden=update_golden)

    if not update_golden and seg_path.exists():
        assert _read_json(seg_path) == normalized


@pytest.mark.parametrize("preset_name", ["fern", "bush", "weed"])
def test_svg_file_created_and_non_empty(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    _normalized, svg, _digest = _generate_for_preset(preset_name)
    _seg_path, svg_path, _sha_path = _paths_for(golden_dir, preset_name)

    _ensure_or_compare(svg_path, svg, update_golden=update_golden)
    assert svg_path.exists()
    assert svg_path.stat().st_size > 0


@pytest.mark.parametrize("preset_name", ["fern", "bush", "weed"])
def test_golden_hash_matches(preset_name: str, golden_dir: Path, update_golden: bool) -> None:
    normalized, _svg, digest = _generate_for_preset(preset_name)
    _seg_path, _svg_path, sha_path = _paths_for(golden_dir, preset_name)

    canonical = canonical_segments_json(normalized)
    computed = sha256_hex(canonical)
    assert computed == digest  # self-consistency

    _ensure_or_compare(sha_path, digest + "\n", update_golden=update_golden)

    if not update_golden and sha_path.exists():
        assert sha_path.read_text(encoding="utf-8").strip() == digest


def test_all_presets_have_golden_files(golden_dir: Path) -> None:
    # Ensure the golden strategy covers the full preset catalog.
    for name in list_presets():
        seg_path, svg_path, sha_path = _paths_for(golden_dir, name)
        assert seg_path.name.endswith("_segments.json")
        assert svg_path.name.endswith(".svg")
        assert sha_path.name.endswith("_segments.sha256")
