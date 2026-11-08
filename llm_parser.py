import requests
import json

def llm_parser(text):
    prompt = f"""
You are an intent classifier for a voice-controlled ROS2 turtle.

Identify the MAIN action requested by the user.

Allowed intents:
forward, backward, left, right, stop,
faster, slower, circle, square, triangle,
spin, reset, unknown.

Important rules:
1. "Move forward slowly" means forward.
2. "Move backward slowly" means backward.
3. "Move forward faster" means forward.
4. "Increase speed" means faster.
5. "Decrease speed" means slower.
6. "Turn left slowly" means left.
7. "Stop moving" means stop.
8. Understand English, Hindi, Kannada and mixed-language commands.
9. Do not confuse movement speed descriptions with speed-change commands.

Return ONLY valid JSON:
{{"intent": "forward", "confidence": 0.95}}

If unclear:
{{"intent": "unknown", "confidence": 0.0}}

User command: {text}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:1.5b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=60
        )

        result = response.json()
        output = json.loads(result["response"])

        return output

    except Exception as e:
        print("LLM Error:", e)
        return {"intent": "unknown", "confidence": 0.0}


if __name__ == "__main__":

    while True:
        text = input("\nEnter voice command (exit to quit): ")

        if text.lower() == "exit":
            break

        result = llm_parser(text)

        print("LLM Output:", result)