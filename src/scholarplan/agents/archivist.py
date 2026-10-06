import json
from pathlib import Path


class Archivist:
    """Archive ScholarPlan results into human-readable and machine-readable files."""

    def __init__(self, blackboard, output_directory="outputs"):
        self.blackboard = blackboard
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def build_report(self, research_goal, status, iterations):
        """Build a Markdown research report from the current run."""

        tasks = self.blackboard.get_tasks()
        sources = self.blackboard.get_sources()
        claims = self.blackboard.get_claims()
        feedback = self.blackboard.get_feedback()
        events = self.blackboard.get_events()

        supported_claims = [
            claim for claim in claims
            if claim[3] == "SUPPORTED"
        ]

        lines = []

        lines.append("# ScholarPlan Research Report")
        lines.append("")

        lines.append("## Research Goal")
        lines.append("")
        lines.append(research_goal)
        lines.append("")

        lines.append("## Execution Summary")
        lines.append("")
        lines.append(f"- Final status: **{status}**")
        lines.append(f"- ReAct iterations executed: **{iterations}**")
        lines.append(f"- Academic sources retrieved: **{len(sources)}**")
        lines.append(f"- Research claims generated: **{len(claims)}**")
        lines.append(
            f"- Verified supported claims: **{len(supported_claims)}**"
        )
        lines.append(f"- Operational events recorded: **{len(events)}**")
        lines.append(
            f"- Run ID: `{self.blackboard.run_id}`"
        )
        lines.append("")

        lines.append("## Research Tasks")
        lines.append("")

        if tasks:
            for task_id, description, task_status in tasks:
                lines.append(
                    f"- **Task {task_id}** — {description} "
                    f"(`{task_status}`)"
                )
        else:
            lines.append("No research tasks were recorded.")

        lines.append("")

        lines.append("## Verified Findings")
        lines.append("")

        if supported_claims:
            for claim_id, claim, source_id, claim_status in supported_claims:
                lines.append(
                    f"- **Claim {claim_id}:** {claim}"
                )

                if source_id:
                    lines.append(
                        f"  - Source ID: {source_id}"
                    )
        else:
            lines.append(
                "No claims were verified as supported."
            )

        lines.append("")

        lines.append("## Claim Verification")
        lines.append("")

        if claims:
            lines.append(
                "| Claim ID | Claim | Source ID | Status |"
            )
            lines.append(
                "|---:|---|---:|---|"
            )

            for claim_id, claim, source_id, claim_status in claims:
                lines.append(
                    f"| {claim_id} | {claim} | "
                    f"{source_id if source_id else ''} | "
                    f"{claim_status} |"
                )
        else:
            lines.append("No claims were generated.")

        lines.append("")

        lines.append("## Academic Sources")
        lines.append("")

        if sources:
            for (
                source_id,
                title,
                authors,
                source_url,
                identifier
            ) in sources:

                lines.append(f"### Source {source_id}")
                lines.append("")
                lines.append(f"**Title:** {title}")
                lines.append("")

                if authors:
                    lines.append(f"**Authors:** {authors}")
                    lines.append("")

                if identifier:
                    lines.append(f"**Identifier:** {identifier}")
                    lines.append("")

                if source_url:
                    lines.append(f"**URL:** {source_url}")
                    lines.append("")

        else:
            lines.append(
                "No academic sources were retrieved."
            )

        lines.append("")

        lines.append("## Verification Feedback")
        lines.append("")

        if feedback:
            for feedback_id, claim_id, message in feedback:
                lines.append(
                    f"- **Feedback {feedback_id} "
                    f"(Claim {claim_id}):** {message}"
                )
        else:
            lines.append(
                "No verification feedback was recorded."
            )

        lines.append("")

        lines.append("## Limitations")
        lines.append("")

        lines.append(
            "The report is based on the academic sources retrieved "
            "during this execution. Source availability, abstracts, "
            "retrieval ranking, and model-generated claim extraction "
            "may affect the completeness of the findings."
        )

        lines.append("")

        lines.append("## Execution Trace Summary")
        lines.append("")

        if events:
            for event_id, event_type, message in events:
                lines.append(
                    f"- **Event {event_id} — {event_type}:** {message}"
                )
        else:
            lines.append(
                "No execution events were recorded."
            )

        lines.append("")

        return "\n".join(lines)

    def write_report(self, research_goal, status, iterations):
        """Write the Markdown research report."""

        report = self.build_report(
            research_goal=research_goal,
            status=status,
            iterations=iterations
        )

        report_path = (
            self.output_directory /
            "research_report.md"
        )

        report_path.write_text(
            report,
            encoding="utf-8"
        )

        return report_path

    def write_bibtex(self):
        """Create a BibTeX file from sources in the current run."""

        sources = self.blackboard.get_sources()

        lines = []

        for (
            source_id,
            title,
            authors,
            source_url,
            identifier
        ) in sources:

            entry_key = f"source{source_id}"

            lines.append(f"@misc{{{entry_key},")
            lines.append(f"  title = {{{title}}},")

            if authors:
                lines.append(
                    f"  author = {{{authors}}},"
                )

            if identifier:
                lines.append(
                    f"  note = {{{identifier}}},"
                )

            if source_url:
                lines.append(
                    f"  url = {{{source_url}}},"
                )

            lines.append("}")
            lines.append("")

        bibtex_path = (
            self.output_directory /
            "references.bib"
        )

        bibtex_path.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        return bibtex_path

    def write_execution_trace(self):
        """Write the current run's operational execution trace as JSON."""

        events = self.blackboard.get_events()

        trace = []

        for event_id, event_type, message in events:
            trace.append(
                {
                    "event_id": event_id,
                    "event_type": event_type,
                    "message": message
                }
            )

        trace_path = (
            self.output_directory /
            "execution_trace.json"
        )

        trace_path.write_text(
            json.dumps(
                trace,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return trace_path

    def archive(self, research_goal, status, iterations):
        """Create all ScholarPlan archival outputs."""

        report_path = self.write_report(
            research_goal=research_goal,
            status=status,
            iterations=iterations
        )

        bibtex_path = self.write_bibtex()

        trace_path = self.write_execution_trace()

        print("\n=== ARCHIVIST OUTPUT ===")
        print(f"Research report: {report_path}")
        print(f"Bibliography: {bibtex_path}")
        print(f"Execution trace: {trace_path}")

        return {
            "research_report": str(report_path),
            "references": str(bibtex_path),
            "execution_trace": str(trace_path)
        }