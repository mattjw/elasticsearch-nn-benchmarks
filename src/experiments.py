import os
import re
from typing import List

from populate_index import populate_vectors

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
        print(case)
        print(populate_vectors(case["fpath"], "fcs"))
        print(populate_vectors(case["fpath"], "dense"))


def main():
    run_experiments()

if __name__ == "__main__":
    main()
