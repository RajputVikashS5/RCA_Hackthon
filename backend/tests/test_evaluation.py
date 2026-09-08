from evaluation.runner import EvaluationCase, evaluate_cases


def test_evaluation_reports_retrieval_and_groundedness_metrics():
    case = EvaluationCase(
        case_id="known",
        description="payment failure",
        relevant_incident_ids=("INC-1",),
        expected_root_cause="pool exhaustion",
        expected_resolution="increase pool",
        expected_behavior="Use the known incident.",
    )

    report = evaluate_cases(
        [case],
        retrieve=lambda _: [{"incident_id": "INC-1"}],
        analyze=lambda _, __: {
            "root_cause": "pool exhaustion",
            "resolution": "increase pool",
            "supporting_incident_ids": ["INC-1"],
            "unsupported_claims": False,
        },
    )

    assert report.retrieval == {"recall_at_1": 1.0, "recall_at_5": 1.0, "mrr": 1.0}
    assert report.rca["root_cause_accuracy"] == 1.0
    assert report.rca["unsupported_claim_rate"] == 0.0
