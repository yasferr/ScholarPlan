import json

from src.scholarplan.llm_client import ask_llm


class Planner:
    """
    Planner agent responsible for decomposing a research goal into
    executable academic research tasks.

    The Planner uses the LLM to create a structured research plan.

    During replanning, Critic feedback from the current run is supplied
    to the LLM so that subsequent research iterations can address
    identified evidence gaps instead of simply repeating the same plan.
    """

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def create_plan(self, research_goal, feedback=None):
        """
        Create a research plan for the supplied research goal.

        The Planner accepts optional Critic feedback so that replanning
        can respond to weaknesses identified during earlier iterations.
        """

        feedback_section = ""

        if feedback:
            feedback_messages = "\n".join(
                f"- {message}"
                for message in feedback
            )

            feedback_section = f"""
Previous Critic feedback from the current research run:

{feedback_messages}

Use this feedback to improve the revised research plan.

The revised plan should:
- address evidence gaps identified by the Critic
- avoid approaches that previously produced irrelevant evidence
- refine or broaden search queries when appropriate
- focus on unresolved aspects of the research goal
"""

        prompt = f"""
You are the planning agent in ScholarPlan, an academic research assistant.

Your responsibility is to decompose the research goal into concrete
research tasks that can be executed by the system.

Research goal:
{research_goal}

{feedback_section}

Create between 3 and 4 research tasks.

Each task must contain:

- "task_id": a unique integer identifier
- "description": a concise description of what should be investigated
- "search_query": a concise academic search query
- "status": "pending"

Requirements:

- Tasks must collectively address the research goal.
- Search queries must contain meaningful academic keywords.
- Avoid duplicate or near-duplicate tasks.
- Prefer complementary research perspectives.
- Each task must be independently executable by the Retriever.
- If Critic feedback is provided, use it to improve the new plan.
- Return ONLY valid JSON.

Use this structure:

{{
    "research_goal": "{research_goal}",
    "tasks": [
        {{
            "task_id": 1,
            "description": "Research task description",
            "search_query": "academic search query",
            "status": "pending"
        }},
        {{
            "task_id": 2,
            "description": "Research task description",
            "search_query": "academic search query",
            "status": "pending"
        }},
        {{
            "task_id": 3,
            "description": "Research task description",
            "search_query": "academic search query",
            "status": "pending"
        }}
    ]
}}
"""

        response = ask_llm(prompt)

        try:
            plan = json.loads(response)
        except json.JSONDecodeError as exc:
            raise ValueError("Planner returned invalid JSON.") from exc

        if not isinstance(plan, dict):
            raise ValueError("Planner response must be a JSON object.")

        tasks = plan.get("tasks")

        if not isinstance(tasks, list):
            raise ValueError(
                "Planner response must contain a 'tasks' list."
            )

        if not 1 <= len(tasks) <= 4:
            raise ValueError(
                "Planner must return between 1 and 4 tasks."
            )

        for task in tasks:

            if not isinstance(task, dict):
                raise ValueError(
                    "Each planner task must be a JSON object."
                )

            if not task.get("description"):
                raise ValueError(
                    "description cannot be empty"
                )

            if not task.get("search_query"):
                raise ValueError(
                    "search_query cannot be empty"
                )

        return plan

    def save_plan(self, plan):
        """
        Store the generated plan in the shared blackboard.

        The production Blackboard and the functional-test FakeBlackboard
        expose slightly different add_task interfaces. Supporting both
        keeps the test double lightweight without changing production
        database behaviour.
        """

        for task in plan["tasks"]:

            try:
                self.blackboard.add_task(
                    task=task["description"],
                    search_query=task["search_query"]
                )

            except TypeError:
                self.blackboard.add_task(
                    task["description"],
                    task["search_query"]
                )