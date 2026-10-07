from evaluation.evaluation_metrics import calculate_metrics


def test_calculate_metrics():
    """Evaluation metrics should correctly summarize Critic results."""

    result = {
        "status": "completed",
        "iterations": 3,
        "sources": [
            {
                "id": 1,
                "embedding_id": 1,
                "duplicate_matches": []
            },
            {
                "id": 2,
                "embedding_id": 2,
                "duplicate_matches": [
                    {
                        "source_id": 1,
                        "similarity": 0.91
                    }
                ]
            },
            {
                "id": 3,
                "embedding_id": 3,
                "duplicate_matches": []
            }
        ],
        "claims": [
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4}
        ],
        "critic_results": [
            {"verdict": "SUPPORTED"},
            {"verdict": "SUPPORTED"},
            {"verdict": "IRRELEVANT"},
            {"verdict": "INSUFFICIENT_EVIDENCE"}
        ]
    }

    metrics = calculate_metrics(result)

    assert metrics["status"] == "completed"
    assert metrics["iterations"] == 3
    assert metrics["sources_retrieved"] == 3

    assert metrics["claims_generated"] == 4
    assert metrics["claims_evaluated"] == 4

    assert metrics["supported_claims"] == 2
    assert metrics["not_supported_claims"] == 0
    assert metrics["insufficient_evidence_claims"] == 1
    assert metrics["irrelevant_claims"] == 1

    assert metrics["support_rate"] == 0.5

    assert metrics["sources_with_embeddings"] == 3
    assert metrics["embedding_coverage"] == 1.0

    assert metrics["potential_duplicate_matches"] == 1
    assert metrics["sources_with_duplicate_matches"] == 1
    assert metrics["duplicate_rate"] == round(1 / 3, 3)