from src.scholarplan.agents.archivist import Archivist


class FakeBlackboard:
    def __init__(self):
        self.run_id = "test-run-123"

    def get_tasks(self):
        return [
            (
                1,
                "Investigate LLM use in academic research.",
                "pending"
            )
        ]

    def get_sources(self):
        return [
            (
                1,
                "LLMs in Academic Research",
                "Test Author",
                "https://example.com/paper",
                "doi:10.1234/example"
            )
        ]

    def get_claims(self):
        return [
            (
                1,
                "LLMs can support academic literature discovery.",
                1,
                "SUPPORTED"
            )
        ]

    def get_feedback(self):
        return [
            (
                1,
                1,
                "Verdict: SUPPORTED\n"
                "Relevance: RELEVANT\n"
                "Feedback: The evidence supports the claim."
            )
        ]

    def get_events(self):
        return [
            (
                1,
                "Observation",
                "Academic sources retrieved."
            ),
            (
                2,
                "Decision",
                "Evidence sufficient."
            )
        ]


def test_archivist_builds_report(tmp_path):
    blackboard = FakeBlackboard()

    archivist = Archivist(
        blackboard=blackboard,
        output_directory=tmp_path
    )

    report = archivist.build_report(
        research_goal=(
            "Investigate the impact of large language models "
            "on academic research."
        ),
        status="completed",
        iterations=2
    )

    assert "# ScholarPlan Research Report" in report

    assert "## Research Goal" in report

    assert (
        "Investigate the impact of large language models "
        "on academic research."
    ) in report

    assert "## Verified Findings" in report

    assert (
        "LLMs can support academic literature discovery."
    ) in report

    assert "SUPPORTED" in report

    assert "## Academic Sources" in report

    assert "LLMs in Academic Research" in report

    assert "## Execution Trace Summary" in report

    assert "Academic sources retrieved." in report


def test_archivist_writes_bibtex(tmp_path):
    blackboard = FakeBlackboard()

    archivist = Archivist(
        blackboard=blackboard,
        output_directory=tmp_path
    )

    bibtex_path = archivist.write_bibtex()

    assert bibtex_path.exists()

    content = bibtex_path.read_text(
        encoding="utf-8"
    )

    assert "@misc{source1," in content
    assert "LLMs in Academic Research" in content
    assert "Test Author" in content
    assert "doi:10.1234/example" in content
    assert "https://example.com/paper" in content


def test_archivist_writes_execution_trace(tmp_path):
    blackboard = FakeBlackboard()

    archivist = Archivist(
        blackboard=blackboard,
        output_directory=tmp_path
    )

    trace_path = archivist.write_execution_trace()

    assert trace_path.exists()

    content = trace_path.read_text(
        encoding="utf-8"
    )

    assert "Academic sources retrieved." in content
    assert "Evidence sufficient." in content
    assert '"event_type": "Observation"' in content
    assert '"event_type": "Decision"' in content