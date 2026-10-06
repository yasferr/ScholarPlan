from src.scholarplan.agents.processor import Processor


class FakeBlackboard:
    def __init__(self):
        self.claims = []

    def add_claim(
        self,
        claim,
        source_id=None,
        status="pending"
    ):
        claim_id = len(self.claims) + 1

        self.claims.append(
            {
                "id": claim_id,
                "claim": claim,
                "source_id": source_id,
                "status": status
            }
        )

        return claim_id


def create_sources():
    return [
        {
            "id": 1,
            "title": "LLMs in Academic Research",
            "authors": "Test Author",
            "source_url": "https://example.com/paper",
            "identifier": "doi:10.1234/example",
            "abstract": (
                "This paper examines how large language models "
                "can support academic research."
            )
        }
    ]


def test_processor_generates_and_stores_claims(monkeypatch):
    valid_response = """
    {
        "research_goal": "Investigate the impact of large language models on academic research.",
        "claims": [
            {
                "claim": "LLMs can support academic literature discovery.",
                "source_ids": [1],
                "evidence": "The source discusses the use of LLMs for literature discovery."
            },
            {
                "claim": "LLMs can assist researchers with academic writing.",
                "source_ids": [1],
                "evidence": "The source describes LLM assistance for academic writing."
            }
        ]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.processor.ask_llm",
        lambda prompt: valid_response
    )

    blackboard = FakeBlackboard()
    processor = Processor(blackboard)

    result = processor.process_sources(
        sources=create_sources(),
        research_goal=(
            "Investigate the impact of large language models "
            "on academic research."
        )
    )

    assert len(result["claims"]) == 2

    assert result["claims"][0]["claim"] == (
        "LLMs can support academic literature discovery."
    )

    assert result["claims"][1]["claim"] == (
        "LLMs can assist researchers with academic writing."
    )

    assert len(blackboard.claims) == 2

    assert blackboard.claims[0]["status"] == "pending"
    assert blackboard.claims[1]["status"] == "pending"


def test_processor_requires_source_ids(monkeypatch):
    invalid_response = """
    {
        "research_goal": "Investigate LLMs in academic research.",
        "claims": [
            {
                "claim": "LLMs can support researchers.",
                "source_ids": [],
                "evidence": "Some evidence."
            }
        ]
    }
    """

    monkeypatch.setattr(
        "src.scholarplan.agents.processor.ask_llm",
        lambda prompt: invalid_response
    )

    blackboard = FakeBlackboard()
    processor = Processor(blackboard)

    try:
        processor.process_sources(
            sources=create_sources(),
            research_goal=(
                "Investigate LLMs in academic research."
            )
        )

        assert False, "Processor should reject claims without sources."

    except ValueError as error:
        assert "at least one source" in str(error)


def test_processor_rejects_invalid_json(monkeypatch):
    monkeypatch.setattr(
        "src.scholarplan.agents.processor.ask_llm",
        lambda prompt: "This is not valid JSON."
    )

    blackboard = FakeBlackboard()
    processor = Processor(blackboard)

    try:
        processor.process_sources(
            sources=create_sources(),
            research_goal=(
                "Investigate LLMs in academic research."
            )
        )

        assert False, "Processor should reject invalid JSON."

    except ValueError as error:
        assert "invalid JSON" in str(error)