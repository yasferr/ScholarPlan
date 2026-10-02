import json

from src.scholarplan.llm_client import ask_llm


class Critic:
    """
    Independently verify research claims against academic evidence.

    The Critic evaluates:
    1. Whether the source evidence supports the claim.
    2. Whether the claim is directly relevant to the research goal.
    """

    def __init__(self, blackboard):

        self.blackboard = blackboard

    def evaluate_claim(
        self,
        claim,
        sources,
        research_goal
    ):

        relevant_sources = []

        for source in sources:

            if source["id"] in claim["source_ids"]:

                relevant_sources.append(
                    source
                )

        evidence_text = "\n\n".join(

            f"Source {source['id']}:\n"
            f"Title: {source['title']}\n"
            f"Abstract: {source.get('abstract', 'No abstract available')}"

            for source in relevant_sources
        )

        prompt = f"""
You are the Critic Agent in ScholarPlan.

Your task is to independently verify a research claim.

Research goal:
{research_goal}

Claim:
{claim["claim"]}

Processor evidence:
{claim["evidence"]}

Academic sources:
{evidence_text}

Evaluate BOTH:

1. Evidence support

Does the provided academic evidence directly support
the claim?

2. Research relevance

Does the claim directly address the research goal?

The research goal is:

"{research_goal}"

A claim is RELEVANT only when the evidence directly concerns
the subject of the research goal.

For this research goal, relevant evidence should directly
address one or more of the following:

- the use of LLMs in academic or scientific research
- changes to research workflows
- researcher productivity
- academic writing or coding
- literature discovery or synthesis
- research quality or accuracy
- reproducibility
- methodological transparency
- scholarly communication
- authorship or publishing practices
- research-related risks or benefits

Do NOT classify a claim as relevant merely because it
describes a general capability of an LLM.

For example:

Claim:
"Larger language models perform better at multilingual tasks."

This may be a true claim about LLMs, but it is NOT directly
relevant to the research goal unless the provided evidence
connects that capability to academic research.

Similarly:

Claim:
"LLMs can assist clinical decision-making."

This is NOT directly relevant unless the evidence specifically
connects clinical use to academic or scientific research.

Classify the claim as exactly one of:

- SUPPORTED
- NOT_SUPPORTED
- INSUFFICIENT_EVIDENCE
- IRRELEVANT

Definitions:

SUPPORTED:
The academic evidence directly supports the claim AND
the claim is directly relevant to the research goal.

NOT_SUPPORTED:
The provided academic evidence contradicts the claim or
does not support it.

INSUFFICIENT_EVIDENCE:
The available evidence is too limited to determine whether
the claim is supported.

IRRELEVANT:
The source may support the claim, but the claim does not
directly address the research goal.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "claim": "{claim["claim"]}",
  "verdict": "SUPPORTED",
  "relevance": "RELEVANT",
  "feedback": "Brief factual explanation based only on the provided evidence and research goal.",
  "source_ids": {claim["source_ids"]}
}}

Rules:

- Use only the provided evidence.
- Do not invent information.
- Do not use general knowledge.
- Do not assume that a general LLM capability is relevant to academic research.
- Do not infer relevance simply because an application could theoretically be used in research.
- The evidence must explicitly connect the claim to academic or scientific research.
- Keep feedback concise and factual.
"""

        response = ask_llm(
            prompt
        )

        try:

            result = json.loads(
                response
            )

        except json.JSONDecodeError as error:

            raise ValueError(
                f"Critic returned invalid JSON: {response}"
            ) from error

        required_fields = [
            "claim",
            "verdict",
            "relevance",
            "feedback",
            "source_ids"
        ]

        if not all(
            field in result
            for field in required_fields
        ):

            raise ValueError(
                "Critic response is missing required fields."
            )

        valid_verdicts = {
            "SUPPORTED",
            "NOT_SUPPORTED",
            "INSUFFICIENT_EVIDENCE",
            "IRRELEVANT"
        }

        if result["verdict"] not in valid_verdicts:

            raise ValueError(
                f"Invalid Critic verdict: "
                f"{result['verdict']}"
            )

        if result["relevance"] not in {
            "RELEVANT",
            "IRRELEVANT"
        }:

            raise ValueError(
                f"Invalid relevance value: "
                f"{result['relevance']}"
            )

        feedback_message = (
            f"Verdict: {result['verdict']}\n"
            f"Relevance: {result['relevance']}\n"
            f"Feedback: {result['feedback']}"
        )

        self.blackboard.add_feedback(
            claim_id=claim["id"],
            message=feedback_message
        )

        return result

    def evaluate_claims(
        self,
        claims,
        sources,
        research_goal
    ):

        results = []

        for claim in claims:

            result = self.evaluate_claim(
                claim=claim,
                sources=sources,
                research_goal=research_goal
            )

            results.append(
                result
            )

        return results