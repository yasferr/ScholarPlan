# ScholarPlan

## LLM-Powered Planning Agent for Academic Research and Information Gathering

ScholarPlan is an LLM-powered autonomous research assistant developed as
part of the MSc Artificial Intelligence programme at the University of
Essex Online.

The system receives a high-level academic research goal, creates a
structured research plan, retrieves academic sources, processes the
retrieved evidence into research claims, independently verifies those
claims, and archives the resulting research package.

The implementation uses a cooperating multi-agent architecture
coordinated through a SQLite Blackboard.

------------------------------------------------------------------------

## 1. Project Objective

The objective of ScholarPlan is to demonstrate how an LLM-powered
planning agent can autonomously support academic research and structured
information gathering.

The system demonstrates the following workflow:

``` text
Research Goal
      ↓
LLM Planner
      ↓
Research Tasks
      ↓
Academic Retrieval
      ↓
Source Processing
      ↓
Claim Generation
      ↓
Independent Verification
      ↓
Re-planning / Additional Retrieval
      ↓
Research Report
      ↓
Execution Trace + References + Evaluation
```

The implementation is based on the design proposed earlier in the
module, while incorporating practical refinements discovered during
development and testing.

------------------------------------------------------------------------

## 2. System Architecture

ScholarPlan uses a cooperating multi-agent architecture.

### Planner

The Planner uses an LLM to decompose the research goal into a small
number of executable research tasks.

The Planner returns structured JSON containing:

-   Research goal
-   Task identifiers
-   Task descriptions
-   Academic search queries
-   Task status

Structured output allows the rest of the system to validate and process
the plan programmatically.

### Retriever

The Retriever searches OpenAlex for academic sources.

For each retrieved source, the system extracts:

-   Title
-   Authors
-   Source URL
-   DOI or OpenAlex identifier
-   Abstract information

The source is then stored in the SQLite Blackboard.

The Retriever also generates a local semantic embedding using
`all-MiniLM-L6-v2`.

### Processor

The Processor receives retrieved academic sources and uses an LLM to
generate concise research claims.

Each claim must reference one or more retrieved sources.

The Processor is instructed to use only the evidence provided by the
Retriever and not to invent evidence.

### Critic

The Critic independently evaluates generated claims.

It considers:

1.  Whether the provided academic evidence supports the claim.
2.  Whether the claim is directly relevant to the research goal.

Claims are classified as:

-   `SUPPORTED`
-   `NOT_SUPPORTED`
-   `INSUFFICIENT_EVIDENCE`
-   `IRRELEVANT`

This provides a verification layer between claim generation and the
final research output.

### Archivist

The Archivist produces the final research package.

It generates:

-   Research report
-   BibTeX bibliography
-   Execution trace

The execution trace records operational events such as planning,
retrieval, processing, verification, replanning and completion.

Private model reasoning is not stored as chain-of-thought.

### Blackboard

The agents communicate through a shared SQLite Blackboard.

The Blackboard stores:

-   Research tasks
-   Academic sources
-   Claims
-   Verification feedback
-   Execution events

Each execution receives a unique `run_id`.

Run-scoped state prevents information from previous executions
contaminating a new research run.

------------------------------------------------------------------------

## 3. Autonomous ReAct Workflow

ScholarPlan uses a bounded iterative research loop.

The process is:

``` text
1. Receive research goal
2. Generate research plan
3. Select a research task
4. Retrieve academic sources
5. Process retrieved evidence
6. Generate research claims
7. Independently verify claims
8. Evaluate evidence quality
9. Re-plan when additional evidence is required
10. Complete when sufficient evidence is available or the iteration limit is reached
11. Archive the final research package
```

The current implementation uses a maximum of three iterations.

Re-planning allows the system to continue gathering evidence when the
accumulated evidence is not yet sufficient.

The loop is deliberately bounded to prevent uncontrolled autonomous
execution and to provide predictable resource usage.

------------------------------------------------------------------------

## 4. Semantic Embeddings

ScholarPlan uses the local `all-MiniLM-L6-v2` model from Sentence
Transformers to create semantic embeddings for retrieved academic
sources.

Each source is represented as a 384-dimensional vector.

The embeddings are stored in SQLite and compared using cosine
similarity.

The workflow is:

``` text
Academic Source
      ↓
Title + Abstract
      ↓
Sentence Transformer
      ↓
384-dimensional vector
      ↓
SQLite storage
      ↓
Cosine similarity
```

The system uses semantic similarity to identify potential duplicate or
highly similar sources.

Sources are not automatically deleted based on similarity because
semantic similarity does not necessarily mean that two academic papers
are duplicates.

### Implementation note

The original design proposal specified `sqlite-vec` for vector indexing.

During implementation, the Python 3.14 SQLite build used for this
project did not expose the SQLite loadable-extension functionality
required by `sqlite-vec`.

The final implementation therefore uses:

-   Sentence Transformers for embedding generation
-   SQLite BLOB storage for vectors
-   NumPy for cosine similarity

This preserves the semantic embedding and similarity functionality
without depending on unavailable SQLite extension loading.

------------------------------------------------------------------------

## 5. Technologies

The main technologies used are:

-   Python 3.14
-   SQLite
-   Azure AI Foundry / Azure OpenAI-compatible API
-   OpenAlex
-   Sentence Transformers
-   `all-MiniLM-L6-v2`
-   NumPy
-   Requests
-   Pytest
-   Git / GitHub
-   PyCharm

The original design proposal specified Python 3.11. The final
implementation was developed and tested using Python 3.14.0.

------------------------------------------------------------------------

## 6. Project Structure

``` text
ScholarPlan/
│
├── evaluation/
│   └── evaluation_metrics.py
│
├── evidence/
│
├── outputs/
│
├── src/
│   └── scholarplan/
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── planner.py
│       │   ├── retriever.py
│       │   ├── processor.py
│       │   ├── critic.py
│       │   └── archivist.py
│       │
│       ├── blackboard/
│       │   ├── __init__.py
│       │   └── database.py
│       │
│       ├── embeddings.py
│       ├── agent_loop.py
│       ├── llm_client.py
│       └── __init__.py
│
├── tests/
│   ├── test_agent_loop.py
│   ├── test_archivist.py
│   ├── test_blackboard.py
│   ├── test_critic.py
│   ├── test_embeddings.py
│   ├── test_evaluation.py
│   ├── test_planner.py
│   ├── test_processor.py
│   └── test_retriever.py
│
├── check_events.py
├── main.py
├── README.md
└── .gitignore
```

Generated files in `outputs/` are excluded from version control.

API credentials are stored in `.env` and excluded from Git.

------------------------------------------------------------------------

## 7. Requirements

The application requires:

-   Python 3.14
-   An Azure AI/OpenAI-compatible endpoint
-   An Azure API key
-   An available LLM deployment

The current implementation uses the Azure deployment:

``` text
gpt-5-mini
```

The main Python dependencies include:

``` text
openai
python-dotenv
requests
sentence-transformers
numpy
pytest
sqlite-vec
```

`sqlite-vec` was installed during development as part of the original
vector-indexing approach. The final implementation does not depend on
SQLite extension loading because of the SQLite build limitation
described above.

------------------------------------------------------------------------

## 8. Environment Configuration

Create a `.env` file in the project root.

Use:

``` text
AZURE_OPENAI_ENDPOINT=YOUR_AZURE_ENDPOINT
AZURE_OPENAI_API_KEY=YOUR_AZURE_API_KEY
AZURE_OPENAI_DEPLOYMENT=gpt-5-mini
```

Do not commit `.env` to GitHub.

The repository `.gitignore` excludes the file.

Never include the actual API key in the README, source code,
screenshots, or presentation.

------------------------------------------------------------------------

## 9. Installation

Create a virtual environment:

``` bash
python -m venv .venv
```

Activate it on macOS/Linux:

``` bash
source .venv/bin/activate
```

Install the required dependencies:

``` bash
pip install openai python-dotenv requests sentence-transformers numpy pytest sqlite-vec
```

Configure the `.env` file before running the application.

------------------------------------------------------------------------

## 10. Running ScholarPlan

From the project root, run:

``` bash
python main.py
```

The current demonstration uses the research goal:

``` text
Investigate the impact of large language models on academic research.
```

A successful execution reports the final status, number of iterations,
sources retrieved and claims generated, followed by the evaluation
metrics.

------------------------------------------------------------------------

## 11. Generated Outputs

A successful execution generates:

``` text
outputs/
├── research_report.md
├── references.bib
├── execution_trace.json
├── evaluation_metrics.json
└── scholarplan.db
```

### `research_report.md`

Contains the research goal, execution summary, research tasks, verified
findings, claim verification results, academic sources, verification
feedback, limitations and execution trace summary.

### `references.bib`

Contains BibTeX-style entries for retrieved academic sources.

### `execution_trace.json`

Contains structured operational events generated during execution. The
execution trace records operational system events rather than private
model reasoning.

### `evaluation_metrics.json`

Contains quantitative evaluation results from the execution.

### `scholarplan.db`

Contains the Blackboard state and execution data.

------------------------------------------------------------------------

## 12. Testing

The project uses Pytest for automated unit and functional testing.

The test suite covers:

-   Blackboard persistence
-   Run isolation
-   Planner validation
-   Retriever behaviour
-   Processor validation
-   Critic verification
-   Archivist output
-   Embedding generation
-   Embedding persistence
-   Semantic similarity
-   Evaluation metrics
-   End-to-end agent execution

The final regression suite contains:

``` text
24 tests passed
0 tests failed
```

The embedding tests verify the expected 384-dimensional representation,
higher similarity between semantically related text, and successful
SQLite persistence and retrieval.

The functional agent-loop test verifies that the complete planning and
execution workflow can complete successfully using controlled test
components.

------------------------------------------------------------------------

## 13. Evaluation

The evaluation component calculates quantitative metrics from each
ScholarPlan execution.

The metrics include:

-   ReAct iterations
-   Sources retrieved
-   Claims generated
-   Claims evaluated
-   Supported claims
-   Unsupported claims
-   Insufficient-evidence claims
-   Irrelevant claims
-   Critic-supported claim rate
-   Sources with embeddings
-   Embedding coverage
-   Potential duplicate matches
-   Duplicate rate

### Latest representative execution

A successful execution produced:

``` text
Status: completed
Iterations: 3
Sources retrieved: 15
Claims generated: 19
Claims evaluated: 19

Supported claims: 13
Irrelevant claims: 5
Insufficient evidence: 1
Unsupported claims: 0

Critic-supported claim rate: 68.4%

Sources with embeddings: 15
Embedding coverage: 100.0%

Potential duplicate matches: 1
Duplicate rate: 6.7%
```

The Critic-supported claim rate should not be interpreted as factual
accuracy. It represents the proportion of generated claims that the
independent Critic classified as `SUPPORTED` using the evidence supplied
to it.

------------------------------------------------------------------------

## 14. Remediation and Development Refinements

Several issues were identified during development and remediated.

### Persistent database contamination

Earlier executions caused historical sources, claims and events to
appear in later reports.

This was addressed by introducing a unique `run_id` for each execution
and filtering Blackboard queries by the active run.

This ensures that each research execution has isolated state.

### Functional test assumptions

The first functional test used too few simulated sources to satisfy the
agent's stopping condition.

The test was modified to provide sufficient simulated evidence while
preserving the production stopping logic.

### Test result key mismatch

An early functional test expected a result key that did not match the
final `ScholarPlanAgent` return structure.

The test was corrected to use the actual `critic_results` field.

### SQLite extension compatibility

The initial vector implementation attempted to use `sqlite-vec` through
SQLite loadable extensions.

The Python SQLite build used for the project did not expose the required
extension-loading functionality.

The implementation was therefore adapted to store embeddings as SQLite
BLOBs and calculate cosine similarity with NumPy.

### Embedding integration

Embedding functionality was introduced incrementally and tested
independently before being integrated into the Retriever.

The full regression suite was repeatedly executed after integration to
ensure that existing functionality remained stable.

------------------------------------------------------------------------

## 15. Design Decisions

### SQLite Blackboard

SQLite was selected because the system is designed for a single-user,
single-machine execution environment. It provides persistent shared
state without introducing the operational complexity of a distributed
database.

### Multi-agent decomposition

Planning, retrieval, processing, verification and archival are separated
into distinct responsibilities. This makes components easier to test and
allows verification to operate independently from claim generation.

### Structured JSON

The Planner and Processor use structured JSON outputs so LLM responses
can be validated before entering the rest of the pipeline. This reduces
the risk of malformed model output disrupting execution.

### Independent Critic

A separate verification stage was implemented because the Processor
generates claims. Separating generation from verification provides an
additional quality-control mechanism and makes it possible to reject
irrelevant or insufficiently supported claims.

### Bounded execution

The ReAct loop uses a maximum iteration limit to prevent uncontrolled
autonomous execution and provide predictable resource usage.

### Run isolation

A unique `run_id` is assigned to each execution to prevent previous
research runs from contaminating current results.

### Local embeddings

Local sentence embeddings were selected to provide semantic similarity
without requiring another external API. This reduces dependence on
additional external services.

------------------------------------------------------------------------

## 16. Limitations

### Source coverage

The current Retriever uses OpenAlex as the primary academic retrieval
source. Crossref and arXiv were included in the original design proposal
but are not currently integrated into the production retrieval workflow.

### Abstract availability

OpenAlex records do not always contain complete abstracts. Consequently,
some claims may be generated from limited source information.

### LLM-based verification

The Critic is itself an LLM. Therefore, a `SUPPORTED` verdict represents
model-based verification rather than independently established ground
truth.

### Embedding similarity

Semantic similarity does not guarantee that two papers are duplicates.
The system therefore flags potential matches rather than automatically
deleting sources.

### Python version

The original design proposal specified Python 3.11. The final
implementation was developed and tested using Python 3.14.0.

### Vector implementation

The original design proposed `sqlite-vec`. The final implementation uses
SQLite BLOB storage and NumPy cosine similarity because the SQLite build
available in the development environment did not support the required
extension-loading mechanism.

### Retrieval limitations

The system currently relies primarily on OpenAlex search ranking.
Retrieval quality may therefore vary depending on query formulation and
the availability of relevant records.

### LLM variability

LLM-generated plans and claims can vary between executions. The system
reduces this risk through structured output validation, bounded
execution, source grounding and independent claim verification.

------------------------------------------------------------------------

## 17. Academic Integrity and Sources

ScholarPlan was developed with reference to academic literature
concerning intelligent agents, LLM-based reasoning, retrieval,
reflection, blackboard architectures, semantic embeddings and claim
verification.

Key academic sources include:

Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. and Cao,
Y. (2023) 'ReAct: Synergizing reasoning and acting in language models'.
*International Conference on Learning Representations (ICLR)*.

Shinn, N., Cassano, F., Labash, B., Gopinath, A., Narasimhan, K. and
Yao, S. (2023) 'Reflexion: Language agents with verbal reinforcement
learning'. *Advances in Neural Information Processing Systems*, 36.

Erman, L.D., Hayes-Roth, F., Lesser, V.R. and Reddy, D.R. (1980) 'The
HEARSAY-II speech-understanding system: Integrating knowledge to resolve
uncertainty'. *ACM Computing Surveys*, 12(2), pp. 213--236.

Reimers, N. and Gurevych, I. (2019) 'Sentence-BERT: Sentence embeddings
using Siamese BERT-networks'. *Proceedings of the 2019 Conference on
Empirical Methods in Natural Language Processing and the 9th
International Joint Conference on Natural Language Processing*,
pp. 3982--3992.

Additional implementation sources include the official documentation
for:

-   OpenAlex
-   Azure AI / OpenAI
-   Sentence Transformers
-   Pytest
-   SQLite
-   NumPy

All external libraries, APIs, models and academic sources used by the
implementation should be acknowledged in the submitted project.

------------------------------------------------------------------------

## 18. Development History

The project was developed incrementally using Git and GitHub.

Major implementation milestones included:

1.  Initial SQLite Blackboard implementation.
2.  Autonomous ReAct research pipeline.
3.  Execution trace implementation.
4.  Evidence accumulation and stopping-logic refinement.
5.  Run-scoped verification and archival.
6.  Comprehensive unit and functional testing.
7.  Local semantic embeddings.
8.  Embedding integration with the Retriever.
9.  Run-scoped embedding storage.
10. Quantitative evaluation metrics.

The Git history provides evidence of incremental development, testing
and remediation throughout the implementation.

------------------------------------------------------------------------

## 19. Demonstration

The final demonstration should show the following aspects of the system.

### Application execution

Run:

``` bash
python main.py
```

Demonstrate the transition from:

``` text
Research goal
      ↓
Planning
      ↓
Retrieval
      ↓
Processing
      ↓
Critic verification
      ↓
Re-planning
      ↓
Final output
```

### Testing

Run:

``` bash
pytest
```

The current test suite contains 24 passing tests.

### Execution trace

Show:

``` text
outputs/execution_trace.json
```

This demonstrates the operational progression of the autonomous agent.

### Evaluation

Show:

``` text
outputs/evaluation_metrics.json
```

This provides quantitative evidence of the final execution.

### Generated research package

Show:

``` text
outputs/research_report.md
outputs/references.bib
```

These demonstrate that the system produces a meaningful final research
output rather than only a console response.

------------------------------------------------------------------------

## 20. Conclusion

ScholarPlan demonstrates an LLM-powered autonomous planning agent for
academic research.

The implemented system receives a research goal, creates a research
plan, retrieves academic evidence, processes sources into claims,
independently verifies those claims, re-plans when additional evidence
is required, and produces a structured research package.

The final implementation combines:

-   LLM-based planning
-   Multi-agent decomposition
-   SQLite Blackboard coordination
-   OpenAlex academic retrieval
-   Structured JSON outputs
-   Claim-level verification
-   Bounded ReAct execution
-   Re-planning
-   Local semantic embeddings
-   Similarity-based duplicate detection
-   Persistent execution traces
-   Quantitative evaluation
-   Automated unit and functional testing

The current regression suite contains 24 passing tests, and the latest
representative execution completed successfully after three ReAct
iterations with 15 retrieved sources, 19 generated claims, 100%
embedding coverage and a 68.4% Critic-supported claim rate.

The system therefore provides a complete implementation and
demonstration of an LLM-powered planning agent for academic research and
structured information gathering.
