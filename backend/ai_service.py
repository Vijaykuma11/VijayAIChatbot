import os
import requests

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.5-flash-lite:generateContent"
)


def get_ai_response(messages: list[dict]) -> str:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Gemini API Error: GEMINI_API_KEY is not configured.")
        return "AI service is not configured yet."

    contents = []
    system_instructions = []

    for message in messages[-10:]:
        role = message.get("role", "user")
        content = str(message.get("content", "")).strip()

        if not content:
            continue

        if role == "system":
            system_instructions.append(content)
            continue

        gemini_role = "model" if role in ("assistant", "model") else "user"
        part = {"text": content}

        # Combine adjacent messages with the same role.
        if contents and contents[-1]["role"] == gemini_role:
            contents[-1]["parts"].append(part)
        else:
            contents.append({
                "role": gemini_role,
                "parts": [part]
            })

    if not contents:
        return "Please enter a message."

    payload = {"contents": contents}

    if system_instructions:
        payload["systemInstruction"] = {
            "parts": [{"text": "\n".join(system_instructions)}]
        }

    try:
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

        if error.response is not None:
            print("Gemini API Details:", error.response.text[:1000])

        return "Sorry, I cannot connect to the AI right now."

    except (KeyError, IndexError, TypeError) as error:
        print("Gemini Response Error:", error)
        return "Sorry, I could not process the AI response."