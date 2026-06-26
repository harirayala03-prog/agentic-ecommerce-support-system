# Agentic E-Commerce Support System

A production-architecture reference implementation of a multi-agent customer support system built on **LangGraph**, **A2A protocol**, **Model Context Protocol (MCP)**, **RAG**, and **Google Cloud Platform**.

The system demonstrates how enterprise-scale agentic AI is architected for reliability, observability, and extensibility — not as a single LLM call, but as a set of focused, testable, independently deployable agents coordinated through standardized protocols.

---

## Architecture Overview

```
Customer message
       │
       ▼
Supervisor Agent (LangGraph state machine)
       │  classifies intent → deterministic routing
       ▼
A2A communication layer
       │
   ┌───┴────────────┬─────────────────┐
   ▼                ▼                 ▼
Order Status    Billing/Refund    Product Knowledge
   Agent            Agent          (RAG) Agent
   └───┬────────────┴─────────────────┘
       ▼
MCP Server (unified tool + data access)
       │
   ┌───┴───────┬────────────┬────────────┐
   ▼           ▼            ▼            ▼
Order DB   Payments API  Vector Store  Customer Memory
```

**Key architectural decisions:**

- **Deterministic routing over free-form LLM improvisation** — the Supervisor classifies intent and routes via a LangGraph state machine, not a prompt asking the LLM to "decide what to do next"
- **Standardized protocols over bespoke integrations** — MCP replaces one-off tool integrations per agent; A2A replaces hardcoded function calls between agents
- **Observable by design** — every agent interaction is traced via LangSmith; evaluation sets and drift detection are built into the pipeline, not added afterward

---

## Tech Stack

| Layer | Tools |
|---|---|
| Orchestration | LangGraph, LangChain |
| LLM | Anthropic Claude (`langchain-anthropic`) |
| Agent coordination | A2A Protocol |
| Tool/data unification | Model Context Protocol (MCP) |
| Retrieval (RAG) | FAISS (local), Pinecone (cloud) |
| Deployment | Docker, GCP Cloud Run, GKE |
| Async events | GCP Pub/Sub, Cloud Functions |
| Auth | GCP IAM, Service Accounts |
| Observability / LLMOps | LangSmith, GCP Cloud Logging, Vertex AI Evaluation |

---

## Agent Responsibilities

### Supervisor Agent
Classifies incoming customer intent and routes to the appropriate specialist via the A2A layer. Implemented as a LangGraph state machine with deterministic branching — routing logic is explicit and testable, not embedded in a prompt.

### Order Status Agent
Handles shipment and delivery queries. Reaches order and logistics data through the MCP server rather than direct database calls, keeping the agent decoupled from infrastructure.

### Billing / Refund Agent
Processes payment history lookups and refund eligibility checks. Applies business rules as code before escalating to LLM reasoning, keeping deterministic logic out of the model.

### Product Knowledge Agent (RAG)
Answers policy and product questions using a retrieval-augmented generation pipeline over indexed policy documents. Uses FAISS for local development and Pinecone for cloud deployment.

---

## MCP Server

The MCP server exposes a single, consistent interface to all shared tools and data:

- Order lookup and status
- Payment history and refund processing
- Vector store search (RAG)
- Customer memory read/write

Each agent calls the MCP server rather than maintaining its own database connections or API clients. This keeps agents thin, testable, and infrastructure-agnostic.

---

## Repository Structure

```
.
├── graph_v2.py           # Supervisor with conditional routing to specialist agents
├── graph_v3.py           # A2A communication layer between agents
├── graph_v4.py           # MCP server integration
├── mcp_server.py         # MCP server exposing shared tools and data
├── mcp_client_test.py    # MCP client integration tests
├── build_vector_store.py # Indexes policy/product docs into FAISS / Pinecone
├── rag_query.py          # RAG retrieval pipeline
├── a2a_types.py          # A2A protocol type definitions
├── mock_data.py          # Order, payment, and customer test fixtures
├── policy_docs.py        # Source documents for RAG indexing
├── faiss_index/          # Local vector store (FAISS)
├── hello_claude.py       # API connectivity check
└── .gitignore
```

---

## Running Locally

```bash
git clone https://github.com/harirayala03-prog/agentic-ecommerce-support-system.git
cd agentic-ecommerce-support-system
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
pip install langchain langgraph langchain-anthropic python-dotenv
```

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
LANGSMITH_API_KEY=your_key_here
```

Run the supervisor workflow:

```bash
python graph_v4.py
```

Run MCP server:

```bash
python mcp_server.py
```

---

## Design Principles

**Separation of concerns** — each agent owns a single domain. The Supervisor does not know how to look up orders; the Order Agent does not know about billing. Boundaries are enforced at the A2A layer.

**Protocols over point-to-point wiring** — MCP and A2A are chosen specifically because they are the protocols emerging as enterprise standards for agentic systems. Adopting them here means the architecture scales to additional agents and tools without restructuring.

**Observability first** — LangSmith tracing is configured from the first graph version, not added at the end. Evaluation sets are built alongside features so regression is detectable.

**Infrastructure parity** — local development uses FAISS and mock data; cloud deployment uses Pinecone and GCP services. The agent code does not change between environments — only configuration does.

---

## Deployment

The system is containerized with Docker and deployable to GCP Cloud Run (stateless agents) or GKE (long-running services). Async events between services use Pub/Sub. Service-to-service authentication uses GCP IAM and service accounts.

```bash
docker build -t agentic-support .
docker run -p 8080:8080 agentic-support
```

---

## Observability

All agent interactions are traced end-to-end in LangSmith. GCP Cloud Logging captures infrastructure-level events. Vertex AI Evaluation is used to run evaluation sets against the RAG pipeline and agent responses, with drift detection on retrieval quality over time.
