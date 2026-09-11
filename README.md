# Enterprise AI Operations Copilot

An enterprise-oriented **GenAI Operations Copilot** built with Python, FastAPI, LangGraph, Retrieval-Augmented Generation (RAG), Qdrant, Ollama/Llama 3, Model Context Protocol (MCP), PostgreSQL, and OpenTelemetry.

The application demonstrates how an AI assistant can combine **LLM reasoning, enterprise knowledge retrieval, external tools, conversational memory, guardrails, and observability** to assist operations teams with incident and service-management questions.

> **Portfolio project:** Designed as a production-oriented GenAI reference application and as a demonstration of enterprise AI architecture patterns.

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │        Client           │
                         │   REST / API Request     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │       FastAPI           │
                         │     API Layer           │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    OperationsAgent      │
                         │      LangGraph          │
                         └────────────┬────────────┘
                                      │
                       ┌──────────────┼──────────────┐
                       │              │              │
                       ▼              ▼              ▼
                    ┌───────┐     ┌───────┐     ┌────────────┐
                    │  RAG  │     │  MCP  │     │ Direct LLM │
                    └───┬───┘     └───┬───┘     └─────┬──────┘
                        │              │               │
                        ▼              ▼               ▼
                 ┌────────────┐   ┌──────────┐   ┌──────────┐
                 │   Qdrant   │   │ MCP      │   │ Ollama   │
                 │ Vector DB  │   │ Tools    │   │ Llama 3  │
                 └─────┬──────┘   └──────────┘   └──────────┘
                       │
                       ▼
                 ┌────────────┐
                 │ Hybrid     │
                 │ Retrieval  │
                 │            │
                 │ Dense +    │
                 │ BM25 + RRF │
                 │ + Reranker │
                 └────────────┘

                       ┌─────────────────────┐
                       │    PostgreSQL       │
                       │ Conversation Memory │
                       └─────────────────────┘

                       ┌─────────────────────┐
                       │   OpenTelemetry     │
                       │ Tracing / Metrics   │
                       └─────────────────────┘
```

The application exposes FastAPI endpoints and routes requests through a LangGraph-based `OperationsAgent`. The agent selects between RAG, MCP/tool execution, and direct LLM generation.

---

## Key Capabilities

### 1. Agentic Request Routing

The `OperationsAgent` uses LangGraph to route incoming questions to one of three paths:

* **RAG** — questions requiring enterprise operational knowledge
* **Tool / MCP** — questions requiring current service information
* **Direct LLM** — general questions that do not require enterprise retrieval or tools

```text
User Query
    │
    ▼
Intent Router
    │
    ├── RAG
    │    └── Retrieve enterprise knowledge
    │
    ├── TOOL
    │    └── Invoke MCP tool
    │
    └── DIRECT_LLM
         └── Ollama / Llama 3
```

The routing workflow is implemented with LangGraph conditional edges.

---

# 2. Retrieval-Augmented Generation

The RAG pipeline combines semantic and lexical retrieval.

```text
User Query
    │
    ▼
Dense Retrieval ──────┐
                      │
BM25 Retrieval ───────┤
                      ▼
              Reciprocal Rank Fusion
                      │
                      ▼
               Cross-Encoder
                 Reranking
                      │
                      ▼
              Relevance Filtering
                      │
                      ▼
                Prompt Builder
                      │
                      ▼
                 Llama 3
                      │
                      ▼
             Grounding Validation
                      │
              ┌───────┴────────┐
              ▼                ▼
         Grounded Answer    Abstain
```

The hybrid retriever combines:

* Dense semantic retrieval using Qdrant
* BM25 lexical retrieval
* Reciprocal Rank Fusion (RRF)
* Cross-encoder reranking
* Relevance filtering

This approach allows the application to combine semantic similarity with keyword-based retrieval for operational documentation.

The RAG service additionally applies document safety checks, relevance filtering, grounding validation, and abstention when sufficient evidence is unavailable.

---

# 3. Enterprise Knowledge Base

The repository contains operational knowledge documents that are loaded and chunked for retrieval.

The ingestion pipeline generates embeddings using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The embedding service normalizes vectors and exposes the model's embedding dimension for vector-store integration.

Qdrant stores the resulting vector representations and provides semantic retrieval.

---

# 4. MCP Tool Integration

The project includes both an **MCP client and MCP server** using Streamable HTTP.

```text
OperationsAgent
      │
      ▼
   MCP Client
      │
      │ Streamable HTTP
      ▼
   MCP Server
      │
      ├── get_service_health
      ├── get_incident_status
      └── get_runbook
```

The MCP server currently exposes three operational tools:

### `get_service_health`

Returns service health information such as:

* service status
* version
* uptime

Example services include:

* `payment-api`
* `customer-notification-service`
* `reservation-api`

### `get_incident_status`

Retrieves operational incident information using an incident identifier.

### `get_runbook`

Returns operational guidance such as:

* recommended action
* maximum retries
* escalation team

The MCP server is implemented using the Python MCP SDK and runs using Streamable HTTP.

---

# 5. Local LLM Inference

The application uses **Ollama** as the local LLM runtime and **Llama 3** as the configured model.

```text
Application
     │
     ▼
OllamaClient
     │
     ▼
Ollama
     │
     ▼
Llama 3
     │
     ▼
LLM Inference
```

The current configuration uses:

```text
Model: llama3:latest
Temperature: 0.2
Endpoint: http://localhost:11434
```

The LLM client records inference telemetry including:

* total generation duration
* model load duration
* prompt tokens
* completion tokens
* total tokens
* response length
* success/failure

This provides visibility into LLM inference performance.

---

# 6. Conversational Memory

The Operations Agent maintains conversation history using PostgreSQL.

```text
User
 │
 ▼
OperationsAgent
 │
 ├── Load conversation history
 │
 ├── Process current request
 │
 └── Persist response
       │
       ▼
   PostgreSQL
```

Conversation messages are stored through a repository abstraction backed by PostgreSQL.

This allows the agent to incorporate previous messages into subsequent requests.

---

# 7. AI Guardrails

The agent applies multiple layers of protection around the LLM workflow.

Current guardrail components include:

* Input security validation
* PII redaction
* Document safety validation
* Output validation
* RAG grounding validation
* Abstention when sufficient evidence is unavailable

The `OperationsAgent` applies input guardrails before executing the graph and validates the generated answer before storing it in conversation memory.

---

# 8. Grounding and Hallucination Protection

The RAG pipeline does not blindly return an LLM response.

After retrieving relevant documents:

1. The documents are filtered for relevance.
2. The prompt is constructed from retrieved evidence.
3. Llama 3 generates the response.
4. The response is validated against retrieved evidence.
5. Unsupported answers are rejected.
6. The system can abstain when there is insufficient evidence.

```text
Retrieved Evidence
       │
       ▼
     Llama 3
       │
       ▼
Generated Answer
       │
       ▼
Grounding Validator
       │
   ┌───┴────┐
   ▼        ▼
Supported  Unsupported
   │          │
   ▼          ▼
 Answer     Abstain
```

This provides an explicit mechanism for reducing unsupported answers in enterprise knowledge scenarios.

---

# 9. Observability

The application uses **OpenTelemetry** for distributed tracing.

Instrumentation covers important parts of the GenAI workflow, including:

* FastAPI requests
* Operations Agent
* RAG execution
* Hybrid retrieval
* LLM inference
* evaluation-related telemetry

The FastAPI application configures an OTLP HTTP exporter and instruments the FastAPI application.

Example conceptual trace:

```text
POST /agent
   │
   └── OperationsAgent.run
         │
         ├── HybridRetriever.retrieve
         │     ├── Dense Retrieval
         │     ├── BM25
         │     ├── RRF
         │     └── Reranking
         │
         ├── LLM.generate
         │
         └── Grounding Validation
```

OpenTelemetry can be connected to a compatible tracing backend such as Jaeger during development.

---

# Technology Stack

| Area                | Technology              |
| ------------------- | ----------------------- |
| Language            | Python                  |
| API                 | FastAPI                 |
| Agent orchestration | LangGraph               |
| LLM runtime         | Ollama                  |
| LLM                 | Llama 3                 |
| RAG                 | Custom RAG pipeline     |
| Embeddings          | `all-MiniLM-L6-v2`      |
| Vector database     | Qdrant                  |
| Lexical retrieval   | BM25                    |
| Retrieval fusion    | Reciprocal Rank Fusion  |
| Reranking           | Cross-encoder           |
| Tool protocol       | MCP                     |
| Persistent memory   | PostgreSQL              |
| ORM / persistence   | SQLAlchemy              |
| Observability       | OpenTelemetry           |
| Testing             | pytest                  |
| Containers          | Docker / Docker Compose |

The repository's dependency configuration includes FastAPI, Qdrant client, sentence-transformers, LangGraph, SQLAlchemy, PostgreSQL support, BM25, OpenTelemetry, MCP, and Uvicorn.

---

# Project Structure

```text
enterprise-ai-operations-copilot/
│
├── app/
│   ├── agents/
│   │   ├── operations_agent.py
│   │   ├── operations_graph.py
│   │   ├── router.py
│   │   ├── state.py
│   │   ├── conversation_memory.py
│   │   └── conversation_repository.py
│   │
│   ├── api/
│   │
│   ├── core/
│   │   ├── security_guardrails.py
│   │   ├── pii_guardrails.py
│   │   ├── output_guardrails.py
│   │   └── document_guardrails.py
│   │
│   ├── evaluation/
│   │
│   ├── llm/
│   │   └── ollama_client.py
│   │
│   ├── mcp/
│   │   ├── client.py
│   │   └── server.py
│   │
│   ├── rag/
│   │   ├── document_loader.py
│   │   ├── embedding.py
│   │   ├── bm25_retriever.py
│   │   ├── retriever.py
│   │   ├── hybrid_retriever.py
│   │   ├── rrf.py
│   │   ├── reranker.py
│   │   ├── relevance_filter.py
│   │   ├── grounding_validator.py
│   │   ├── prompt_builder.py
│   │   ├── vector_store.py
│   │   └── rag_service.py
│   │
│   └── main.py
│
├── documents/
│
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── LICENSE
```

The current repository contains dedicated packages for agents, APIs, core guardrails, evaluation, LLM, MCP, RAG, models, and tools, along with tests and container configuration.

---

# Running the Project

## Prerequisites

Install:

* Python 3.x
* Docker
* Ollama
* Llama 3 model

Qdrant and PostgreSQL can be started using Docker Compose.

---

## 1. Clone the repository

```bash
git clone https://github.com/mthatipamula/enterprise-ai-operations-copilot.git

cd enterprise-ai-operations-copilot
```

---

## 2. Create a Python virtual environment

```bash
python -m venv .venv
```

Activate it.

### macOS / Linux

```bash
source .venv/bin/activate
```

### Windows

```powershell
.venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Start infrastructure

The repository includes Docker Compose configuration for:

* Qdrant
* PostgreSQL

```bash
docker compose up -d
```

The current Compose configuration exposes Qdrant on port `6333` and PostgreSQL on port `5432`.

---

## 5. Start Ollama

Make sure Ollama is running and the configured Llama 3 model is available.

```bash
ollama pull llama3
```

Then start the Ollama service if it is not already running.

The application communicates with Ollama at:

```text
http://localhost:11434
```

---

## 6. Start the FastAPI application

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://localhost:8000
```

Health check:

```text
GET /health
```

---

# MCP Server

The MCP server can be started independently:

```bash
python -m app.mcp.server
```

The MCP endpoint uses Streamable HTTP.

```text
http://localhost:8000/mcp
```

The MCP server exposes:

```text
get_service_health
get_incident_status
get_runbook
```

For unit tests, MCP calls should be mocked where appropriate so tests do not depend on a running MCP HTTP server.

---

# Running Tests

Run the full test suite:

```bash
pytest -q
```

Run the Operations Agent tests:

```bash
pytest -v tests/test_operations_agent.py
```

Run tool-related tests:

```bash
pytest -v tests/test_operations_agent.py -k "tool"
```

The repository contains tests covering retrieval, embeddings, RAG, routing, grounding, conversation memory, MCP/tool behavior, the Ollama client, security guardrails, and the Operations Agent.

---

# Example Use Cases

## Operational Knowledge

```text
"What should I do when the payment service returns HTTP 503?"
```

The agent routes the question through RAG, retrieves relevant operational knowledge, generates an answer using Llama 3, and validates the response against the retrieved evidence.

---

## Service Health

```text
"Is the payment service currently experiencing an incident?"
```

The agent can route the request to the tool path and obtain service information through MCP.

---

## General Question

```text
"What is the purpose of exponential backoff?"
```

Questions that do not require enterprise retrieval or operational tools can use the direct LLM path.

---

# Design Principles

This project demonstrates several principles relevant to enterprise GenAI systems:

### Ground responses in enterprise knowledge

Use RAG when the answer depends on organization-specific procedures, policies, or operational documentation.

### Use tools for dynamic information

Use MCP/tool calls when information must come from an external operational capability rather than a static knowledge base.

### Do not use the LLM for everything

The architecture separates:

```text
Knowledge retrieval
Tool execution
LLM generation
```

This reduces unnecessary LLM usage and creates clearer control boundaries.

### Validate generated answers

Generated responses are validated against retrieved evidence before being returned.

### Preserve conversation context

Conversation history is persisted in PostgreSQL so subsequent requests can use prior context.

### Instrument the GenAI workflow

OpenTelemetry provides visibility into API, agent, retrieval, and LLM execution.

---

# Why This Project?

Enterprise GenAI applications require more than simply connecting an LLM to an API.

This project demonstrates an end-to-end architecture combining:

```text
LLM
+
RAG
+
Vector Search
+
Hybrid Retrieval
+
Agent Orchestration
+
Tool Calling
+
MCP
+
Conversation Memory
+
Guardrails
+
Grounding
+
Observability
```

The goal is to demonstrate how these components can work together as an enterprise-oriented AI application rather than as an isolated chatbot.

---

# Future Enhancements

Potential future production enhancements include:

* Authentication and authorization
* Document-level access control
* Production operational APIs behind MCP tools
* Persistent MCP connections
* External LLM providers
* Production-grade evaluation datasets
* Automated CI/CD
* Kubernetes deployment
* Distributed tracing backend
* Production secrets management
* Rate limiting and resilience policies

These are intentionally separated from the currently implemented core architecture.

---

# License

This project is licensed under the MIT License.

---

## Author

**Mahesh Thatipamula**

Enterprise Software Engineer | GenAI / AI Engineering

GitHub: https://github.com/mthatipamula
