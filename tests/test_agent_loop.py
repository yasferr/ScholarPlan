from src.scholarplan.agent_loop import ScholarPlanAgent


class FakeBlackboard:
    def __init__(self):
        self.tasks = []
        self.sources = []
        self.claims = []
        self.feedback = []
        self.events = []

    def add_task(self, description, status="pending"):
        task_id = len(self.tasks) + 1

        self.tasks.append(
            (task_id, description, status)
        )

        return task_id

    def get_tasks(self):
        return self.tasks

    def add_source(
        self,
        title,
        authors="",
        source_url="",
        identifier=""
    ):
        source_id = len(self.sources) + 1

        self.sources.append(
            (
                source_id,
                title,
                authors,
                source_url,
                identifier
            )
        )

        return source_id

    def get_sources(self):
        return self.sources

    def add_claim(
        self,
        claim,
        source_id=None,
        status="pending"
    ):
        claim_id = len(self.claims) + 1

        self.claims.append(
            (
                claim_id,
                claim,
                source_id,
                status
            )
        )

        return claim_id

    def update_claim_status(
        self,
        claim_id,
        status
    ):
        updated_claims = []

        for (
            existing_id,
            claim,
            source_id,
            existing_status
        ) in self.claims:

            if existing_id == claim_id:
                existing_status = status

            updated_claims.append(
                (
                    existing_id,
                    claim,
                    source_id,
                    existing_status
                )
            )

        self.claims = updated_claims

    def get_claims(self):
        return self.claims

    def add_feedback(
        self,
        claim_id,
        message
    ):
        feedback_id = len(self.feedback) + 1

        self.feedback.append(
            (
                feedback_id,
                claim_id,
                message
            )
        )

        return feedback_id

    def get_feedback(self):
        return self.feedback

    def add_event(
        self,
        event_type,
        message
    ):
        event_id = len(self.events) + 1

        self.events.append(
            (
                event_id,
                event_type,
                message
            )
        )


class FakeArchivist:

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def archive(
        self,
        research_goal,
        status,
        iterations
    ):
        return {
            "research_report": "test_report.md",
            "references": "test_references.bib",
            "execution_trace": "test_trace.json"
        }


def test_complete_agent_pipeline(monkeypatch):

    planner_response = """
    {
        "research_goal": "Investigate the impact of large language models on academic research.",
        "tasks": [
            {
                "task_id": 1,
                "description": "Investigate LLM use in academic research.",
                "search_query": "LLM academic research",
                "status": "pending"
            }
        ]
    }
    """

    processor_response = """
    {
        "research_goal": "Investigate the impact of large language models on academic research.",
        "claims": [
            {
                "claim": "LLMs can support academic literature discovery.",
                "source_ids": [1],
                "evidence": "The retrieved academic source discusses LLM support for literature discovery."
            }
        ]
    }
    """

    critic_response = """
    {
        "claim": "LLMs can support academic literature discovery.",
        "verdict": "SUPPORTED",
        "relevance": "RELEVANT",
        "feedback": "The academic evidence supports the claim.",
        "source_ids": [1]
    }
    """

    def fake_llm(prompt):

        if "planning agent" in prompt:
            return planner_response

        if "processing agent" in prompt:
            return processor_response

        if "Critic Agent" in prompt:
            return critic_response

        raise AssertionError(
            "Unexpected LLM prompt."
        )

    monkeypatch.setattr(
        "src.scholarplan.agents.planner.ask_llm",
        fake_llm
    )

    monkeypatch.setattr(
        "src.scholarplan.agents.processor.ask_llm",
        fake_llm
    )

    monkeypatch.setattr(
        "src.scholarplan.agents.critic.ask_llm",
        fake_llm
    )

    def fake_search(
        self,
        query,
        max_results=5
    ):
        sources = []

        for index in range(5):

            source = {
                "id": None,
                "title": (
                    f"LLMs in Academic Research "
                    f"Paper {index + 1}"
                ),
                "authors": f"Test Author {index + 1}",
                "source_url": (
                    f"https://example.com/paper{index + 1}"
                ),
                "identifier": (
                    f"doi:10.1234/example{index + 1}"
                ),
                "abstract": (
                    "This academic source examines "
                    "the use of large language models "
                    "in academic research."
                )
            }

            source_id = self.blackboard.add_source(
                title=source["title"],
                authors=source["authors"],
                source_url=source["source_url"],
                identifier=source["identifier"]
            )

            source["id"] = source_id

            sources.append(source)

        return sources

    monkeypatch.setattr(
        "src.scholarplan.agents.retriever.Retriever.search",
        fake_search
    )

    blackboard = FakeBlackboard()

    agent = ScholarPlanAgent(
        blackboard
    )

    agent.archivist = FakeArchivist(
        blackboard
    )

    result = agent.run(
        "Investigate the impact of large language models on academic research."
    )

    assert result["status"] == "completed"

    assert result["iterations"] >= 2

    assert len(result["sources"]) >= 10

    assert len(result["claims"]) >= 2

    assert len(result["critic_results"]) >= 2

    assert (
        result["critic_results"][0]["verdict"]
        == "SUPPORTED"
    )

    assert (
        result["archive"]["research_report"]
        == "test_report.md"
    )

    assert (
        result["archive"]["references"]
        == "test_references.bib"
    )

    assert (
        result["archive"]["execution_trace"]
        == "test_trace.json"
    )