import ollama

MODEL_NAME = "llama3.2:1b"


def ask_llama(prompt: str, json_mode=False, json_schema=None) -> str:
    """
    Send a prompt to the local Llama model.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=json_schema if json_schema else ("json" if json_mode else None),
        options={
            "temperature": 0.1,
            "num_predict": 500
        }
    )

    return response["message"]["content"]