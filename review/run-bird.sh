#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
: "${CONFIG_PATH:?Set CONFIG_PATH to the absolute path of a populated config}"
export CONFIG_PATH
unset SQL_CONTRACT_PROMPT
run() { "${PYTHON_BIN:-.venv/bin/python}" "runner/$1.py"; }
run preprocess_dataset
run create_vector_db_parallel
run run_value_retrieval
run run_few_shot_preparation
run run_schema_linking
run run_sql_generation
run run_sql_revision
run run_sql_selection
