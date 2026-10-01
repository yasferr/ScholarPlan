from src.scholarplan.blackboard.database import Blackboard
from src.scholarplan.agents.planner import Planner
from src.scholarplan.agents.retriever import Retriever


def main():
    print("Starting ScholarPlan...")

    blackboard = Blackboard()

    research_goal = (
        "Investigate the impact of large language models "
        "on academic research."
    )

    print(f"\nResearch goal:\n{research_goal}")

    # Step 1: Create research plan
    planner = Planner(blackboard)

    plan = planner.create_plan(research_goal)

    print("\nResearch plan created:")

    for task in plan["tasks"]:
        print(
            f"Task {task['task_id']}: "
            f"{task['description']}"
        )

    planner.save_plan(plan)

    # Step 2: Retrieve sources for the research goal
    retriever = Retriever(blackboard)

    sources = retriever.search(
        research_goal,
        max_results=5
    )

    print("\nSources retrieved:")

    for source in sources:
        print(f"- {source['title']}")

    print("\nScholarPlan pipeline completed successfully.")

    blackboard.close()


if __name__ == "__main__":
    main()