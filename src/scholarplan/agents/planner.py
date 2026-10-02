import json

from src.scholarplan.llm_client import ask_llm


class Planner:
    """Create a structured research plan using an LLM."""

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def create_plan(self, research_goal):

        prompt = f"""
You are the planning agent in ScholarPlan, an academic research assistant.

Your task is to decompose the following research goal into a small number
of clear and useful research tasks.

Research goal:
{research_goal}

Create between 3 and 4 tasks.

IMPORTANT:

Every task must be executable by ScholarPlan using academic sources
retrieved from OpenAlex, Crossref, or arXiv.

Do NOT create tasks involving:
- surveys or interviews
- recruiting participants
- human experiments
- ethics or IRB approval
- proprietary databases
- unsupported APIs
- collecting new data from people

Each task must:

- address a different aspect of the research goal
- be specific enough for a retrieval agent to execute
- focus on finding and analysing existing academic evidence
- contribute directly to answering the research goal
- be concise and practical

For EVERY task, also create a concise academic search query.

The search query must:

- contain approximately 3 to 10 important keywords or short phrases
- focus on the core topic of the task
- be suitable for an OpenAlex keyword search
- NOT contain instructions
- NOT contain long sentences
- NOT contain dates
- NOT contain phrases such as "retrieve papers" or "analyse studies"

Return ONLY valid JSON.

Do not include markdown, explanations, or additional text.

Use exactly this structure:

{{
  "research_goal": "{research_goal}",
  "tasks": [
    {{
      "task_id": 1,
      "description": "Clear research task",
      "search_query": "concise academic search query",
      "status": "pending"
    }}
  ]
}}
"""

        response = ask_llm(prompt)

        try:

            plan = json.loads(response)

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Planner returned invalid JSON: {response}"
            ) from error

        if "research_goal" not in plan:

            raise ValueError(
                "Planner response is missing research_goal."
            )

        if "tasks" not in plan:

            raise ValueError(
                "Planner response is missing tasks."
            )

        if not isinstance(plan["tasks"], list):

            raise ValueError(
                "Planner tasks must be a list."
            )

        for task in plan["tasks"]:

            required_fields = [
                "task_id",
                "description",
                "search_query",
                "status"
            ]

            if not all(
                field in task
                for field in required_fields
            ):

                raise ValueError(
                    "Each planner task must contain "
                    "task_id, description, search_query "
                    "and status."
                )

            if not task["search_query"].strip():

                raise ValueError(
                    "Planner search_query cannot be empty."
                )

        return plan

    def save_plan(self, plan):

        for task in plan["tasks"]:

            self.blackboard.add_task(
                description=task["description"],
                status=task["status"]
            )

    def plan_as_json(self, plan):

        return json.dumps(
            plan,
            indent=2
        )