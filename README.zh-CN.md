# CECRA 评测与协议配置发布包

[English](README.md) | 简体中文

本仓库是 CECRA 录用论文配套的**有限评测与配置材料**。它独立于完整
CECRA 研究仓库，不公开神经模型实现、案件文本、查询 ID、qrels、
预测分数、证据缓存、模型权重、checkpoint、审稿材料或实验逐条结果文件。

当前包含：对冻结分数文件计算指标的工具、从获准使用的官方文件生成仅含
ID 的数据划分清单的工具、依据预先规定的 dev128 MAP 曲线选择 checkpoint
的工具、脱敏协议配置、合成单元测试，以及离线证据构建所用 Qwen3-32B-AWQ
本地快照的文件指纹。下方汇总论文结果供读者理解研究结论；逐查询结果和
预测文件不在本仓库中。

本地 Qwen 快照没有保留确切的上游 commit。因此，模型标识、记录中的
revision 字符串、本地文件 SHA-256、prompt 哈希和生成参数记录在
[Qwen 快照说明](reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md)中。
这些指纹用于识别实验中实际使用的文件，不会分发模型权重。

## 文件清单

| 文件 | 用途 |
|---|---|
| [evaluate.py](evaluate.py) | 根据冻结分数和获准使用的 qrels 计算论文中的七项指标。 |
| [make_split_ids.py](make_split_ids.py) | 重建仅含 ID 的 train512/dev128/test160 清单，并校验官方源文件哈希。 |
| [select_checkpoint.py](select_checkpoint.py) | 按预先规定的六个 dev128 MAP 点选 checkpoint；拒绝非 dev 选点曲线。 |
| [configs/revised_protocol.json](configs/revised_protocol.json) | 脱敏协议、源文件哈希、划分数量及各方法选点步数。 |
| [tests/test_release.py](tests/test_release.py) | 合成数据测试；不含案件文本、qrels、预测或私有 ID。 |
| [reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md](reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md) | 本地模型与 prompt 指纹，以及独立成本审计的范围。 |

## 录用论文

| 项目 | 信息 |
|---|---|
| 题目 | CECRA: Structured Evidence-Aware Reranking for Long-Document Legal Case Retrieval |
| 作者 | Hanjie Ma、Yun Sun |
| 期刊 | Applied Sciences |
| 状态 | 已录用；本发布包尚未记录出版社分配的 DOI 和最终引文信息 |

CECRA 将全局 Summary 表示与局部 Fact Evidence、Reasoning Evidence
结合；局部视图包含 5 个事实槽位和 4 个推理步骤，并通过有效性掩码和
槽位级交互进行匹配。Qwen3-32B 只在离线阶段构建证据，不是重排器在线
运行的依赖。本仓库发布的是评测和协议工具，不包含 CECRA 模型或训练实现。

### LeCaRDv2 主结果

下列数值对应修订后的 train512/dev128/test160 论文协议，为随机种子
42、123、2026 的均值 ± 标准差，按 0–100 刻度报告。可训练方法只用
dev128 选择 checkpoint；test160 不用于训练、调参或 checkpoint 选择。

| 方法 | MAP | MRR | P@1 | P@3 | NDCG@3 | NDCG@5 | NDCG@10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| KELLER | 67.32 ± 0.11 | 74.27 ± 0.48 | 66.25 ± 0.62 | 60.49 ± 0.73 | 83.57 ± 0.31 | 84.61 ± 0.04 | 87.12 ± 0.07 |
| SAILER-FT | 70.72 ± 0.08 | 77.22 ± 0.16 | 70.83 ± 0.36 | 66.74 ± 0.12 | 86.21 ± 0.07 | 87.12 ± 0.02 | 88.78 ± 0.06 |
| **CECRA** | **72.95 ± 0.05** | **80.51 ± 0.18** | **73.96 ± 0.36** | **68.40 ± 0.12** | **87.70 ± 0.05** | **88.29 ± 0.04** | **90.01 ± 0.06** |

预先指定的两项 CECRA–SAILER-FT 比较以 query 为聚类单位，并对两项检验
进行 Holm 校正：

- MAP：提高 2.23 个百分点；95% CI [0.46, 4.15]；校正后 p = 0.0138。
- NDCG@10：提高 1.23 个百分点；95% CI [0.54, 1.97]；校正后 p = 0.0011。

局部证据消融同时移除两个局部视图及其关联的 Agreement 计算，MAP
下降 2.24 个百分点。这个联合变化不能单独证明 Agreement 的独立效果。

### 论文结论的适用范围

- LeCaRDv2 主实验是在固定的已判定候选池中排序：测试集有 160 个 query、
  4,795 个已判定 query-candidate 对。这不是全库检索。
- EUR-LexRD 是基于 qrels 定义候选池、单 checkpoint 的探索性零样本评测，
  不能证明全语料检索能力或跨法域普遍泛化。
- EUR-LexRD 分析包含 100 个英语 CJEU query、6,146 个唯一已判定候选和
  12,365 个已判定对，只评测一个冻结 checkpoint。该池中 CECRA、SAILER-FT、
  BM25 的 MAP 分别为 27.99、24.29、31.94；BM25 的七项指标都高于 CECRA。
- Qwen3-32B 在离线阶段构造证据；CECRA 重排器在线运行不依赖 Qwen。
- 本仓库中的评测器只根据已经冻结的分数计算指标，不运行模型，也不复现
  模型推理。
- 论文另行报告了预先规定的固定 epoch 敏感性分析。后续内部多 checkpoint
  test 诊断不属于确认性主结果，也未用于选择论文报告的 checkpoint。

出版社确定最终信息后，应补充 DOI、卷期、文章编号或页码，以及 Version
of Record 链接。

## 划分来源与哈希

论文采用的划分以 seed 20260919 将官方 640 个训练 query 划分为 train512
和 dev128；官方 test160 保持为独立测试集。代码包不包含 adopted manifest
或 query ID。以下哈希可用于核对用户依法取得的本地文件：

| 参考文件 | 查询数 / 已判定 query-candidate 对 | SHA-256 |
|---|---:|---|
| Adopted manifest | — | 978aa250e8363dc912384eb18954eec18b958b7d90d75d939376fd324fd69287 |
| train512 划分 | 512 / 15,333 | ee85b304f7912c4a734c5cdd000d82e636c114fe4b0bb18690c67a99741334de |
| dev128 划分 | 128 / 3,836 | 92febc7336c58492684731209bbd0f703cbc145ec8331037176abc45b0c1c48d |
| test160 划分 | 160 / 4,795 | 943a4211d79a171a20d70451b88a3bfd0a23f54f2c780c390d01fbbfb9a8ffd6 |

划分工具只向用户指定的本地目录写出 ID 清单。请勿将生成的 query ID
清单提交到本仓库。

## 数据、权重与使用许可

LeCaRD 和 LeCaRDv2 数据应从[上游仓库](https://github.com/myx666/LeCaRD)
和[LeCaRDv2 仓库](https://github.com/THUIR/LeCaRDv2)获取，并遵循相应
条款。本发布包不包含案件文本、query ID、qrels、预测、模型权重或生成的
法律文本。EUR-LexRD 数据集来源为
[KU Leuven Research Data Repository](https://doi.org/10.48804/TK4IER)。

一次独立的离线抽取成本审计实测了固定已判定候选池中的 23,911 个候选：
提交输入 133,604,181 tokens、生成输出 19,696,968 tokens、GPU 活动占用
119.05 小时。该测量不代表 LeCaRDv2 全部 55,192 个候选的成本、不含 query
抽取，也不是正式证据缓存的历史构建成本；详细范围见
[Qwen 快照说明](reproducibility/QWEN3_32B_AWQ_LOCAL_SNAPSHOT.md)。

本 Git 仓库**没有 LICENSE 文件**。代码可在线查看不代表用户自动获得
复用、修改或再分发权限。作者选定并添加许可证之前，不应把此代码快照称为
已取得 OSI 许可证的开源发布。第三方数据集、模型和稿件材料仍适用各自条款。

## 引用

出版社分配最终信息之前，可暂按以下格式引用录用稿：

> Ma, Hanjie, and Yun Sun. “CECRA: Structured Evidence-Aware Reranking for
> Long-Document Legal Case Retrieval.” *Applied Sciences*. Accepted
> manuscript.

获得最终出版信息后，请替换为正式引文和 DOI。
