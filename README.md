# CECRA

This repository contains the evaluation and configuration code released before acceptance of the CECRA manuscript. It is separate from the full CECRA research repository; publishing this subset does not release the model implementation, case texts, weights, or experiment artifacts.

Included: a seven-metric evaluator for already generated scores, an ID-only deterministic split utility, a six-point `dev128` checkpoint selector, a redacted protocol configuration, and synthetic unit tests. Not included: case texts, query IDs, qrels, prediction scores, generated evidence caches, model code or weights, checkpoints, reviewer material, or results. Users must obtain datasets under their own applicable terms.

## Evaluation contract

- LeCaRDv2: fit on `train512`, select checkpoints on `dev128` only, freeze, then evaluate the official `test160` judged pool. All trainable methods use 10 epochs and six prespecified, method-specific progress checkpoints.
- The evaluator expects one score per **judged candidate** for every requested query (160 queries; 4,795 judged pairs on test160). Missing or extra candidate IDs fail closed. Pool membership is supplied by qrels, not BM25.
- Sort by score descending; break exact ties by document ID descending, matching the revised CECRA score-ranking path. Query and document IDs are strings. This is not a statement that every third-party baseline's native implementation uses the same tie rule.
- For MAP, MRR, and P@k, a query with label 3 uses label 3 as positive; otherwise labels 2 and 3 are positive. A query with no positive gets AP=0 and stays in the denominator. P@k divides by fixed `k`. NDCG uses gains `0, 1, 2, 4` for labels `0, 1, 2, 3`, with the ideal ranking from the same judged pool; zero ideal gain yields zero.
- All seven metrics are query-macro means in `[0,1]`; multiply by 100 only for paper table display. The evaluator does not train, select, or run a neural model.

## Usage after obtaining authorized qrels and frozen predictions

```bash
python3 make_split_ids.py --official-train YOUR_OFFICIAL_TRAIN.jsonl \
  --official-test YOUR_OFFICIAL_TEST.jsonl --out-dir YOUR_SPLIT_IDS_DIR
python3 evaluate.py --qrels YOUR_QRELS.trec --queries YOUR_TEST_IDS.jsonl \
  --predictions YOUR_FROZEN_SCORES.json --variant clean --out-dir YOUR_OUTPUT_DIR \
  --acknowledge-frozen-checkpoint
python3 select_checkpoint.py --curve YOUR_DEV_CURVE.json --config configs/revised_protocol.json
python3 -m unittest discover -s tests -v
```

`YOUR_TEST_IDS.jsonl` contains only `{"id": "query-id"}` rows. `YOUR_QRELS.trec` uses `qid 0 did grade`; `YOUR_FROZEN_SCORES.json` uses `{qid: {did: score}}`, optionally nested under `clean`. The evaluator also accepts the frozen SAILER-FT envelope `{qid: {"scores": {did: score}, ...}}`, but always reads labels from the separately supplied qrels. These are format descriptions, **not** released dataset files. For checkpoint selection, the input is `{ "method": "cecra", "seed": 42, "split": "dev128", "epochs": 10, "points": [{"step": 13, "MAP": 0.5}, ...] }` with the six steps in the configuration.

`make_split_ids.py` applies Python's seeded shuffle to the official train640 rows in their source order, then sorts each derived split by numeric query ID. It verifies the adopted source-file SHA-256 values and emits ID-only manifests into a user-selected output directory. The generated manifests are local outputs and must not be added to this code-only repository.

The scripts are stdlib-only, do not read the CECRA source tree, and do not contain local machine paths. They intentionally stop short of reproducing model inference or redistributing restricted source material. No license file is included in this limited release; the authors will decide reuse terms separately.
