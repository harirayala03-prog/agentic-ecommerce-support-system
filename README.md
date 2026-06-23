# Agentic E-Commerce Support System

A multi-agent customer support system built to practice and demonstrate the
core architecture patterns used in production agentic AI systems: stateful
orchestration with **LangGraph**, agent-to-agent coordination via the **A2A
protocol**, unified tool/data access via the **Model Context Protocol (MCP)**,
retrieval-augmented generation (**RAG**), and deployment/observability on
**Google Cloud Platform**.

This project is being built incrementally and documented as it grows, rather
than delivered as a single finished drop — the commit history reflects real
iterative development.

## Why this project exists

I built this to deeply understand and demonstrate the architecture behind
modern agentic AI systems — the kind used for automated customer support and
operations at scale. Rather than a single LLM call wrapped in a chat UI, this
project explores how to build a system that:

- Breaks a broad task into small, focused, testable agents
- Routes work deterministically rather than letting an LLM freely improvise
  its next step
- Connects agents to tools and data through standardized protocols (MCP)
  instead of one-off integrations
- Lets independent agents coordinate as peers (A2A) rather than as hardcoded
  function calls
- Is observable and evaluable, not just "it worked when I tried it once"

## The scenario

A customer messages support with something like:

> "My order #4521 hasn't arrived and I want a refund."

A **Supervisor Agent** classifies the intent and routes the request through a
deterministic LangGraph workflow to the right specialist:

- **Order Status Agent** — checks shipment/delivery status
- **Billing / Refund Agent** — checks payment history, refund eligibility
- **Product Knowledge Agent** — answers policy/product questions via RAG

Specialist agents communicate through an **A2A layer** and reach shared tools
and data (order database, payments, vector store, customer memory) through a
single **MCP server**, rather than each agent having its own bespoke
integration code.

## Architecture

```
Customer message
       │
       ▼
Supervisor Agent (LangGraph state machine)
       │
       ▼
A2A communication layer
       │
   ┌───┴────────────┬─────────────────┐
   ▼                ▼                 ▼
Order Status    Billing/Refund    Product Knowledge
   Agent            Agent          (RAG) Agent
   └───┬────────────┴─────────────────┘
       ▼
MCP server (tools + resources)
       │
   ┌───┴───────┬────────────┬────────────┐
   ▼           ▼            ▼            ▼
Order DB   Payments API  Vector store  Customer memory
```

## Tech stack

| Layer | Tools |
|---|---|
| Orchestration | LangGraph, LangChain |
| LLM | Anthropic Claude (via `langchain-anthropic`) |
| Agent-to-agent coordination | A2A protocol |
| Tool/data unification | MCP (Model Context Protocol) |
| Retrieval (RAG) | FAISS (local), Pinecone (cloud) |
| Deployment | Docker, GCP Cloud Run / GKE |
| Async events | GCP Pub/Sub, Cloud Functions |
| Observability / LLMOps | LangSmith, GCP Cloud Logging, Vertex AI Evaluation |

## Project status

This is a learning project built in public, in stages:

- [x] Environment setup, first raw LLM call
- [x] First LangGraph graph — single linear workflow (classify → respond)
- [x] Conditional branching — supervisor routes to specialist agents based on
      classified intent
- [ ] A2A communication layer between supervisor and specialist agents
- [ ] MCP server exposing shared tools (order lookup, refund, RAG search,
      customer memory)
- [ ] RAG pipeline over product/policy documents (FAISS → Pinecone)
- [ ] Containerization (Docker) and deployment to GCP Cloud Run
- [ ] Async events via Pub/Sub, secure service-to-service auth via IAM
- [ ] LLMOps: LangSmith tracing, evaluation set, drift detection, governance
      rules

## Repository structure

```
.
├── hello_claude.py     # First raw call to Claude — sanity check that the
│                         API connection and key work
├── graph_v1.py         # First LangGraph graph: linear, no branching
├── graph_v2.py         # Adds conditional routing to specialist agent nodes
│                         based on classified customer intent
├── .env                # API keys (not committed — see .gitignore)
└── .gitignore
```

## Running locally

```bash
git clone https://github.com/harirayala03-prog/agentic-ecommerce-support-system.git
cd agentic-ecommerce-support-system
python -m venv venv
venv\Scripts\activate        # Windows
pip install langchain langgraph langchain-anthropic python-dotenv
```

Create a `.env` file in the project root with your own Anthropic API key:

```
ANTHROPIC_API_KEY=your_key_here
```

Then run any of the example scripts:

```bash
python graph_v2.py
```

## Background

This project's design deliberately mirrors the responsibilities of an
agentic-systems AI engineer role at a large enterprise (telecom customer
support and network operations), adapted here to an e-commerce support
domain so the focus stays on architecture rather than domain-specific
knowledge.
