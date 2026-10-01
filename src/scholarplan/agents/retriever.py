import requests


class Retriever:
    """Retrieve academic sources from OpenAlex."""

    OPENALEX_URL = "https://api.openalex.org/works"

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def search(self, query, max_results=5):
        """Search OpenAlex and store the results on the blackboard."""

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
            title = result.get("display_name", "Unknown title")

            authors = ", ".join(
                authorship.get("author", {}).get("display_name", "")
                for authorship in result.get("authorships", [])
                if authorship.get("author")
            )

            source_url = ""

            primary_location = result.get("primary_location")

            if primary_location:
                source_url = primary_location.get(
                    "landing_page_url",
                    ""
                ) or ""

            identifier = result.get("doi") or result.get("id", "")

            source_id = self.blackboard.add_source(
                title=title,
                authors=authors,
                source_url=source_url,
                identifier=identifier
            )

            stored_sources.append({
                "id": source_id,
                "title": title,
                "authors": authors,
                "source_url": source_url,
                "identifier": identifier
            })

        return stored_sources