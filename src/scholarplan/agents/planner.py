import json


class Planner:
    """Create a structured research plan from a research goal."""

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def create_plan(self, research_goal):
        """Create a structured set of research tasks."""

        tasks = [
            {
                "task_id": 1,
                "description": (
                    f"Identify the main applications of the research topic: "
                    f"{research_goal}"
                ),
                "status": "pending"
            },
            {
                "task_id": 2,
                "description": (
                    f"Identify the main benefits and opportunities related to: "
                    f"{research_goal}"
                ),
                "status": "pending"
            },
            {
                "task_id": 3,
                "description": (
                    f"Identify limitations, risks and challenges related to: "
                    f"{research_goal}"
                ),
                "status": "pending"
            },
            {
                "task_id": 4,
                "description": (
                    f"Find academic evidence supporting the main findings about: "
                    f"{research_goal}"
                ),
                "status": "pending"
            }
        ]

        plan = {
            "research_goal": research_goal,
            "tasks": tasks
        }

        return plan

    def save_plan(self, plan):
        """Store the generated research tasks on the blackboard."""

        for task in plan["tasks"]:
            self.blackboard.add_task(
                description=task["description"],
                status=task["status"]
            )

    def plan_as_json(self, plan):
        """Return the plan as JSON."""

        return json.dumps(plan, indent=2)