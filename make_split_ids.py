#!/usr/bin/env python3
"""Derive only query-ID manifests from authorized official LeCaRDv2 files."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ids_in_source_order(path: Path) -> list[str]:
    ids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        ids.append(str(row["id"]))
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate query IDs in source")
    return ids


def qid_key(qid: str) -> tuple[int, str]:
    try:
        return int(qid), qid
    except ValueError:
        return 0, qid


def split_ids(train_ids: list[str], test_ids: list[str], seed: int) -> dict[str, list[str]]:
    if len(train_ids) != 640 or len(test_ids) != 160:
        raise ValueError("expected official 640 train and 160 test queries")
    if len(set(train_ids + test_ids)) != 800:
        raise ValueError("train/test query IDs overlap or repeat")
    shuffled = list(train_ids)
    random.Random(seed).shuffle(shuffled)
    return {
        "train512": sorted(shuffled[:512], key=qid_key),
        "dev128": sorted(shuffled[512:], key=qid_key),
        "test160": sorted(test_ids, key=qid_key),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--official-train", required=True, type=Path)
    parser.add_argument("--official-test", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "configs/revised_protocol.json")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    for role, path in (("train640", args.official_train), ("test160", args.official_test)):
        if sha256(path) != config["official_source_sha256"][role]:
            parser.error(f"{role} source SHA-256 differs from adopted protocol")
    splits = split_ids(ids_in_source_order(args.official_train),
                       ids_in_source_order(args.official_test), config["split_seed"])
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        parser.error("output directory is nonempty; choose a new directory")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    for role, ids in splits.items():
        path = args.out_dir / f"{role}_ids.jsonl"
        path.write_text("".join(json.dumps({"id": qid}) + "\n" for qid in ids), encoding="utf-8")
    print(json.dumps({role: len(ids) for role, ids in splits.items()}, sort_keys=True))


if __name__ == "__main__":
    main()
