import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluate import evaluate, score_query
from make_split_ids import split_ids
from select_checkpoint import select


class MetricContractTests(unittest.TestCase):
    def test_dynamic_positive_and_no_positive(self):
        labels = {"a": 3, "b": 2, "c": 0}
        scores = {"a": 3.0, "b": 2.0, "c": 1.0}
        self.assertEqual(score_query(scores, labels)["MAP"], 1.0)
        no_positive = score_query({"a": 2.0, "b": 1.0}, {"a": 1, "b": 0})
        self.assertEqual(no_positive["MAP"], 0.0)
        self.assertGreater(no_positive["NDCG@3"], 0.0)

    def test_descending_doc_id_tie(self):
        labels = {"2": 0, "10": 3}
        scores = {"2": 1.0, "10": 1.0}
        self.assertEqual(score_query(scores, labels)["P@1"], 0.0)

    def test_query_macro_and_pool_guard(self):
        labels = {"q1": {"a": 3, "b": 0}, "q2": {"a": 0, "b": 1}}
        scores = {"q1": {"a": 2, "b": 1}, "q2": {"a": 2, "b": 1}}
        result, rows = evaluate(scores, labels, ["q1", "q2"])
        self.assertEqual(result["MAP"], 0.5)
        self.assertEqual(len(rows), 2)
        with self.assertRaises(ValueError):
            score_query({"a": 1.0}, labels["q1"])


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "configs/revised_protocol.json").read_text())
        self.curve = {
            "method": "cecra", "seed": 42, "split": "dev128", "epochs": 10,
            "points": [
                {"step": step, "MAP": value}
                for step, value in zip((13, 26, 39, 52, 65, 78), (.1, .2, .3, .4, .4, .3))
            ],
        }

    def test_earliest_maximum(self):
        self.assertEqual(select(self.curve, self.config)["selected_step"], 52)

    def test_reject_test_selection(self):
        self.curve["split"] = "test160"
        with self.assertRaises(ValueError):
            select(self.curve, self.config)

    def test_reject_missing_opportunity(self):
        self.curve["points"].pop()
        with self.assertRaises(ValueError):
            select(self.curve, self.config)


class SplitTests(unittest.TestCase):
    def test_deterministic_disjoint_counts(self):
        train = [str(i) for i in range(640)]
        test = [str(i) for i in range(640, 800)]
        one = split_ids(train, test, 20260919)
        self.assertEqual(one, split_ids(train, test, 20260919))
        self.assertEqual([len(one[key]) for key in ("train512", "dev128", "test160")], [512, 128, 160])
        self.assertEqual(len(set().union(*map(set, one.values()))), 800)

if __name__ == "__main__":
    unittest.main()
