import requests
from opentelemetry import trace


tracer = trace.get_tracer(__name__)


class OllamaClient:
    """
    Simple client for communicating with a local Ollama server.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3:latest",
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:
        """
        Generate a response from the configured Ollama model.
        """

        with tracer.start_as_current_span("LLM.generate") as span:
            span.set_attribute("llm.provider", "Ollama")
            span.set_attribute("llm.model", self.model)
            span.set_attribute("llm.temperature", temperature)

            if not prompt.strip():
                span.set_attribute("llm.success", False)
                raise ValueError("Prompt cannot be empty")

            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    },
                },
                timeout=120,
            )

            response.raise_for_status()

            data = response.json()

            if data.get("total_duration") is not None:
                span.set_attribute(
                    "llm.total_duration_ms",
                    data["total_duration"] / 1_000_000,
            )

            if data.get("load_duration") is not None:
                span.set_attribute(
                    "llm.load_duration_ms",
                    data["load_duration"] / 1_000_000,
            )

            if data.get("prompt_eval_count") is not None:
                span.set_attribute(
                    "llm.prompt_tokens",
                    data["prompt_eval_count"],
            )

            if data.get("eval_count") is not None:
                span.set_attribute(
                    "llm.completion_tokens",
                    data["eval_count"],
            )

            if (
                data.get("prompt_eval_count") is not None
                and data.get("eval_count") is not None
            ):
                span.set_attribute(
                    "llm.total_tokens",
                    data["prompt_eval_count"] + data["eval_count"],
                )

            answer = data["response"]

            span.set_attribute("llm.response_length", len(answer))
            span.set_attribute("llm.success", True)

            return answer