from app.llm.ollama_client import OllamaClient


def test_ollama_generation():
    client = OllamaClient()

    response = client.generate(
        "Explain HTTP 503 in one sentence."
    )

    assert response
    assert isinstance(response, str)