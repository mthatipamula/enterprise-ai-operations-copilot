from opentelemetry import trace

from app.agents.conversation_memory import ConversationMemory
from app.agents.operations_graph import build_operations_graph
from app.core.security_guardrails import SecurityGuardrails
from app.core.pii_guardrails import PIIGuardrails
from app.core.output_guardrails import OutputGuardrails


tracer = trace.get_tracer(__name__)


class OperationsAgent:
    def __init__(self):
        self.memory = ConversationMemory()
        self.graph = build_operations_graph()
        self.guardrails = SecurityGuardrails()
        self.pii_guardrails = PIIGuardrails()
        self.output_guardrails = OutputGuardrails()

    def run(
        self,
        query: str,
        session_id: str = "default",
        user_context: dict | None = None,
    ):
        with tracer.start_as_current_span("OperationsAgent.run") as span:
            span.set_attribute("agent.name", "OperationsAgent")
            span.set_attribute("session.id", session_id)

            if not query.strip():
                span.set_attribute("agent.success", False)
                raise ValueError("Query cannot be empty")

            self.guardrails.validate_input(query)

            sanitized_query = self.pii_guardrails.redact(query)

            self.memory.add_message(
                session_id=session_id,
                role="user",
                content=sanitized_query,
            )

            messages = self.memory.get_messages(session_id)

            conversation_history = [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ]

            result = self.graph.invoke(
                {
                    "query": query,
                    "session_id": session_id,
                    "user_context": user_context or {},
                }
            )

            answer = result.get("answer", "")

            self.output_guardrails.validate(answer)

            self.memory.add_message(
                session_id=session_id,
                role="assistant",
                content=answer,
            )

            route = result["route"].value
            abstained = result.get("abstained", False)
            grounded = result.get("grounded", False)

            span.set_attribute("agent.route", route)
            span.set_attribute("agent.abstained", abstained)
            span.set_attribute("agent.grounded", grounded)
            span.set_attribute("agent.success", True)

            response = {
                "query": query,
                "route": route,
                "answer": answer,
                "sources": result.get("sources", []),
                "abstained": abstained,
                "grounded": grounded,
            }

            if result.get("tool"):
                response["tool"] = result["tool"]

            if result.get("tool_arguments"):
                response["tool_arguments"] = result["tool_arguments"]

            if result.get("tool_result"):
                response["tool_result"] = result["tool_result"]

            return response