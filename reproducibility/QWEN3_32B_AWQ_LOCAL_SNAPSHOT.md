# Qwen3-32B-AWQ local snapshot record

This record identifies the local offline evidence-construction snapshot used in the CECRA study. It does not redistribute model weights, case text, prompts containing case data, generated evidence, or predictions.

## Model identity and revision boundary

- Model identifier: `Qwen/Qwen3-32B-AWQ`
- Local directory name: `qwen3-32b-awq`
- Revision recorded in local metadata: `master`
- Local metadata creation timestamp: `1747844553`
- Immutable upstream commit: **not retained and therefore not reported**

Because an immutable upstream commit cannot be recovered from the local snapshot, the full local-file fingerprints below are the reproducibility identifier for the model files actually used.

## Local-file SHA-256 fingerprints

| File | SHA-256 |
|---|---|
| `config.json` | `0e0c09d430b12e84773ef83ca83dba7c9174caf5a94bb940cd895b82df6c6528` |
| weight index | `7d0427c7d238f401b5d38ec08dca07cc8a921aa69d73769b2b7983520de504a1` |
| `tokenizer_config.json` | `d5d09f07b48c3086c508b30d1c9114bd1189145b74e982a265350c923acd8101` |
| `generation_config.json` | `2325da0f15bb848e018c5ae071b7943332e9f871d6b60e2ed22ca97d4cb993d2` |
| weight shard 00001 | `ab7988215e3b087c884e0c14ce1994a64aac31dc9a37a4bcf29f5b45f3506e2e` |
| weight shard 00002 | `46faff349f1dd18ffe76993edd3d9fd32941d042331dc590525409bbe3d37edf` |
| weight shard 00003 | `6e9f763d8c31ad19f1cd67b0b599a38edffd76a4465a22ff5f7fcac46d820e63` |
| weight shard 00004 | `87f180889fead12b00b1bdf4dca3a3a14e4510e1e200bf56e31898e120b993d8` |

## Prompt SHA-256 fingerprints

| Prompt | SHA-256 |
|---|---|
| system | `6669e2fa6242942ce558123e5bf680603a488edbbf329754f003a37443d9eb12` |
| query template | `d55803494eb20ef816e69fc3cbd876d05a33d233a8bff0dcc2cfb638917faabd` |
| candidate template | `714503e93ff1053649fe52972f9e377ac79cd6938984c046056145621817e6f6` |

The human-readable Chinese prompts are reproduced in Appendix A of the manuscript. The hashes above refer to the exact prompt strings used by the cost-audit implementation.

## Generation settings

| Setting | Value |
|---|---:|
| Temperature | 0.1 |
| Top-p | 0.9 |
| Decoding top-k | 20 |
| Presence penalty | 1.5 |
| Maximum output tokens | 4,096 |
| Thinking mode | disabled |
| Generation seed | 42 |
| Maximum model length | 32,768 tokens |

The main evidence cache was reused for training seeds 42, 123, and 2026; evidence was not regenerated per training seed.

## Cost-audit scope

The independent measured audit covered 23,911 unique candidates in the fixed judged pools: 2,611 LeCaRD candidates and 21,300 LeCaRDv2 candidates. It submitted 133,604,181 input tokens, generated 19,696,968 output tokens, and used 119.05 active GPU-hours across eight RTX 4090 GPUs. This is a judged-pool candidate audit. It is not a measurement of all 55,192 LeCaRDv2 candidates, query extraction, or the historical construction cost of the formal cache.
