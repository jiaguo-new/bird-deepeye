# ZCode DeepEye Dev audit snapshot

Source: ZCode sess_c281fcd3-8578-4d0c-9ffd-6864ad3f2709.
This captures the observed application overlay over upstream 252ab45.
The launcher retains the eight stages, omits the original proxy settings
and clears SQL_CONTRACT_PROMPT. The observed source cannot attest to the
exact code or environment used by the historical run.

Populate a separate copy of bird-dev-full.example.toml outside Git with
the dataset and output paths, embedding model identity, approved endpoints
and credentials. Use its absolute path as CONFIG_PATH. PYTHON_BIN defaults
to .venv/bin/python. The template uses the historical Dev split.
