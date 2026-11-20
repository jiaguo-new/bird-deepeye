"""Export frozen BIRD predictions without loading evaluator inputs."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.append(".")
from app.dataset import load_dataset


def export_predictions(dataset, output: Path, expected_count: int) -> str:
    predictions = {}
    for item in dataset:
        question_id = item.question_id
        sql = item.final_selected_sql
        if item.gold_sql:
            raise ValueError(f"Gold SQL is present for question {question_id}")
        if question_id in predictions or not sql or not sql.strip():
            raise ValueError(f"Duplicate question or missing prediction: {question_id}")
        predictions[question_id] = f"{sql}\t----- bird -----\t{item.database_id}"
    if set(predictions) != set(range(expected_count)):
        raise ValueError("Prediction IDs do not match the expected BIRD question range")
    payload = json.dumps(dict(sorted(predictions.items())), ensure_ascii=False).encode("utf-8")
    with output.open("xb") as handle:
        handle.write(payload)
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-count", required=True, type=int)
    args = parser.parse_args()
    print(export_predictions(load_dataset(args.snapshot), args.output, args.expected_count))
