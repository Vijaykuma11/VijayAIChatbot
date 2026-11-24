
import os
import requests

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.1-flash-lite:generateContent"
)


def get_ai_response(messages: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return "AI service is not configured yet."

    try:
        contents = []

        for message in messages[-10:]:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                role = "user"
                content = "Instructions: " + content
            elif role == "assistant":
                role = "model"
            else:
                role = "user"

            contents.append({
                "role": role,
                "parts": [{"text": str(content)}]
            })

        payload = {
            "contents": contents
        }

        response = requests.post(
            GEMINI_API_URL,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.RequestException as error:
        print("Gemini API Error:", error)
        return "Sorry, I cannot connect to the AI right now."

    except (KeyError, IndexError, TypeError) as error:
        print("Gemini Response Error:", error)
        return "Sorry, I could not process the AI response."