from src.scholarplan.agents.planner import Planner
from src.scholarplan.agents.retriever import Retriever
from src.scholarplan.agents.processor import Processor
from src.scholarplan.agents.critic import Critic
from src.scholarplan.agents.archivist import Archivist


class ScholarPlanAgent:
    """
    Orchestrates the ScholarPlan agents using a bounded ReAct-style loop.

    The system can:
    1. Plan the research goal
    2. Select a research task
    3. Use the Planner's search query
    4. Retrieve academic sources
    5. Process sources into claims
    6. Critically verify claims
    7. Decide whether the accumulated evidence is sufficient
    8. Re-plan when further evidence is required
    9. Archive the final research outputs

    Operational events are stored in the Blackboard as an execution trace.
    The trace records actions, observations and decisions rather than
    private model reasoning.
    """

    MAX_ITERATIONS = 3

    def __init__(self, blackboard):
        self.blackboard = blackboard

        self.planner = Planner(blackboard)
        self.retriever = Retriever(blackboard)
        self.processor = Processor(blackboard)
        self.critic = Critic(blackboard)
        self.archivist = Archivist(blackboard)

    def log_event(self, event_type, message):
        """
        Store an operational event in the Blackboard execution trace.
        """
        self.blackboard.add_event(
            event_type=event_type,
            message=message
        )

    def archive_results(
        self,
        research_goal,
        status,
        iterations
    ):
        """
        Generate the persistent research outputs after the
        autonomous research process has completed.
        """

        print(
            "\n[Action] Archivist is generating "
            "the final research package..."
        )

        self.log_event(
            "ARCHIVIST_STARTED",
            "Generating final research report, "
            "BibTeX bibliography and execution trace."
        )

        archive_result = self.archivist.archive(
            research_goal=research_goal,
            status=status,
            iterations=iterations
        )

        print(
            "\n[Observation] "
            "Final research package generated."
        )

        print(
            f"Research report: "
            f"{archive_result['research_report']}"
        )

        print(
            f"References: "
            f"{archive_result['references']}"
        )

        print(
            f"Execution trace: "
            f"{archive_result['execution_trace']}"
        )

        return archive_result

    def run(self, research_goal):
        print("\n=== ScholarPlan Autonomous Agent ===")
        print(f"Research goal: {research_goal}")

        self.log_event(
            "RUN_STARTED",
            f"Research goal: {research_goal}"
        )

        # ---------------------------------------------------------
        # INITIAL PLANNING
        # ---------------------------------------------------------

        plan = self.planner.create_plan(research_goal)
        self.planner.save_plan(plan)

        self.log_event(
            "PLAN_CREATED",
            f"Initial plan created with {len(plan['tasks'])} tasks."
        )

        print("\nInitial research plan:")

        for task in plan["tasks"]:
            print(f"- {task['description']}")
            print(f"  Search query: {task['search_query']}")

        # ---------------------------------------------------------
        # ACCUMULATED EVIDENCE
        # ---------------------------------------------------------

        all_sources = []
        all_claims = []
        all_critic_results = []

        # ---------------------------------------------------------
        # BOUNDED REACT LOOP
        # ---------------------------------------------------------

        for iteration in range(1, self.MAX_ITERATIONS + 1):

            print(f"\n{'=' * 60}")
            print(f"REACT ITERATION {iteration}")
            print(f"{'=' * 60}")

            self.log_event(
                "ITERATION_STARTED",
                f"Starting ReAct iteration {iteration}."
            )

            tasks = plan["tasks"]

            if not tasks:
                self.log_event(
                    "ERROR",
                    "Planner returned an empty task list."
                )

                raise ValueError(
                    "Planner returned an empty task list."
                )

            # -----------------------------------------------------
            # SELECT TASK
            # -----------------------------------------------------

            task_index = (iteration - 1) % len(tasks)

            selected_task = tasks[task_index]

            task_description = selected_task["description"]
            search_query = selected_task["search_query"]

            print("\n[Decision] Selected research task:")
            print(task_description)

            print("\n[Decision] Search query:")
            print(search_query)

            self.log_event(
                "TASK_SELECTED",
                f"Iteration {iteration}: {task_description}"
            )

            self.log_event(
                "SEARCH_QUERY_SELECTED",
                f"Iteration {iteration}: {search_query}"
            )

            # -----------------------------------------------------
            # RETRIEVE
            # -----------------------------------------------------

            print(
                "\n[Action] Retrieving academic sources "
                "for selected task..."
            )

            self.log_event(
                "RETRIEVAL_STARTED",
                f"Iteration {iteration}: "
                f"Searching OpenAlex using the Planner query."
            )

            sources = self.retriever.search(
                query=search_query,
                max_results=5
            )

            print(
                "[Observation] "
                f"Retrieved {len(sources)} sources."
            )

            self.log_event(
                "SOURCES_RETRIEVED",
                f"Iteration {iteration}: "
                f"Retrieved {len(sources)} sources."
            )

            # Accumulate sources from every iteration.
            all_sources.extend(sources)

            # -----------------------------------------------------
            # PROCESS
            # -----------------------------------------------------

            print(
                "\n[Action] Processing sources "
                "into research claims..."
            )

            self.log_event(
                "PROCESSING_STARTED",
                f"Iteration {iteration}: "
                f"Processing retrieved sources."
            )

            processed = self.processor.process_sources(
                sources=sources,
                research_goal=research_goal
            )

            claims = processed["claims"]

            print(
                "[Observation] "
                f"Generated {len(claims)} claims."
            )

            self.log_event(
                "CLAIMS_GENERATED",
                f"Iteration {iteration}: "
                f"Generated {len(claims)} claims."
            )

            # Accumulate claims from every iteration.
            all_claims.extend(claims)

            # -----------------------------------------------------
            # CRITIC
            # -----------------------------------------------------

            print(
                "\n[Action] Verifying claims with Critic..."
            )

            self.log_event(
                "CRITIC_STARTED",
                f"Iteration {iteration}: "
                f"Verifying {len(claims)} claims."
            )

            critic_results = self.critic.evaluate_claims(
                claims=claims,
                sources=sources,
                research_goal=research_goal
            )

            supported = 0
            insufficient = 0
            rejected = 0

            for result in critic_results:

                print(f"\nClaim: {result['claim']}")
                print(f"Verdict: {result['verdict']}")
                print(f"Relevance: {result['relevance']}")

                if result["verdict"] == "SUPPORTED":
                    supported += 1

                elif result["verdict"] == "INSUFFICIENT_EVIDENCE":
                    insufficient += 1

                else:
                    rejected += 1

            print("\n[Observation]")
            print(f"Supported claims: {supported}")
            print(f"Insufficient evidence: {insufficient}")
            print(f"Rejected/irrelevant: {rejected}")

            self.log_event(
                "CRITIC_COMPLETED",
                f"Iteration {iteration}: "
                f"{supported} supported, "
                f"{insufficient} insufficient, "
                f"{rejected} rejected or irrelevant."
            )

            # Accumulate Critic results from every iteration.
            all_critic_results.extend(critic_results)

            # -----------------------------------------------------
            # ACCUMULATED DECISION METRICS
            # -----------------------------------------------------

            total_accumulated_claims = len(
                all_critic_results
            )

            accumulated_supported = sum(
                1
                for result in all_critic_results
                if result["verdict"] == "SUPPORTED"
            )

            accumulated_support_ratio = (
                accumulated_supported / total_accumulated_claims
                if total_accumulated_claims > 0
                else 0
            )

            minimum_iterations_reached = iteration >= 2
            minimum_sources_reached = len(all_sources) >= 10

            print(
                "\n[Decision Metrics] "
                f"Accumulated sources: {len(all_sources)}"
            )

            print(
                "[Decision Metrics] "
                f"Accumulated claims: "
                f"{total_accumulated_claims}"
            )

            print(
                "[Decision Metrics] "
                f"Accumulated supported claims: "
                f"{accumulated_supported}"
            )

            print(
                "[Decision Metrics] "
                f"Accumulated support ratio: "
                f"{accumulated_support_ratio:.2f}"
            )

            # -----------------------------------------------------
            # DECISION
            # -----------------------------------------------------

            if (
                minimum_iterations_reached
                and minimum_sources_reached
                and accumulated_support_ratio >= 0.6
            ):

                print(
                    "\n[Decision] Accumulated evidence is sufficient. "
                    "Ending autonomous loop."
                )

                self.log_event(
                    "EVIDENCE_SUFFICIENT",
                    f"Iteration {iteration}: "
                    f"Accumulated evidence threshold satisfied."
                )

                self.log_event(
                    "RUN_COMPLETED",
                    f"ScholarPlan completed after "
                    f"{iteration} iteration(s)."
                )

                archive_result = self.archive_results(
                    research_goal=research_goal,
                    status="completed",
                    iterations=iteration
                )

                return {
                    "research_goal": research_goal,
                    "iterations": iteration,
                    "sources": all_sources,
                    "claims": all_claims,
                    "critic_results": all_critic_results,
                    "archive": archive_result,
                    "status": "completed"
                }

            # -----------------------------------------------------
            # RE-PLANNING
            # -----------------------------------------------------

            if iteration < self.MAX_ITERATIONS:

                print(
                    "\n[Decision] Accumulated evidence is "
                    "not yet sufficient."
                )

                print(
                    "[Action] Re-planning research strategy..."
                )

                self.log_event(
                    "EVIDENCE_INSUFFICIENT",
                    f"Iteration {iteration}: "
                    f"Accumulated evidence threshold "
                    f"was not satisfied."
                )

                self.log_event(
                    "REPLANNING_STARTED",
                    f"Iteration {iteration}: "
                    f"Generating a new research plan."
                )

                plan = self.planner.create_plan(
                    research_goal
                )

                self.planner.save_plan(plan)

                self.log_event(
                    "PLAN_CREATED",
                    f"New plan created after iteration "
                    f"{iteration} with "
                    f"{len(plan['tasks'])} tasks."
                )

                print("\nNew research plan:")

                for task in plan["tasks"]:

                    print(
                        f"- {task['description']}"
                    )

                    print(
                        f"  Search query: "
                        f"{task['search_query']}"
                    )

            else:

                print(
                    "\n[Decision] Maximum iteration "
                    "limit reached."
                )

                self.log_event(
                    "MAX_ITERATIONS_REACHED",
                    f"Maximum of "
                    f"{self.MAX_ITERATIONS} iterations reached."
                )

        # ---------------------------------------------------------
        # MAXIMUM ITERATIONS REACHED
        # ---------------------------------------------------------

        self.log_event(
            "RUN_COMPLETED",
            "ScholarPlan stopped because the maximum "
            "iteration limit was reached."
        )

        archive_result = self.archive_results(
            research_goal=research_goal,
            status="maximum_iterations_reached",
            iterations=self.MAX_ITERATIONS
        )

        return {
            "research_goal": research_goal,
            "iterations": self.MAX_ITERATIONS,
            "sources": all_sources,
            "claims": all_claims,
            "critic_results": all_critic_results,
            "archive": archive_result,
            "status": "maximum_iterations_reached"
        }