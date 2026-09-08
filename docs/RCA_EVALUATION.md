# RCA Evaluation

The evaluation harness is in `backend/evaluation/`. It is deliberately dependency-injected so tests can use the production retriever and RCA functions without changing their contracts.

## Method

Each case hides the expected labels from the analysis function. The harness measures Recall@1, Recall@5, MRR, root-cause accuracy, resolution accuracy, evidence accuracy, and unsupported-claim rate. Cases with no expected label are excluded from that RCA accuracy denominator and remain visible in the per-case output.

`backend/evaluation/cases.json` contains deterministic edge-case scenarios. Empty `relevant_incident_ids` and null expected labels are intentional until a real labelled incident corpus is supplied; the harness never fabricates scores for them.

## Running an evaluation

Provide adapters around the production retriever and RCA endpoint, then call `evaluate_cases`. Serialize `EvaluationReport.to_dict()` to an artifact outside source control. Do not hand-edit or report metrics from an unexecuted run.

## Limitations

The repository does not currently contain a labelled holdout set with verified root causes and resolutions. Therefore no production evaluation metrics are reported in this repository yet.
