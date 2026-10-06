from src.scholarplan.agents.critic import Critic


class FakeBlackboard:
    def __init__(self):
        self.updated_claims = []
        self.feedback = []

    def update_claim_status(self, claim_id, status):
        self.updated_claims.append(
            (claim_id, status)
        )

    def add_feedback(self, claim_id, message):
        self.feedback.append(
            (claim_id, message)
        )


def create_claim():
    return {
        "id": 1,
        "claim": "LLMs can support academic literature discovery.",
        "source_ids": [10],
        "evidence": (
            "The paper reports that LLM-based tools can "
            "assist researchers with literature discovery."
        )
    }


def create_sources():
    return [
        {
            "id": 10,
            "title": "LLMs and Academic Research",
            "authors": "Test Author",
            "source_url": "https://example.com/paper",
            "abstract": (
                "This study examines the use of large language "
                "models in academic research and literature discovery."
            )
        }
    ]


def test_critic_accepts_supported_claim(monkeypatch):
    valid_response = """
    {
        "claim": "LLMs can support academic literature discovery.",
        "verdict": "SUPPORTED",
        "relevance": "RELEVANT",
        "feedback": "The source directly supports the claim.",
        "source_ids": [10]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.critic.ask_llm",
        lambda prompt: valid_response
    )

    blackboard = FakeBlackboard()
    critic = Critic(blackboard)

    result = critic.evaluate_claim(
        claim=create_claim(),
        sources=create_sources(),
        research_goal=(
            "Investigate the impact of large language models "
            "on academic research."
        )
    )

    assert result["verdict"] == "SUPPORTED"
    assert result["relevance"] == "RELEVANT"

    assert blackboard.updated_claims == [
        (1, "SUPPORTED")
    ]

    assert len(blackboard.feedback) == 1
    assert blackboard.feedback[0][0] == 1


def test_critic_rejects_irrelevant_claim(monkeypatch):
    valid_response = """
    {
        "claim": "LLMs perform well on multilingual tasks.",
        "verdict": "IRRELEVANT",
        "relevance": "IRRELEVANT",
        "feedback": "The claim does not directly address academic research.",
        "source_ids": [10]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.critic.ask_llm",
        lambda prompt: valid_response
    )

    blackboard = FakeBlackboard()
    critic = Critic(blackboard)

    claim = create_claim()

    claim["claim"] = (
        "LLMs perform well on multilingual tasks."
    )

    result = critic.evaluate_claim(
        claim=claim,
        sources=create_sources(),
        research_goal=(
            "Investigate the impact of large language models "
            "on academic research."
        )
    )

    assert result["verdict"] == "IRRELEVANT"
    assert result["relevance"] == "IRRELEVANT"

    assert blackboard.updated_claims == [
        (1, "IRRELEVANT")
    ]


def test_critic_rejects_invalid_json(monkeypatch):
    monkeypatch.setattr(
        "src.scholarplan.agents.critic.ask_llm",
        lambda prompt: "This is not valid JSON."
    )

    blackboard = FakeBlackboard()
    critic = Critic(blackboard)

    try:
        critic.evaluate_claim(
            claim=create_claim(),
            sources=create_sources(),
            research_goal=(
                "Investigate the impact of large language models "
                "on academic research."
            )
        )

        assert False, "Critic should reject invalid JSON."

    except ValueError as error:
        assert "invalid JSON" in str(error)