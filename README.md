# Enterprise AI Operations Copilot

An enterprise-oriented **GenAI Operations Copilot** built with Python, FastAPI, LangGraph, Retrieval-Augmented Generation (RAG), Qdrant, Ollama/Llama 3, Model Context Protocol (MCP), PostgreSQL, JWT/RBAC security, and OpenTelemetry.

The application demonstrates how an AI assistant can combine **LLM reasoning, enterprise knowledge retrieval, external tools, conversational memory, security controls, guardrails, grounding, and observability** to assist operations teams with incident and service-management questions.

> **Portfolio project:** Designed as a production-oriented GenAI reference application and as a demonstration of enterprise AI architecture patterns.

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │        Client           │
                         │      REST / Swagger      │
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
                         │   JWT Authentication    │
                         │      + RBAC             │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │    OperationsAgent      │
                         │       LangGraph         │
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
                 │   Qdrant   │   │   MCP    │   │  Ollama  │
                 │ Vector DB  │   │  Tools   │   │  Llama 3 │
                 └─────┬──────┘   └──────────┘   └──────────┘
                       │
                       ▼
                 ┌────────────┐
                 │   Hybrid   │
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

The application exposes FastAPI endpoints and routes requests through a LangGraph-based OperationsAgent. The agent selects between RAG, MCP/tool execution, and direct LLM generation.

Authentication and authorization are applied at the API boundary, while document-level access controls are propagated through the RAG pipeline.

Key Capabilities
1. Agentic Request Routing

The OperationsAgent uses LangGraph to route incoming questions to one of three paths:

RAG — questions requiring enterprise operational knowledge
Tool / MCP — questions requiring current service information
Direct LLM — general questions that do not require enterprise retrieval or tools
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

The routing workflow is implemented with LangGraph conditional edges.

2. Authentication and Authorization

The API implements JWT-based authentication and role-based access control (RBAC).

Client
  │
  ▼
POST /api/v1/auth/token
  │
  ▼
JWT Access Token
  │
  ▼
Protected API
  │
  ├── Authentication
  │
  └── Authorization / RBAC
Demo Users
User	Role	Department
operations_user	operations	payments
support_user	support	customer-support
admin_user	admin	platform

The implementation demonstrates:

JWT access tokens
Bearer authentication
Token expiration
Role-based authorization
Protected agent APIs
Protected administrative APIs
Department and role context propagation into RAG
Authentication Endpoint
POST /api/v1/auth/token

The endpoint returns a Bearer access token that can be used with protected APIs.

RBAC Example

Administrative endpoints require the admin role.

operations_user → 403 Forbidden
support_user    → 403 Forbidden
admin_user      → 200 OK

The demo credentials are intended only for local development and portfolio demonstration. Production systems should use an enterprise identity provider, secure secret storage, password hashing, token rotation, and appropriate OAuth2/OIDC flows.

3. Document-Level Access Control

The RAG pipeline propagates authenticated user context into retrieval.

JWT
 │
 ├── user_id
 ├── roles
 └── department
        │
        ▼
   OperationsAgent
        │
        ▼
       RAG
        │
        ▼
 HybridRetriever
    │         │
    ▼         ▼
  Qdrant     BM25
    │         │
    └────┬────┘
         ▼
    Authorized
     Candidates
         │
         ▼
        RRF
         │
         ▼
     Reranker

Documents contain access metadata such as:

department
allowed_roles

Both dense and lexical retrieval paths apply authorization filtering before results are fused.

The current demonstration implements:

Department-based document filtering
Role-based document filtering
Admin access
Authorization-aware dense retrieval
Authorization-aware BM25 retrieval
Authorization context propagation through the LangGraph workflow

This prevents unauthorized documents from entering the hybrid retrieval candidate set.

The current metadata is demonstration data. A production implementation would typically manage document entitlements through an enterprise authorization service or policy engine.

4. Retrieval-Augmented Generation

The RAG pipeline combines semantic and lexical retrieval.

User Query
    │
    ├───────────────┐
    ▼               ▼
Dense Retrieval   BM25 Retrieval
    │               │
    └───────┬───────┘
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
       ┌────┴────┐
       ▼         ▼
  Grounded     Abstain
   Answer

The hybrid retriever combines:

Dense semantic retrieval using Qdrant
BM25 lexical retrieval
Reciprocal Rank Fusion (RRF)
Cross-encoder reranking
Relevance filtering
Document-level authorization filtering

This approach combines semantic similarity with keyword-based retrieval for operational documentation.

The RAG service additionally applies document safety checks, relevance filtering, grounding validation, and abstention when sufficient evidence is unavailable.

5. Enterprise Knowledge Base

The repository contains operational knowledge documents that are loaded and chunked for retrieval.

The ingestion pipeline generates embeddings using:

sentence-transformers/all-MiniLM-L6-v2

Qdrant stores the resulting vector representations and provides semantic retrieval.

Document metadata is stored alongside vector representations to support authorization-aware retrieval.

6. MCP Tool Integration

The project includes both an MCP client and MCP server using Streamable HTTP.

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

The MCP server currently exposes three operational tools.

get_service_health

Returns service health information such as:

service status
version
uptime

Example services:

payment-api
customer-notification-service
reservation-api
get_incident_status

Retrieves operational incident information using an incident identifier.

get_runbook

Returns operational guidance such as:

recommended action
maximum retries
escalation team

The MCP server is implemented using the Python MCP SDK and runs using Streamable HTTP.

The current MCP server uses demonstration data. In a production environment, MCP tools would call real operational APIs, monitoring systems, incident-management platforms, or service registries.

7. Local LLM Inference

The application uses Ollama as the local LLM runtime and Llama 3 as the configured model.

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

Current configuration:

Model: llama3:latest
Temperature: 0.2
Endpoint: http://localhost:11434

The LLM client records inference telemetry including:

total generation duration
model load duration
prompt tokens
completion tokens
total tokens
response length
success/failure
8. Conversational Memory

The Operations Agent maintains conversation history using PostgreSQL.

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

Conversation messages are stored through a repository abstraction backed by PostgreSQL.

This allows the agent to incorporate previous messages into subsequent requests.

9. AI Guardrails

The agent applies multiple layers of protection around the LLM workflow.

Current guardrail components include:

Input security validation
PII redaction
Document safety validation
Output validation
RAG grounding validation
Abstention when sufficient evidence is unavailable

The OperationsAgent applies input guardrails before executing the graph and validates the generated answer before storing it in conversation memory.

10. Grounding and Hallucination Protection

The RAG pipeline does not blindly return an LLM response.

After retrieving relevant documents:

Documents are filtered for relevance.
The prompt is constructed from retrieved evidence.
Llama 3 generates the response.
The response is validated against retrieved evidence.
Unsupported answers are rejected.
The system can abstain when there is insufficient evidence.
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
    ┌──┴────┐
    ▼       ▼
Supported Unsupported
    │       │
    ▼       ▼
 Answer   Abstain
11. Observability

The application uses OpenTelemetry for distributed tracing.

Instrumentation covers important parts of the GenAI workflow, including:

FastAPI requests
Operations Agent
RAG execution
Hybrid retrieval
LLM inference
Evaluation-related telemetry

Example conceptual trace:

POST /api/v1/agent/chat
   │
   └── OperationsAgent.run
         │
         ├── Intent Routing
         │
         ├── HybridRetriever.retrieve
         │     ├── Dense Retrieval
         │     ├── BM25
         │     ├── RRF
         │     └── Reranking
         │
         ├── MCP Tool Call
         │
         ├── LLM.generate
         │
         └── Grounding Validation

OpenTelemetry can be connected to a compatible tracing backend such as Jaeger during development.

Technology Stack
Area	Technology
Language	Python
API	FastAPI
Authentication	JWT / Bearer
Authorization	RBAC
Agent orchestration	LangGraph
LLM runtime	Ollama
LLM	Llama 3
RAG	Custom RAG pipeline
Embeddings	all-MiniLM-L6-v2
Vector database	Qdrant
Lexical retrieval	BM25
Retrieval fusion	Reciprocal Rank Fusion
Reranking	Cross-encoder
Tool protocol	MCP
Persistent memory	PostgreSQL
ORM / persistence	SQLAlchemy
Observability	OpenTelemetry
Testing	pytest
Containers	Docker / Docker Compose
Project Structure
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
│   │   ├── auth.py
│   │   ├── agent.py
│   │   ├── admin.py
│   │   └── search.py
│   │
│   ├── core/
│   │   ├── security.py
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
│   ├── models/
│   │   └── document_access.py
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
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pytest.ini
└── LICENSE
Running the Project
Prerequisites

Install:

Python 3.x
Docker
Ollama
Llama 3 model

Qdrant and PostgreSQL can be started using Docker Compose.

1. Clone the Repository
git clone https://github.com/mthatipamula/enterprise-ai-operations-copilot.git

cd enterprise-ai-operations-copilot
2. Create a Python Virtual Environment
python -m venv .venv
macOS / Linux
source .venv/bin/activate
Windows
.venv\Scripts\activate
3. Install Dependencies
pip install -r requirements.txt
4. Start Infrastructure

The repository includes Docker Compose configuration for:

Qdrant
PostgreSQL
docker compose up -d

Qdrant:

http://localhost:6333

PostgreSQL:

localhost:5432
5. Start Ollama

Make sure Ollama is running and the configured Llama 3 model is available.

ollama pull llama3

The application communicates with Ollama at:

http://localhost:11434
6. Start the FastAPI Application
uvicorn app.main:app --reload

Application:

http://localhost:8000

Swagger UI:

http://localhost:8000/docs

Health check:

GET /health
Authentication Flow

First obtain a JWT token.

curl -X POST \
  "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=operations_user&password=operations123"

The response contains:

{
  "access_token": "<JWT>",
  "token_type": "bearer"
}

Use the token to call protected APIs:

curl -X POST \
  "http://localhost:8000/api/v1/agent/chat" \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "query": "What should I do when the payment service returns HTTP 503?"
  }'

Swagger UI can also be used to authenticate through the Authorize button.

RBAC Example

Test the administrative endpoint:

GET /api/v1/admin/status

Expected behavior:

operations_user → 403 Forbidden
support_user    → 403 Forbidden
admin_user      → 200 OK

This demonstrates API-level role-based access control.

MCP Server

The MCP server can be started independently:

python -m app.mcp.server

MCP endpoint:

http://localhost:8000/mcp

Available tools:

get_service_health
get_incident_status
get_runbook

For unit tests, MCP calls should be mocked where appropriate so tests do not depend on a running MCP HTTP server.

Running Tests

Run the full test suite:

pytest -q

Run Operations Agent tests:

pytest -v tests/test_operations_agent.py

Run tool-related tests:

pytest -v tests/test_operations_agent.py -k "tool"

The repository contains tests covering retrieval, embeddings, RAG, routing, grounding, conversation memory, MCP/tool behavior, the Ollama client, security guardrails, authentication/authorization, and the Operations Agent.

Example Use Cases
Operational Knowledge
"What should I do when the payment service returns HTTP 503?"

The agent routes the question through RAG, retrieves relevant operational knowledge, generates an answer using Llama 3, and validates the response against retrieved evidence.

Service Health
"Is the payment service currently experiencing an incident?"

The agent can route the request to the tool path and obtain service information through MCP.

General Question
"What is the purpose of exponential backoff?"

Questions that do not require enterprise retrieval or operational tools can use the direct LLM path.

Secured Knowledge Retrieval

Authenticated users receive retrieval results based on their department and roles.

For example:

operations_user
    │
    ▼
department = payments
role = operations
    │
    ▼
Payments documents

Unauthorized users are prevented from contributing documents to the hybrid retrieval candidate set.

Design Principles
Ground Responses in Enterprise Knowledge

Use RAG when the answer depends on organization-specific procedures, policies, or operational documentation.

Use Tools for Dynamic Information

Use MCP/tool calls when information must come from an external operational capability rather than a static knowledge base.

Do Not Use the LLM for Everything

The architecture separates:

Knowledge retrieval
Tool execution
LLM generation

This reduces unnecessary LLM usage and creates clearer control boundaries.

Enforce Authorization Before Generation

Document-level authorization is applied during retrieval so unauthorized knowledge is excluded before it reaches the LLM context.

Validate Generated Answers

Generated responses are validated against retrieved evidence before being returned.

Preserve Conversation Context

Conversation history is persisted in PostgreSQL so subsequent requests can use prior context.

Instrument the GenAI Workflow

OpenTelemetry provides visibility into API, agent, retrieval, and LLM execution.

Why This Project?

Enterprise GenAI applications require more than simply connecting an LLM to an API.

This project demonstrates an end-to-end architecture combining:

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
Authentication
+
RBAC
+
Document-Level Access Control
+
Conversation Memory
+
Guardrails
+
Grounding
+
Observability

The goal is to demonstrate how these components can work together as an enterprise-oriented AI application rather than as an isolated chatbot.

Future Enhancements

Potential future production enhancements include:

Production identity provider / OAuth2 / OIDC integration
Production authorization service or policy engine
Production operational APIs behind MCP tools
Persistent MCP connections
External LLM providers
Production-grade evaluation datasets
Automated CI/CD
Kubernetes deployment
Distributed tracing backend
Production secrets management
Rate limiting and resilience policies
More sophisticated multi-role authorization policies
License

This project is licensed under the MIT License.

Author

Mahesh Thatipamula

Enterprise Software Engineer | GenAI / AI Engineering

GitHub: https://github.com/mthatipamula