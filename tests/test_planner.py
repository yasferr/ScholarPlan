from src.scholarplan.agents.planner import Planner


def test_planner_accepts_valid_json(monkeypatch):
    valid_response = """
    {
        "research_goal": "Investigate the impact of large language models on academic research.",
        "tasks": [
            {
                "task_id": 1,
                "description": "Investigate LLM use in academic literature discovery.",
                "search_query": "LLM academic literature discovery",
                "status": "pending"
            },
            {
                "task_id": 2,
                "description": "Investigate the effect of LLMs on researcher productivity.",
                "search_query": "LLM researcher productivity academic research",
                "status": "pending"
            },
            {
                "task_id": 3,
                "description": "Investigate risks of LLM use in academic research.",
                "search_query": "LLM risks academic research",
                "status": "pending"
            }
        ]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.planner.ask_llm",
        lambda prompt: valid_response
    )

    planner = Planner(blackboard=None)

    plan = planner.create_plan(
        "Investigate the impact of large language models on academic research."
    )

    assert "research_goal" in plan
    assert "tasks" in plan
    assert len(plan["tasks"]) == 3

    for task in plan["tasks"]:
        assert "task_id" in task
        assert "description" in task
        assert "search_query" in task
        assert "status" in task
        assert task["search_query"].strip()


def test_planner_rejects_invalid_json(monkeypatch):
    invalid_response = "This is not valid JSON."

    monkeypatch.setattr(
        "src.scholarplan.agents.planner.ask_llm",
        lambda prompt: invalid_response
    )

    planner = Planner(blackboard=None)

    try:
        planner.create_plan(
            "Investigate the impact of large language models on academic research."
        )
        assert False, "Planner should reject invalid JSON."
    except ValueError as error:
        assert "invalid JSON" in str(error)


def test_planner_rejects_missing_search_query(monkeypatch):
    invalid_response = """
    {
        "research_goal": "Investigate LLMs in academic research.",
        "tasks": [
            {
                "task_id": 1,
                "description": "Investigate LLM use.",
                "search_query": "",
                "status": "pending"
            }
        ]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.planner.ask_llm",
        lambda prompt: invalid_response
    )

    planner = Planner(blackboard=None)

    try:
        planner.create_plan(
            "Investigate LLMs in academic research."
        )
        assert False, "Planner should reject an empty search query."
    except ValueError as error:
        assert "search_query cannot be empty" in str(error)