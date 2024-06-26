import json
import os

import argparse


def to_dict_key(key: str):
    for r in [" ", ":", "-"]:
        key = key.replace(r, "_")
    for r in ["(", ")"]:
        key = key.replace(r, "")
    return key


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--experimental",
        action="store_true",
        default=False,
        help="If passed, run ray.experimental microbenchmarks.",
    )
    args = parser.parse_args()

    if args.experimental:
        from ray._private.ray_experimental_perf import main
    else:
        from ray._private.ray_perf import main

    results = main() or []

    result_dict = {
        f"{to_dict_key(v[0])}": (v[1], v[2]) for v in results if v is not None
    }

    perf_metrics = [
        {
            "perf_metric_name": to_dict_key(v[0]),
            "perf_metric_value": v[1],
            "perf_metric_type": "THROUGHPUT",
        }
        for v in results
        if v is not None
    ]
    result_dict["perf_metrics"] = perf_metrics

    test_output_json = os.environ.get("TEST_OUTPUT_JSON", "/tmp/microbenchmark.json")

    with open(test_output_json, "wt") as f:
        json.dump(result_dict, f)
