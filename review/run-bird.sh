#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
: "${CONFIG_PATH:?Set CONFIG_PATH to the absolute path of a populated config}"
: "${BIRD_PREDICTIONS:?Set BIRD_PREDICTIONS to a new output JSON path}"
: "${BIRD_EXPECTED_COUNT:?Set BIRD_EXPECTED_COUNT to the number of input questions}"
export CONFIG_PATH
unset SQL_CONTRACT_PROMPT HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
python_bin="${PYTHON_BIN:-.venv/bin/python}"
snapshot="$("$python_bin" review/bird_preflight.py)"
run() { "$python_bin" "runner/$1.py"; }
run preprocess_dataset
run create_vector_db_parallel
run run_value_retrieval
run run_few_shot_preparation
run run_schema_linking
run run_sql_generation
run run_sql_revision
run run_sql_selection
"$python_bin" runner/export_bird_predictions.py "$snapshot" "$BIRD_PREDICTIONS" \
    --expected-count "$BIRD_EXPECTED_COUNT"
