import json
from datetime import datetime

from src.scholarplan.agents.planner import Planner
from src.scholarplan.agents.retriever import Retriever
from src.scholarplan.agents.processor import Processor
from src.scholarplan.agents.critic import Critic
from src.scholarplan.agents.archivist import Archivist
from src.scholarplan.blackboard.database import Blackboard


class AgentLoop:
    """
    Orchestrates the complete autonomous ScholarPlan research workflow.

    The workflow follows a bounded ReAct-style loop:

        Goal
          ↓
        Planning
          ↓
        Retrieval
          ↓
        Processing
          ↓
        Critic verification
          ↓
        Feedback
          ↓
        Replanning
          ↓
        Archive

    The loop is deliberately bounded to prevent uncontrolled
    API usage and repeated research cycles.
    """

    MAX_ITERATIONS = 3

    def __init__(self, database_path):
        """
        Initialise the ScholarPlan agent.

        Supports both the production SQLite Blackboard and the
        lightweight FakeBlackboard used by the functional tests.
        """

        # ---------------------------------------------------------
        # Blackboard initialisation
        # ---------------------------------------------------------

        if hasattr(database_path, "add_event"):
            # Functional tests provide a FakeBlackboard directly.
            self.blackboard = database_path
            self.database_path = None

            # Initialise Retriever normally so its internal
            # attributes exist, then connect it to the test
            # Blackboard.
            self.retriever = Retriever(self.database_path)
            self.retriever.blackboard = self.blackboard

        else:
            # Production execution uses the real SQLite Blackboard.
            self.database_path = database_path
            self.blackboard = Blackboard(database_path)
            self.retriever = Retriever(database_path)

        # ---------------------------------------------------------
        # Agent initialisation
        # ---------------------------------------------------------

        self.planner = Planner(self.blackboard)
        self.processor = Processor(self.blackboard)
        self.critic = Critic(self.blackboard)
        self.archivist = Archivist(self.blackboard)

    # =============================================================
    # EVENT LOGGING
    # =============================================================

    def log_event(self, event_type, details):
        """
        Record an operational event in the Blackboard.

        Events provide an execution trace for demonstration,
        debugging, evaluation and reproducibility.
        """

        try:
            self.blackboard.add_event(
                event_type=event_type,
                details=json.dumps(details)
            )

        except TypeError:
            self.blackboard.add_event(
                event_type,
                json.dumps(details)
            )

    # =============================================================
    # MAIN AGENT LOOP
    # =============================================================

    def run(self, research_goal):
        """
        Execute the complete autonomous research workflow.

        The Planner creates a research plan.
        The Retriever gathers scholarly evidence.
        The Processor generates claims from the evidence.
        The Critic independently verifies those claims.

        If evidence is insufficient, Critic feedback is retrieved
        from the Blackboard and supplied to the Planner so that
        the next iteration can refine its research strategy.

        The execution is bounded by MAX_ITERATIONS.
        """

        start_time = datetime.utcnow().isoformat()

        self.log_event(
            "RUN_STARTED",
            {
                "research_goal": research_goal,
                "started_at": start_time
            }
        )

        # ---------------------------------------------------------
        # Initial planning
        # ---------------------------------------------------------

        self.log_event(
            "PLANNING_STARTED",
            {
                "research_goal": research_goal,
                "iteration": 1
            }
        )

        plan = self.planner.create_plan(research_goal)

        self.planner.save_plan(plan)

        self.log_event(
            "PLAN_CREATED",
            {
                "iteration": 1,
                "tasks": plan["tasks"]
            }
        )

        # Keep the actual sources and claims rather than only counts.
        # The application and functional tests use these collections
        # for evaluation and reporting.
        all_sources = []
        all_claims = []
        all_critic_results = []

        # ---------------------------------------------------------
        # Bounded ReAct research loop
        # ---------------------------------------------------------

        for iteration in range(1, self.MAX_ITERATIONS + 1):

            self.log_event(
                "ITERATION_STARTED",
                {
                    "iteration": iteration
                }
            )

            # =====================================================
            # RETRIEVAL
            # =====================================================

            self.log_event(
                "RETRIEVAL_STARTED",
                {
                    "iteration": iteration,
                    "task_count": len(plan["tasks"])
                }
            )

            iteration_sources = []

            for task in plan["tasks"]:

                query = task["search_query"]

                sources = self.retriever.search(
                    query=query,
                    max_results=5
                )

                iteration_sources.extend(sources)

            # Preserve the actual retrieved source objects.
            all_sources.extend(iteration_sources)

            self.log_event(
                "RETRIEVAL_COMPLETED",
                {
                    "iteration": iteration,
                    "sources_retrieved": len(iteration_sources)
                }
            )

            # =====================================================
            # PROCESSING
            # =====================================================

            self.log_event(
                "PROCESSING_STARTED",
                {
                    "iteration": iteration
                }
            )

            processed_result = self.processor.process_sources(
                iteration_sources,
                research_goal
            )

            # The Processor normally returns a structured object
            # containing the research goal and claims.
            if isinstance(processed_result, dict):
                claims = processed_result.get("claims", [])
            else:
                # Preserve compatibility with a test double that
                # returns the claims list directly.
                claims = processed_result

            if not isinstance(claims, list):
                raise ValueError(
                    "Processor output must contain a 'claims' list."
                )

            # Preserve the actual generated claims.
            all_claims.extend(claims)

            self.log_event(
                "PROCESSING_COMPLETED",
                {
                    "iteration": iteration,
                    "claims_generated": len(claims)
                }
            )

            # =====================================================
            # INDEPENDENT CRITIC VERIFICATION
            # =====================================================

            self.log_event(
                "CRITIC_STARTED",
                {
                    "iteration": iteration,
                    "claims_to_evaluate": len(claims)
                }
            )

            # Critic requires:
            #   claims
            #   sources
            #   research goal
            #
            # The iteration sources allow the Critic to independently
            # compare each claim against the retrieved evidence.
            critic_results = self.critic.evaluate_claims(
                claims,
                iteration_sources,
                research_goal
            )

            all_critic_results.extend(critic_results)

            self.log_event(
                "CRITIC_COMPLETED",
                {
                    "iteration": iteration,
                    "claims_evaluated": len(critic_results)
                }
            )

            # =====================================================
            # EVIDENCE EVALUATION
            # =====================================================

            supported_claims = [
                result
                for result in all_critic_results
                if result.get("verdict") == "SUPPORTED"
                and result.get("relevance") == "RELEVANT"
            ]

            total_evaluated = len(all_critic_results)

            if total_evaluated > 0:
                support_ratio = (
                    len(supported_claims) / total_evaluated
                )
            else:
                support_ratio = 0.0

            # Use the actual accumulated source collection for the
            # stopping criterion. This also works with the test
            # Blackboard where database retrieval may differ.
            source_count = len(all_sources)

            self.log_event(
                "EVIDENCE_EVALUATED",
                {
                    "iteration": iteration,
                    "total_claims_evaluated": total_evaluated,
                    "supported_claims": len(supported_claims),
                    "support_ratio": support_ratio,
                    "sources_available": source_count
                }
            )

            # =====================================================
            # STOPPING CRITERIA
            # =====================================================

            # Require at least two iterations before completion.
            minimum_iterations_completed = iteration >= 2

            sufficient_sources = source_count >= 10

            sufficient_support = support_ratio >= 0.60

            if (
                minimum_iterations_completed
                and sufficient_sources
                and sufficient_support
            ):

                self.log_event(
                    "STOPPING_CRITERIA_MET",
                    {
                        "iteration": iteration,
                        "reason": (
                            "Sufficient evidence and "
                            "verification quality"
                        ),
                        "sources": source_count,
                        "support_ratio": support_ratio
                    }
                )

                break

            # =====================================================
            # REPLANNING
            # =====================================================

            if iteration < self.MAX_ITERATIONS:

                feedback_rows = self.blackboard.get_feedback()

                feedback = [
                    row[2]
                    for row in feedback_rows
                    if len(row) >= 3 and row[2]
                ]

                self.log_event(
                    "REPLANNING_STARTED",
                    {
                        "iteration": iteration,
                        "feedback_count": len(feedback)
                    }
                )

                # Critic feedback is explicitly supplied to the
                # Planner so that the next plan can address
                # evidence gaps and improve search strategy.
                plan = self.planner.create_plan(
                    research_goal=research_goal,
                    feedback=feedback
                )

                self.planner.save_plan(plan)

                self.log_event(
                    "PLAN_CREATED",
                    {
                        "iteration": iteration + 1,
                        "tasks": plan["tasks"],
                        "based_on_feedback": True
                    }
                )

        # =========================================================
        # ARCHIVING
        # =========================================================

        self.log_event(
            "ARCHIVING_STARTED",
            {
                "research_goal": research_goal
            }
        )

        archive_result = self.archivist.archive(
            research_goal=research_goal,
            status="completed",
            iterations=iteration
        )

        self.log_event(
            "ARCHIVING_COMPLETED",
            {
                "research_goal": research_goal
            }
        )

        # =========================================================
        # FINAL STATUS
        # =========================================================

        final_supported_claims = [
            result
            for result in all_critic_results
            if result.get("verdict") == "SUPPORTED"
            and result.get("relevance") == "RELEVANT"
        ]

        if all_critic_results:
            final_support_ratio = (
                len(final_supported_claims)
                / len(all_critic_results)
            )
        else:
            final_support_ratio = 0.0

        end_time = datetime.utcnow().isoformat()

        self.log_event(
            "RUN_COMPLETED",
            {
                "research_goal": research_goal,
                "completed_at": end_time,
                "iterations": iteration,
                "sources": len(all_sources),
                "claims": len(all_claims),
                "support_ratio": final_support_ratio
            }
        )

        # IMPORTANT:
        # Return the actual lists, not integer counts.
        # main.py calculates their lengths, and the functional
        # test checks len(result["sources"]) and len(result["claims"]).
        return {
            "status": "completed",
            "iterations": iteration,
            "sources": all_sources,
            "claims": all_claims,
            "critic_results": all_critic_results,
            "archive": archive_result
        }


# Backward-compatible name used by the existing test suite.
ScholarPlanAgent = AgentLoop