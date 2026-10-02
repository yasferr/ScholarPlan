import json

from src.scholarplan.llm_client import ask_llm


class Processor:
    """Process retrieved academic sources using an LLM."""

    def __init__(self, blackboard):
        self.blackboard = blackboard

    def process_sources(self, sources, research_goal):
        source_text = "\n\n".join(
            f"Source {source['id']}:\n"
            f"Title: {source['title']}\n"
            f"Authors: {source['authors']}\n"
            f"URL: {source['source_url']}\n"
            f"Abstract: {source.get('abstract', 'No abstract available')}"
            for source in sources
        )

        prompt = f"""
You are the processing agent in ScholarPlan.

Research goal:
{research_goal}

The following academic sources were retrieved:

{source_text}

Analyse the retrieved sources and identify the main research claims
that can be supported by the available source information.

Return ONLY valid JSON using exactly this structure:

{{
  "research_goal": "{research_goal}",
  "claims": [
    {{
      "claim": "A concise research claim",
      "source_ids": [1],
      "evidence": "Brief explanation of the supporting evidence"
    }}
  ]
}}

Rules:
- Only make claims supported by the provided sources.
- Do not invent facts, results, authors, or evidence.
- Each claim must reference one or more source IDs.
- Keep claims concise and academically phrased.
"""

        response = ask_llm(prompt)

        try:
            result = json.loads(response)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Processor returned invalid JSON: {response}"
            ) from error

        if "claims" not in result:
            raise ValueError(
                "Processor response is missing 'claims'."
            )

        if not isinstance(result["claims"], list):
            raise ValueError(
                "Processor claims must be a list."
            )

        stored_claims = []

        for claim in result["claims"]:
            if not all(
                field in claim
                for field in ["claim", "source_ids", "evidence"]
            ):
                raise ValueError(
                    "Each claim must contain "
                    "claim, source_ids and evidence."
                )

            source_ids = claim["source_ids"]

            if not source_ids:
                raise ValueError(
                    "Each claim must reference at least one source."
                )

            # Store the claim in the Blackboard.
            # The current Blackboard schema stores one source_id,
            # so we use the first referenced source.
            claim_id = self.blackboard.add_claim(
                claim=claim["claim"],
                source_id=source_ids[0],
                status="pending"
            )

            stored_claims.append(
                {
                    "id": claim_id,
                    "claim": claim["claim"],
                    "source_ids": source_ids,
                    "evidence": claim["evidence"]
                }
            )

        result["claims"] = stored_claims

        return result