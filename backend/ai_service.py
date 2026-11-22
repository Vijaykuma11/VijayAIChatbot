
import requests

OLLAMA_API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "qwen2.5:1.5b"


def get_ai_response(messages: list[dict]) -> str:
    try:
        payload = {
            "model": MODEL_NAME,
            "messages": messages[-10:],
            "stream": False
        }

        response = requests.post(
            OLLAMA_API_URL,
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()
        return result["message"]["content"]

    except requests.exceptions.Timeout:
        return "Sorry, the AI response took too long. Please try again."

    except requests.exceptions.RequestException as error:
        print("Ollama API Error:", error)
        return "Sorry, I cannot connect to the AI right now."
