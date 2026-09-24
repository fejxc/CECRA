#!/usr/bin/env python3
"""Seven paper metrics from frozen scores and an authorized judged pool.

This is a dependency-free extraction of the revised CECRA metric contract.
It cannot select checkpoints or run a model. Scores must already be frozen.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean

METRICS = ("MAP", "MRR", "P@1", "P@3", "NDCG@3", "NDCG@5", "NDCG@10")
GAIN = (0.0, 1.0, 2.0, 4.0)


def read_queries(path: Path) -> list[str]:
    qids = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        qid = item.get("id", item.get("qid")) if isinstance(item, dict) else item
        if qid is None:
            raise ValueError("query row lacks id/qid")
        qids.append(str(qid))
    if not qids or len(qids) != len(set(qids)):
        raise ValueError("query list is empty or has duplicate IDs")
    return qids


def read_qrels(path: Path, qids: list[str]) -> dict[str, dict[str, int]]:
    allowed = set(qids)
    output = {qid: {} for qid in qids}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(f"qrels line {number}: expected qid 0 did grade")
        qid, did = parts[0], parts[2]
        if qid not in allowed:
            continue
        grade_float = float(parts[3])
        grade = int(grade_float)
        if grade_float != grade or grade not in range(4):
            raise ValueError(f"qrels line {number}: invalid grade")
        if did in output[qid]:
            raise ValueError(f"qrels line {number}: duplicate qid/did")
        output[qid][did] = grade
    if any(not values for values in output.values()):
        raise ValueError("at least one requested query has no judged candidates")
    return output


def read_scores(path: Path, variant: str | None = None) -> dict[str, dict[str, float]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if variant:
        raw = raw[variant]
    if not isinstance(raw, dict):
        raise ValueError("scores must be a JSON object keyed by query ID")
    scores = {}
    for qid, value in raw.items():
        if not isinstance(value, dict):
            raise ValueError("each query must map candidate IDs to numeric scores")
        if "scores" in value and isinstance(value["scores"], dict):
            # Also accepts the frozen SAILER-FT ranking artifact envelope.
            value = value["scores"]
        row = {str(did): float(score) for did, score in value.items()}
        if not all(math.isfinite(score) for score in row.values()):
            raise ValueError(f"non-finite score for query {qid}")
        scores[str(qid)] = row
    return scores


def score_query(scores: dict[str, float], labels: dict[str, int]) -> dict[str, float]:
    if set(scores) != set(labels):
        raise ValueError("prediction candidate IDs must exactly equal judged-pool IDs")
    # Matches the revised score-ranking path: score descending, then did descending.
    ranking = sorted(scores, key=lambda did: (scores[did], did), reverse=True)
    positive = {3} if 3 in labels.values() else {2, 3}
    hits = 0
    ap_sum = 0.0
    reciprocal_rank = 0.0
    for position, did in enumerate(ranking, 1):
        if labels[did] in positive:
            hits += 1
            ap_sum += hits / position
            if not reciprocal_rank:
                reciprocal_rank = 1.0 / position
    # Complete judged pools make retrieved hits equal all judged positives.
    ap = ap_sum / hits if hits else 0.0
    row = {
        "MAP": ap,
        "MRR": reciprocal_rank,
        "P@1": sum(labels[d] in positive for d in ranking[:1]) / 1,
        "P@3": sum(labels[d] in positive for d in ranking[:3]) / 3,
    }
    ideal = sorted((GAIN[label] for label in labels.values()), reverse=True)
    for k in (3, 5, 10):
        actual_gain = sum(GAIN[labels[d]] / math.log2(i + 2) for i, d in enumerate(ranking[:k]))
        ideal_gain = sum(value / math.log2(i + 2) for i, value in enumerate(ideal[:k]))
        row[f"NDCG@{k}"] = actual_gain / ideal_gain if ideal_gain else 0.0
    return row


def evaluate(scores: dict[str, dict[str, float]], qrels: dict[str, dict[str, int]],
             qids: list[str]) -> tuple[dict[str, float], list[dict]]:
    if set(scores) != set(qids) or set(qrels) != set(qids):
        raise ValueError("predictions and qrels must cover exactly the requested queries")
    rows = []
    for qid in qids:
        rows.append({"qid": qid, **score_query(scores[qid], qrels[qid])})
    aggregate = {key: mean(row[key] for row in rows) for key in METRICS}
    aggregate["query_count"] = len(rows)
    aggregate["judged_pairs"] = sum(len(qrels[qid]) for qid in qids)
    return aggregate, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qrels", required=True, type=Path)
    parser.add_argument("--queries", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--variant", help="Optional top-level prediction key, e.g. clean")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--config", type=Path, default=Path(__file__).parent / "configs/revised_protocol.json")
    parser.add_argument("--acknowledge-frozen-checkpoint", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_frozen_checkpoint:
        parser.error("confirm checkpoint was frozen before held-out evaluation")
    config = json.loads(args.config.read_text(encoding="utf-8"))
    qids = read_queries(args.queries)
    expected_queries = config["query_counts"]["test160"]
    if len(qids) != expected_queries:
        parser.error(f"this revised test160 entry point requires {expected_queries} queries, got {len(qids)}")
    qrels = read_qrels(args.qrels, qids)
    scores = read_scores(args.predictions, args.variant)
    result, rows = evaluate(scores, qrels, qids)
    if result["judged_pairs"] != config["test160_judged_pairs"]:
        parser.error("judged-pair count differs from the frozen test160 protocol")
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        parser.error("output directory is nonempty; choose a new directory")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    with (args.out_dir / "per_query_metrics.csv").open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=("qid",) + METRICS)
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
