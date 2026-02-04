from __future__ import annotations

import hashlib
import json

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
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_expansion_determinism_10x() -> None:
    preset = get_preset("fern")

    baseline = expand(preset.system, preset.iterations)
    for _ in range(10):
        assert expand(preset.system, preset.iterations) == baseline


def test_full_pipeline_determinism_10x() -> None:
    preset = get_preset("bush")

    expanded0 = expand(preset.system, preset.iterations)
    seg0 = interpret(expanded0, angle=preset.angle, step=preset.step)
    norm0 = normalize_segments(seg0)
    canon0 = _canonical_segments_json(norm0)
    hash0 = _sha256_text(canon0)
    svg0 = render_svg(seg0)

    for _ in range(10):
        expanded = expand(preset.system, preset.iterations)
        seg = interpret(expanded, angle=preset.angle, step=preset.step)
        norm = normalize_segments(seg)
        canon = _canonical_segments_json(norm)
        h = _sha256_text(canon)
        svg = render_svg(seg)

        assert expanded == expanded0
        assert norm == norm0
        assert h == hash0
        assert svg == svg0
