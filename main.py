from src.scholarplan.blackboard.database import Blackboard
from src.scholarplan.agent_loop import ScholarPlanAgent

from evaluation.evaluation_metrics import (
    calculate_metrics,
    save_metrics
)


def main():
    print("Starting ScholarPlan...")

    blackboard = Blackboard()

    research_goal = (
        "Investigate the impact of large language models "
        "on academic research."
    )

    try:
        agent = ScholarPlanAgent(blackboard)

        result = agent.run(research_goal)

        print("\n")
        print("=" * 60)
        print("SCHOLARPLAN FINAL STATUS")
        print("=" * 60)

        print(f"Status: {result['status']}")
        print(f"Iterations executed: {result['iterations']}")
        print(f"Sources retrieved: {len(result['sources'])}")
        print(f"Claims generated: {len(result['claims'])}")

        # Calculate quantitative evaluation metrics.
        metrics = calculate_metrics(result)

        # Save metrics for the current execution.
        metrics_path = save_metrics(metrics)

        print("\n")
        print("=" * 60)
        print("SCHOLARPLAN EVALUATION")
        print("=" * 60)

        print(f"Claims evaluated: {metrics['claims_evaluated']}")
        print(f"Supported claims: {metrics['supported_claims']}")
        print(f"Unsupported claims: {metrics['not_supported_claims']}")
        print(f"Irrelevant claims: {metrics['irrelevant_claims']}")
        print(
            "Insufficient evidence: "
            f"{metrics['insufficient_evidence_claims']}"
        )
        print(f"Support rate: {metrics['support_rate']:.1%}")

        print(f"\nEvaluation saved to: {metrics_path}")
        print("\nScholarPlan pipeline completed.")

    finally:
        blackboard.close()


if __name__ == "__main__":
    main()