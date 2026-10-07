# CECRA evaluation and protocol release

English | [简体中文](README.zh-CN.md)

This repository contains a **limited evaluation and configuration companion**
for the accepted CECRA manuscript. It is separate from the full CECRA
research repository and does not release the neural model implementation,
case texts, query IDs, qrels, prediction scores, evidence caches, weights,
checkpoints, reviewer material, or underlying experiment result files.

The included tools evaluate frozen score files, derive ID-only split
manifests from authorized official files, and select checkpoints from the
prespecified dev128 MAP curve. The repository also includes a redacted
protocol configuration, synthetic unit tests, and fingerprints for the local
Qwen3-32B-AWQ snapshot used for offline evidence construction. The aggregate
paper results below are supplied for context; their per-query records and
predictions are not included here. Users must obtain datasets under their own
applicable terms.


The exact upstream commit of the local Qwen snapshot was not retained. The model identifier, recorded revision string, local file SHA-256 fingerprints, prompt hashes, and generation settings are therefore reported in [`reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md`](reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md). These fingerprints identify the files used in this study without redistributing them.

## Repository contents

| File | Purpose |
|---|---|
| [evaluate.py](evaluate.py) | Computes the seven paper metrics from frozen scores and authorized qrels. |
| [make_split_ids.py](make_split_ids.py) | Recreates ID-only train512/dev128/test160 manifests and verifies official source-file hashes. |
| [select_checkpoint.py](select_checkpoint.py) | Selects among six prespecified dev128 MAP checkpoints; rejects non-dev selection curves. |
| [configs/revised_protocol.json](configs/revised_protocol.json) | Redacted protocol settings, source hashes, split sizes, and method-specific checkpoint steps. |
| [tests/test_release.py](tests/test_release.py) | Synthetic tests; contains no case text, qrels, predictions, or private IDs. |
| [reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md](reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md) | Local model and prompt fingerprints plus the measured cost-audit scope. |

## Accepted paper

| Field | Information |
|---|---|
| Title | CECRA: Structured Evidence-Aware Reranking for Long-Document Legal Case Retrieval |
| Authors | Hanjie Ma and Yun Sun |
| Journal | Applied Sciences |
| Status | Accepted; publisher-assigned DOI and final citation metadata are not recorded in this release yet |

CECRA combines a global Summary representation with local Fact Evidence and
Reasoning Evidence. The local views use five fact slots and four reasoning
steps with validity masks and slot-level interaction. Qwen3-32B constructs
the evidence offline; it is not an online reranker dependency. This repository
releases the evaluation and protocol utilities, not the CECRA model or
training implementation.

### Main LeCaRDv2 results

The values below are the paper-facing results under the revised
train512/dev128/test160 protocol. They are means ± standard deviations across
seeds 42, 123, and 2026, on a 0–100 scale. Trainable methods select
checkpoints on dev128; test160 is not used for training, tuning, or checkpoint
selection.

| Method | MAP | MRR | P@1 | P@3 | NDCG@3 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| KELLER | 67.32 ± 0.11 | 74.27 ± 0.48 | 66.25 ± 0.62 | 60.49 ± 0.73 | 83.57 ± 0.31 | 84.61 ± 0.04 | 87.12 ± 0.07 |
| SAILER-FT | 70.72 ± 0.08 | 77.22 ± 0.16 | 70.83 ± 0.36 | 66.74 ± 0.12 | 86.21 ± 0.07 | 87.12 ± 0.02 | 88.78 ± 0.06 |
| **CECRA** | **72.95 ± 0.05** | **80.51 ± 0.18** | **73.96 ± 0.36** | **68.40 ± 0.12** | **87.70 ± 0.05** | **88.29 ± 0.04** | **90.01 ± 0.06** |

The two prespecified CECRA–SAILER-FT comparisons use query-clustered
inference and Holm correction across the two tests:

- MAP: +2.23 percentage points; 95% CI [0.46, 4.15]; adjusted p = 0.0138.
- NDCG@10: +1.23 percentage points; 95% CI [0.54, 1.97]; adjusted p = 0.0011.

The local-evidence ablation jointly removes both local views and their
associated Agreement calculations. The resulting 2.24-point MAP decrease
does not isolate Agreement's independent effect.

### Scope of the paper's claims

- The main LeCaRDv2 evaluation ranks each query's fixed judged candidate pool:
  160 test queries and 4,795 judged query-candidate pairs. It is not
  full-corpus retrieval.
- EUR-LexRD is an exploratory, single-checkpoint, zero-shot evaluation over a
  qrels-defined judged pool. It is not evidence of full-corpus or universal
  cross-jurisdiction generalization.
- The EUR-LexRD analysis covers 100 English CJEU queries, 6,146 unique judged
  candidates, and 12,365 judged pairs. It reports one frozen checkpoint:
  CECRA MAP 27.99, SAILER-FT MAP 24.29, and BM25 MAP 31.94. BM25 is higher
  than CECRA on all seven reported metrics in this pool.
- Qwen3-32B constructs evidence offline. The CECRA reranker itself has no
  online Qwen dependency.
- The evaluator in this repository computes metrics from already frozen
  scores. It does not run the model or reproduce model inference.
- The paper reports a prespecified fixed-epoch sensitivity separately.
  Later internal multi-checkpoint test diagnostics are excluded from the
  confirmatory main results and are not used to select the reported checkpoint.

The article's publication record should be updated with the publisher's final
DOI, volume, issue, article number or pages, and Version of Record link when
those details are assigned.

## Evaluation contract

- LeCaRDv2: fit on `train512`, select checkpoints on `dev128` only, freeze, then evaluate the official `test160` judged pool. All trainable methods use 10 epochs and six prespecified, method-specific progress checkpoints.
- The evaluator expects one score per **judged candidate** for every requested query (160 queries; 4,795 judged pairs on test160). Missing or extra candidate IDs fail closed. Pool membership is supplied by qrels, not BM25.
- Sort by score descending; break exact ties by document ID descending, matching the revised CECRA score-ranking path. Query and document IDs are strings. This is not a statement that every third-party baseline's native implementation uses the same tie rule.
- For MAP, MRR, and P@k, a query with label 3 uses label 3 as positive; otherwise labels 2 and 3 are positive. A query with no positive gets AP=0 and stays in the denominator. P@k divides by fixed `k`. NDCG uses gains `0, 1, 2, 4` for labels `0, 1, 2, 3`, with the ideal ranking from the same judged pool; zero ideal gain yields zero.
- All seven metrics are query-macro means in `[0,1]`; multiply by 100 only for paper table display. The evaluator does not train, select, or run a neural model.

## Split provenance

The adopted paper-facing split uses seed 20260919 to divide the official
640-query training set into train512 and dev128; the official test160 remains
held out. The adopted source manifest is not copied into this code-only
repository. Its hashes are recorded here so users can check authorized local
files without publishing query IDs:

| Reference artifact | Queries / judged pairs | SHA-256 |
|---|---:|---|
| Adopted manifest | — | 978aa250e8363dc912384eb18954eec18b958b7d90d75d939376fd324fd69287 |
| train512 split | 512 / 15,333 | ee85b304f7912c4a734c5cdd000d82e636c114fe4b0bb18690c67a99741334de |
| dev128 split | 128 / 3,836 | 92febc7336c58492684731209bbd0f703cbc145ec8331037176abc45b0c1c48d |
| test160 split | 160 / 4,795 | 943a4211d79a171a20d70451b88a3bfd0a23f54f2c780c390d01fbbfb9a8ffd6 |

The split-ID utility writes only to a user-selected local output directory.
Do not commit generated split-ID manifests to this repository.

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

The scripts are stdlib-only, do not read the CECRA source tree, and do not
contain local machine paths. They intentionally stop short of reproducing
model inference or redistributing restricted source material.

## Data, weights, and reuse

The LeCaRD and LeCaRDv2 source datasets must be obtained from their upstream
repositories under the terms that apply there. This release does not include
those datasets, their query IDs or qrels, model weights, or generated legal
text. The Qwen fingerprints identify a local model snapshot; they are not the
weights themselves and do not recover the missing immutable upstream model
commit.

An independent offline extraction cost audit measured 23,911 judged-pool
candidate records, 133,604,181 submitted input tokens, 19,696,968 generated
output tokens, and 119.05 active GPU-hours. This is not a cost measurement for
all 55,192 LeCaRDv2 candidates, query extraction, or the historical build of
the formal evidence cache; see the fingerprint record for the full boundary.

This Git repository has **no LICENSE file**. Public visibility does not grant
reuse, modification, or redistribution rights. Do not describe this code
snapshot as an OSI-licensed open-source release until the authors select and
add license terms. Third-party dataset, model, and manuscript terms remain
separate.

## Citation

Until the publisher assigns final metadata, cite the accepted manuscript as:

> Ma, Hanjie, and Yun Sun. “CECRA: Structured Evidence-Aware Reranking for
> Long-Document Legal Case Retrieval.” *Applied Sciences*. Accepted
> manuscript.

Replace this provisional citation with the final publisher citation and DOI
when available.
