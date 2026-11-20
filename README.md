# BirdFusion for BIRD

BirdFusion converts a question and its database context into SQL. It retrieves
relevant values and examples from other training databases, links the schema,
generates SQL candidates, and uses read-only execution to help revise and
select a final query.

The generation experiment adds two independently configurable changes.

| Feature | What it changes |
| --- | --- |
| Semantic checks | Replaces two of four direct generation slots with prompts that check filters, JOIN cardinality, output grain, grouping and ties. |
| Value anchors | Connects values already retrieved from the database to their table and column when the values appear in the question or evidence. The design draws on AskData's value grounding. No additional model calls or database queries are introduced. |

Both changes can be combined within the same 12 candidate slots. The default
keeps both off for the comparison. Their accuracy impact is under evaluation.
The historical 73.40% Dev result belongs to an earlier adaptation.

Experiments use paired BIRD TRAIN holdouts split by database. Inference receives
question inputs without Gold SQL. The scorer receives answers only after
predictions are frozen. Successful variants must improve on a separate
held-out set before full Dev evaluation.

See [the evaluation procedure](review/README.md) for configuration, dataset
layout, runtime boundaries and prediction export.

The pipeline builds on [DeepEye-SQL](https://github.com/HKUSTDial/DeepEye-SQL)
under the [MIT license](LICENSE). See the [upstream README](UPSTREAM_README.md)
for original documentation and citations. The value-anchor implementation in
this repository is original. See the [AskData paper](https://arxiv.org/abs/2505.19988)
for the design reference.
