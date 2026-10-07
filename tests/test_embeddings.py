import numpy as np

from src.scholarplan.embeddings import EmbeddingStore


def test_embedding_dimension(tmp_path):
    """Embeddings should have the expected 384 dimensions."""

    database_path = tmp_path / "test.db"

    store = EmbeddingStore(
        database_path=database_path
    )

    vector = store.create_embedding(
        "Large language models can support academic research."
    )

    assert len(vector) == 384

    store.close()


def test_related_text_has_higher_similarity(tmp_path):
    """Related research text should be more similar than unrelated text."""

    database_path = tmp_path / "test.db"

    store = EmbeddingStore(
        database_path=database_path
    )

    research_text = (
        "Large language models can support academic "
        "research and literature discovery."
    )

    related_text = (
        "LLMs can assist researchers with finding "
        "and reviewing academic literature."
    )

    unrelated_text = (
        "The weather in Milan is warm and sunny today."
    )

    research_vector = store.create_embedding(research_text)
    related_vector = store.create_embedding(related_text)
    unrelated_vector = store.create_embedding(unrelated_text)

    related_similarity = float(
        np.dot(research_vector, related_vector)
    )

    unrelated_similarity = float(
        np.dot(research_vector, unrelated_vector)
    )

    assert related_similarity > unrelated_similarity

    store.close()


def test_embedding_can_be_stored_and_retrieved(tmp_path):
    """Stored embeddings should be retrievable from SQLite."""

    database_path = tmp_path / "test.db"

    store = EmbeddingStore(
        database_path=database_path
    )

    vector = store.create_embedding(
        "Artificial intelligence supports academic research."
    )

    embedding_id = store.store_embedding(
        source_id=123,
        vector=vector
    )

    embeddings = store.get_embeddings()

    assert embedding_id > 0
    assert len(embeddings) == 1
    assert embeddings[0]["source_id"] == 123
    assert embeddings[0]["dimension"] == 384

    store.close()