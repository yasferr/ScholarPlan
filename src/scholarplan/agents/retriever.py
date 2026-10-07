import requests

from src.scholarplan.embeddings import EmbeddingStore


class Retriever:
    """Retrieve academic sources from OpenAlex."""

    OPENALEX_URL = "https://api.openalex.org/works"

    def __init__(self, blackboard):
        self.blackboard = blackboard

        # The real Blackboard provides a database path.
        # Lightweight fake blackboards used in unit tests may not.
        if hasattr(blackboard, "database_path"):
            self.embedding_store = EmbeddingStore(
                database_path=blackboard.database_path
            )
        else:
            self.embedding_store = None

    def search(self, query, max_results=5):
        print(f"Retriever searching OpenAlex for: {query}")

        response = requests.get(
            self.OPENALEX_URL,
            params={
                "search": query,
                "per-page": max_results
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print(f"Retriever found {len(results)} sources.")

        stored_sources = []

        for result in results:
            title = result.get(
                "display_name",
                "Unknown title"
            )

            authors = ", ".join(
                authorship.get(
                    "author",
                    {}
                ).get(
                    "display_name",
                    ""
                )
                for authorship in result.get(
                    "authorships",
                    []
                )
                if authorship.get("author")
            )

            source_url = ""

            primary_location = result.get(
                "primary_location"
            )

            if primary_location:
                source_url = (
                    primary_location.get(
                        "landing_page_url",
                        ""
                    )
                    or ""
                )

            identifier = (
                result.get("doi")
                or result.get("id", "")
            )

            abstract = ""

            abstract_index = result.get(
                "abstract_inverted_index"
            )

            if abstract_index:
                words = []

                for word, positions in abstract_index.items():
                    for position in positions:
                        words.append(
                            (position, word)
                        )

                words.sort()

                abstract = " ".join(
                    word
                    for _, word in words
                )

            source_id = self.blackboard.add_source(
                title=title,
                authors=authors,
                source_url=source_url,
                identifier=identifier
            )

            embedding_result = None
            duplicate_matches = []

            if self.embedding_store is not None:

                # Create the embedding before storing it.
                vector = self.embedding_store.create_embedding(
                    f"{title}\n\n{abstract}"
                )

                # Compare this source against embeddings that
                # were already stored during the current run.
                duplicate_matches = (
                    self.embedding_store.find_similar(
                        vector=vector,
                        threshold=0.85
                    )
                )

                # Store the new embedding after comparison so
                # that a source does not match itself.
                embedding_id = (
                    self.embedding_store.store_embedding(
                        source_id=source_id,
                        vector=vector
                    )
                )

                embedding_result = {
                    "id": embedding_id,
                    "dimension": len(vector)
                }

            stored_sources.append(
                {
                    "id": source_id,
                    "title": title,
                    "authors": authors,
                    "source_url": source_url,
                    "identifier": identifier,
                    "abstract": abstract,
                    "embedding_id": (
                        embedding_result["id"]
                        if embedding_result
                        else None
                    ),
                    "embedding_dimension": (
                        embedding_result["dimension"]
                        if embedding_result
                        else None
                    ),
                    "duplicate_matches": duplicate_matches
                }
            )

        return stored_sources

    def close(self):
        """Close the embedding store."""

        if self.embedding_store is not None:
            self.embedding_store.close()