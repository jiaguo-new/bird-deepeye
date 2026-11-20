"""Check the BIRD review launcher settings before starting inference."""
import os
import sys
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.config import get_config


def check_endpoints(section):
    for key, value in section.items():
        if isinstance(value, dict):
            check_endpoints(value)
        if key == "base_url":
            endpoint = urlsplit(value)
            if endpoint.scheme not in {"http", "https"} or endpoint.hostname not in {
                "127.0.0.1", "::1",
            } or endpoint.username is not None:
                raise SystemExit("Model endpoints must use a numeric loopback address")


if __name__ == "__main__":
    with Path(os.environ["CONFIG_PATH"]).open("rb") as handle:
        check_endpoints(tomllib.load(handle))
    config = get_config()
    dataset = config.dataset_config
    if dataset.type != "bird" or not dataset.blind_inference:
        raise SystemExit("Set dataset.type='bird' and dataset.blind_inference=true")
    if dataset.max_samples is not None or dataset.max_samples_per_db is not None:
        raise SystemExit("Provide the exact input split instead of setting sample caps")
    print(config.sql_selection_config.save_path)
