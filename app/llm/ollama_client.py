import requests


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

        if not prompt.strip():
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

        return data["response"]