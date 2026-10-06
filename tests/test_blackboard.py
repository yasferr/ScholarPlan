from src.scholarplan.blackboard.database import Blackboard


def test_blackboard_stores_task(tmp_path):
    database_path = tmp_path / "test.db"

    blackboard = Blackboard(database_path)

    task_id = blackboard.add_task(
        "Investigate the impact of LLMs on academic research."
    )

    tasks = blackboard.get_tasks()

    assert len(tasks) == 1
    assert tasks[0][0] == task_id
    assert tasks[0][1] == (
        "Investigate the impact of LLMs on academic research."
    )
    assert tasks[0][2] == "pending"

    blackboard.close()


def test_blackboard_stores_source(tmp_path):
    database_path = tmp_path / "test.db"

    blackboard = Blackboard(database_path)

    source_id = blackboard.add_source(
        title="Example Academic Paper",
        authors="Test Author",
        source_url="https://example.com/paper",
        identifier="doi:10.1234/example"
    )

    sources = blackboard.get_sources()

    assert len(sources) == 1
    assert sources[0][0] == source_id
    assert sources[0][1] == "Example Academic Paper"
    assert sources[0][2] == "Test Author"
    assert sources[0][3] == "https://example.com/paper"
    assert sources[0][4] == "doi:10.1234/example"

    blackboard.close()


def test_claim_status_and_feedback(tmp_path):
    database_path = tmp_path / "test.db"

    blackboard = Blackboard(database_path)

    claim_id = blackboard.add_claim(
        claim="LLMs can support literature discovery.",
        status="pending"
    )

    blackboard.update_claim_status(
        claim_id,
        "SUPPORTED"
    )

    blackboard.add_feedback(
        claim_id,
        "The provided evidence supports the claim."
    )

    claims = blackboard.get_claims()
    feedback = blackboard.get_feedback()

    assert claims[0][0] == claim_id
    assert claims[0][1] == (
        "LLMs can support literature discovery."
    )
    assert claims[0][3] == "SUPPORTED"

    assert len(feedback) == 1
    assert feedback[0][1] == claim_id
    assert feedback[0][2] == (
        "The provided evidence supports the claim."
    )

    blackboard.close()


def test_runs_are_isolated(tmp_path):
    database_path = tmp_path / "test.db"

    first_run = Blackboard(database_path)

    first_run.add_task(
        "Task belonging to the first run."
    )

    first_run.add_source(
        title="First run source"
    )

    first_run.close()

    second_run = Blackboard(database_path)

    second_run.add_task(
        "Task belonging to the second run."
    )

    second_run.add_source(
        title="Second run source"
    )

    tasks = second_run.get_tasks()
    sources = second_run.get_sources()

    assert len(tasks) == 1
    assert tasks[0][1] == (
        "Task belonging to the second run."
    )

    assert len(sources) == 1
    assert sources[0][1] == "Second run source"

    second_run.close()