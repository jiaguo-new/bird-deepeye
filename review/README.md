# DeepEye-based BIRD evaluation candidate

This candidate builds on DeepEye-SQL upstream 252ab45 (MIT). The earlier
73.40% legacy Dev result belongs to a separate historical run. This revision
changes input validation and few-shot eligibility and has no measured Dev EX.

Use Python 3.12 and install dependencies with `uv sync --locked`. Populate a
copy of `bird-dev-full.example.toml` outside Git. Set the dataset root and a
private run directory, the model and embedding identities, and the local
model endpoints and credentials. Build the few-shot index with
`python runner/build_few_shot_index.py --config /path/to/config.toml`
using the public BIRD TRAIN release. Pin the index and its source before
evaluating. Use a new run directory for fresh runs.

Place the evaluator-provided inputs at `<root>/<split>/<split>.json` and
databases at `<root>/<split>/<split>_databases/<db_id>/<db_id>.sqlite`.
Use `test` for organizer Test and `dev` for the legacy Dev dry run. The
question input contains question_id, db_id, question and evidence.
Difficulty is optional. The launcher rejects Gold SQL. It uses the supplied
evidence and SQLite database descriptions and does not require a separate
column_meaning.json.

```sh
CONFIG_PATH=/path/to/config.toml BIRD_PREDICTIONS=/path/to/predictions.json \
  BIRD_EXPECTED_COUNT=1534 bash review/run-bird.sh
```

Set the expected count to the actual organizer input count for Test. Use
the stage logs and snapshots to diagnose or resume failed runs with the
same configuration and input. The export checks question coverage and
prints the prediction SHA-256. Mount Gold only in a separate official
scoring environment after exporting.

The launcher requires configured model URLs on loopback. Run inference
inside an environment that denies external network egress and hosts
approved model and embedding services in that boundary. Column values
and sampled SQL results reach those services. A local proxy forwarding
those payloads outside the evaluation boundary does not satisfy this setup.
The submission still needs a measured Dev token total, runtime and hardware,
the frozen Dev prediction file, and a verified model-serving setup.
