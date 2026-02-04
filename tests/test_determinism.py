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


def canonical_segments_json(normalized: list[dict[str, list[float]]]) -> str:
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_expansion_determinism_10x() -> None:
    preset = get_preset("fern")
    out0 = expand(preset.system, preset.iterations)
    for _ in range(10):
        assert expand(preset.system, preset.iterations) == out0


def test_full_pipeline_determinism_10x() -> None:
    preset = get_preset("bush")

    instructions0 = expand(preset.system, preset.iterations)
    segments0 = interpret(instructions0, angle=preset.angle, step=preset.step)
    norm0 = normalize_segments(segments0)
    canon0 = canonical_segments_json(norm0)
    digest0 = sha256_hex(canon0)
    svg0 = render_svg(segments0)

    for _ in range(10):
        instructions = expand(preset.system, preset.iterations)
        segments = interpret(instructions, angle=preset.angle, step=preset.step)
        norm = normalize_segments(segments)
        canon = canonical_segments_json(norm)
        digest = sha256_hex(canon)
        svg = render_svg(segments)

        assert instructions == instructions0
        assert norm == norm0
        assert digest == digest0
        assert svg == svg0
