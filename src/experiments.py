import os
import re
from typing import List

from populate_index import populate_vectors
from query_index import test_query_fcs, test_query_dense

QUERY_EXPERIMENT_NUM_REPEATS = 1
TEST_CASES_DIR = "./data/slices/"


def test_cases(test_cases_dir=TEST_CASES_DIR) -> List[dict]:
    """Generate all test cases to be executed."""
    cases = []
    for fname in os.listdir(test_cases_dir):
        match = re.match("vectors_dim(\d+)_num(\d+).txt", fname)
        if match is not None:
            cases.append({
                "fpath": os.path.join(test_cases_dir, fname),
                "num_dimensions": int(match.group(1)),
                "num_vectors": int(match.group(2)),
            })
    cases.sort(key=lambda d: d["num_vectors"])
    return cases


def run_experiments():
    for case in test_cases():
        test_case_results = {"test_case": case}

        # # FCS
        record = {}
        record["populate_time_secs"] = populate_vectors(case["fpath"], "fcs")
        record["populate_time_avg_secs"] = record["populate_time_secs"] / case["num_vectors"]
        record["populate_time_ips"] = 1.0 / record["populate_time_avg_secs"]  # insertions per second

        record["query_time_avg_secs"] = test_query_fcs(case["fpath"], QUERY_EXPERIMENT_NUM_REPEATS)
        record["query_time_num_repeats"] = QUERY_EXPERIMENT_NUM_REPEATS
        record["query_time_qps"] = 1.0 / record["query_time_avg_secs"]  # queries per second

        test_case_results["fcs"] = record

        # dense
        record = {}
        record["populate_time_secs"] = populate_vectors(case["fpath"], "dense")
        record["populate_time_avg_secs"] = record["populate_time_secs"] / case["num_vectors"]
        record["populate_time_ips"] = 1.0 / record["populate_time_avg_secs"]  # insertions per second

        record["query_time_avg_secs"] = test_query_dense(case["fpath"], QUERY_EXPERIMENT_NUM_REPEATS)
        record["query_time_num_repeats"] = QUERY_EXPERIMENT_NUM_REPEATS
        record["query_time_qps"] = 1.0 / record["query_time_avg_secs"]  # queries per second

        test_case_results["dense"] = record

        print(
            "{}\n    fcs:   {}\n    dense: {}".format(
                test_case_results["test_case"], test_case_results["fcs"], test_case_results["dense"]))


def main():
    run_experiments()


if __name__ == "__main__":
    main()
