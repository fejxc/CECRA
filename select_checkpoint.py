#!/usr/bin/env python3
"""Select a checkpoint from six dev128 MAP points; never read test metrics."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def select(curve: dict, config: dict) -> dict:
    if curve.get("split") != "dev128":
        raise ValueError("checkpoint selection requires dev128, never test160")
    if curve.get("epochs") != config["epochs"] or config["epochs"] != 10:
        raise ValueError("expected the prespecified 10-epoch schedule")
    method = curve.get("method")
    if method not in config["checkpoint_steps"]:
        raise ValueError("unknown method")
    seed = curve.get("seed")
    if seed not in config["seeds"]:
        raise ValueError("unknown seed")
    points = curve.get("points")
    expected = config["checkpoint_steps"][method]
    if not isinstance(points, list) or len(points) != 6:
        raise ValueError("exactly six dev checkpoint opportunities are required")
    steps = [point.get("step") for point in points]
    if steps != expected:
        raise ValueError("dev checkpoint steps differ from frozen configuration")
    maps = [float(point["MAP"]) for point in points]
    if not all(math.isfinite(value) and 0 <= value <= 1 for value in maps):
        raise ValueError("MAP must be finite and within [0,1]")
    best = max(range(6), key=lambda index: (maps[index], -steps[index]))
    return {
        "method": method,
        "seed": seed,
        "selection_split": "dev128",
        "selection_metric": "MAP",
        "selected_step": steps[best],
        "selected_dev_MAP": maps[best],
        "opportunities": 6,
        "epochs": 10,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--curve", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "configs/revised_protocol.json")
    args = parser.parse_args()
    curve = json.loads(args.curve.read_text(encoding="utf-8"))
    config = json.loads(args.config.read_text(encoding="utf-8"))
    print(json.dumps(select(curve, config), indent=2))


if __name__ == "__main__":
    main()
