# DeepEye-based BIRD evaluation candidate

This candidate builds on DeepEye-SQL upstream 252ab45 (MIT). The earlier
73.40% legacy Dev result belongs to a separate historical run. This revision
changes input validation and few-shot eligibility and has no measured Dev EX.

The project adds a generation experiment to address SQL intent errors.
Under `[sql_generation]`, `dc_semantic_budget = 2` replaces two of the
four direct-generation slots with a prompt that checks filters, join
cardinality, output grain, grouping, and ties. The other two direct slots
and the skeleton and ICL budgets stay the same. The default of zero
keeps the adapted DeepEye comparison arm. The check uses the question,
evidence and available schema, with no answer or extra model call per slot.
This experiment has no measured accuracy gain yet.
Set `dc_value_anchors = true` in `[sql_generation]` to append column-bound
evidence to direct prompts. Anchors use only retrieved text values explicitly
mentioned in the question or evidence and cap the added context at six entries.

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

## Paired TRAIN evaluation

Before requesting any candidates, freeze a 100-question TRAIN holdout
and a second 50-question set from disjoint TRAIN databases. Exclude those
databases from the few-shot index used by both arms. Record the dataset
version, model identities, code, prompts, index and scoring hashes. Both
arms use the same model, four DC, four skeleton and four ICL slots, with
the same revision and selection code and budgets. Actual requests,
retries, failures, and tokens are counted separately. The added prompt
increases input tokens and can affect actual retry and downstream costs.

Use the same official execution comparison for both arms, with predictions
frozen before the scorer gets Gold. Preserve the full denominator and
report rescues and regressions. Require at least five net additional
correct on the 100 paired questions and a positive net on the untouched
50-question confirmation before promoting the variant. This comparison
tests the effect of our change relative to the adapted DeepEye baseline.
Claims against published DeepEye require a separate same-protocol baseline.

For the value anchor study, fix both switches before opening any scores. Run
baseline, semantic checks only, value anchors only, and both switches together.
Keep input, models, generation slots and downstream revision/selection fixed.
Report the individual and joint effects against baseline and the incremental
effect of adding anchors to semantic checks. Compare EX and actual token costs.

### Schema coverage follow-up

The first paired study's combined arm scored 76/100 against the adapted
baseline's 75/100. Of the combined arm's 24 misses, 20 had no correct SQL
in either candidate pool, three had a correct revised candidate that was
not selected, and one lost every correct candidate during revision.

The follow-up sets `dc_full_schema_budget = 2` to give two direct slots
the value-enriched schema before pruning. Two semantic slots and all
skeleton/ICL slots still use the linked schema. Both arms retain the same
value anchors and budgets. This follows the database profiling and schema
grounding direction described in the AskData paper while testing whether
a complementary schema view recovers SQL missed by pruning.

Run both arms on 100 new TRAIN questions from 20 databases disjoint from
the diagnosis and confirmation databases. Admission requires at least
five net additional correct answers over the previous combined recipe
on those same new questions. Report candidate coverage before and after
revision and separate it from top-one EX. The prior 50-question
confirmation remains sealed until admission.
