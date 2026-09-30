from src.scholarplan.blackboard.database import Blackboard


def main():
    print("Starting ScholarPlan...")

    blackboard = Blackboard()

    task_id = blackboard.add_task(
        "Investigate the impact of large language models on academic research."
    )

    blackboard.add_event(
        "system",
        "ScholarPlan blackboard initialized."
    )

    print("Blackboard initialized successfully.")
    print(f"Created task with ID: {task_id}")

    tasks = blackboard.get_tasks()

    print("\nTasks currently stored on the blackboard:")

    for task in tasks:
        print(task)

    blackboard.close()


if __name__ == "__main__":
    main()