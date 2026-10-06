from src.scholarplan.agents.retriever import Retriever


def test_retriever_stores_sources(monkeypatch):
    fake_response = {
        "results": [
            {
                "display_name": "Large Language Models in Academic Research",
                "authorships": [
                    {
                        "author": {
                            "display_name": "Test Author"
                        }
                    }
                ],
                "primary_location": {
                    "landing_page_url": "https://example.com/paper"
                },
                "doi": "https://doi.org/10.1234/example",
                "id": "https://openalex.org/W123456",
                "abstract_inverted_index": {
                    "Large": [0],
                    "language": [1],
                    "models": [2],
                    "support": [3],
                    "research": [4]
                }
            }
        ]
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_response

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "src.scholarplan.agents.retriever.requests.get",
        fake_get
    )

    class FakeBlackboard:
        def __init__(self):
            self.sources = []

        def add_source(
            self,
            title,
            authors="",
            source_url="",
            identifier=""
        ):
            source_id = len(self.sources) + 1

            self.sources.append(
                {
                    "id": source_id,
                    "title": title,
                    "authors": authors,
                    "source_url": source_url,
                    "identifier": identifier
                }
            )

            return source_id

    blackboard = FakeBlackboard()

    retriever = Retriever(blackboard)

    sources = retriever.search(
        "large language models academic research"
    )

    assert len(sources) == 1

    assert sources[0]["title"] == (
        "Large Language Models in Academic Research"
    )

    assert sources[0]["authors"] == "Test Author"

    assert sources[0]["source_url"] == (
        "https://example.com/paper"
    )

    assert sources[0]["identifier"] == (
        "https://doi.org/10.1234/example"
    )

    assert sources[0]["abstract"] == (
        "Large language models support research"
    )

    assert len(blackboard.sources) == 1


def test_retriever_handles_multiple_sources(monkeypatch):
    fake_response = {
        "results": [
            {
                "display_name": "Paper One",
                "authorships": [],
                "primary_location": {},
                "doi": "doi:one",
                "id": "openalex:one"
            },
            {
                "display_name": "Paper Two",
                "authorships": [],
                "primary_location": {},
                "doi": "doi:two",
                "id": "openalex:two"
            }
        ]
    }

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return fake_response

    monkeypatch.setattr(
        "src.scholarplan.agents.retriever.requests.get",
        lambda *args, **kwargs: FakeResponse()
    )

    class FakeBlackboard:
        def __init__(self):
            self.next_id = 1

        def add_source(
            self,
            title,
            authors="",
            source_url="",
            identifier=""
        ):
            source_id = self.next_id
            self.next_id += 1
            return source_id

    retriever = Retriever(FakeBlackboard())

    sources = retriever.search(
        "academic research",
        max_results=2
    )

    assert len(sources) == 2
    assert sources[0]["title"] == "Paper One"
    assert sources[1]["title"] == "Paper Two"


def test_retriever_raises_api_error(monkeypatch):
    def fake_get(*args, **kwargs):
        raise ConnectionError(
            "OpenAlex connection failed"
        )

    monkeypatch.setattr(
        "src.scholarplan.agents.retriever.requests.get",
        fake_get
    )

    class FakeBlackboard:
        pass

    retriever = Retriever(FakeBlackboard())

    try:
        retriever.search(
            "large language models"
        )
        assert False, "Retriever should raise the API error."
    except ConnectionError as error:
        assert "OpenAlex connection failed" in str(error)