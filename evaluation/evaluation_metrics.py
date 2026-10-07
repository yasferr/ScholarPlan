import json
from pathlib import Path


def calculate_metrics(result):
    """Calculate evaluation metrics from a ScholarPlan run."""

    critic_results = result.get("critic_results", [])

    total_claims = len(critic_results)

    supported_claims = sum(
        1
        for item in critic_results
        if item.get("verdict") == "SUPPORTED"
    )

    not_supported_claims = sum(
        1
        for item in critic_results
        if item.get("verdict") == "NOT_SUPPORTED"
    )

    insufficient_evidence_claims = sum(
        1
        for item in critic_results
        if item.get("verdict") == "INSUFFICIENT_EVIDENCE"
    )

    irrelevant_claims = sum(
        1
        for item in critic_results
        if item.get("verdict") == "IRRELEVANT"
    )

    support_rate = (
        supported_claims / total_claims
        if total_claims > 0
        else 0
    )

    # Embedding-based source similarity metrics.
    sources = result.get("sources", [])

    sources_with_embeddings = sum(
        1
        for source in sources
        if source.get("embedding_id") is not None
    )

    potential_duplicate_matches = sum(
        len(source.get("duplicate_matches", []))
        for source in sources
    )

    sources_with_duplicate_matches = sum(
        1
        for source in sources
        if source.get("duplicate_matches")
    )

    embedding_coverage = (
        sources_with_embeddings / len(sources)
        if sources
        else 0
    )

    duplicate_rate = (
        sources_with_duplicate_matches / len(sources)
        if sources
        else 0
    )

    return {
        "status": result.get("status"),
        "iterations": result.get("iterations", 0),
        "sources_retrieved": len(sources),
        "claims_generated": len(result.get("claims", [])),
        "claims_evaluated": total_claims,
        "supported_claims": supported_claims,
        "not_supported_claims": not_supported_claims,
        "insufficient_evidence_claims": (
            insufficient_evidence_claims
        ),
        "irrelevant_claims": irrelevant_claims,
        "support_rate": round(support_rate, 3),
        "sources_with_embeddings": sources_with_embeddings,
        "embedding_coverage": round(embedding_coverage, 3),
        "potential_duplicate_matches": (
            potential_duplicate_matches
        ),
        "sources_with_duplicate_matches": (
            sources_with_duplicate_matches
        ),
        "duplicate_rate": round(duplicate_rate, 3)
    }


def save_metrics(
    metrics,
    output_path="outputs/evaluation_metrics.json"
):
    """Save evaluation metrics as JSON."""

    path = Path(output_path)
    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            metrics,
            indent=2
        ),
        encoding="utf-8"
    )

    return path


if __name__ == "__main__":
    print(
        "Evaluation metrics module loaded successfully."
    )