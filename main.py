from src.scholarplan.blackboard.database import Blackboard
from src.scholarplan.agent_loop import ScholarPlanAgent


def main():

    print("Starting ScholarPlan...")

    blackboard = Blackboard()

    research_goal = (
        "Investigate the impact of large language models "
        "on academic research."
    )

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

    print("\nScholarPlan pipeline completed.")

    blackboard.close()


if __name__ == "__main__":
    main()