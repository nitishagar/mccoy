"""Make one GPT-5.6 Luna request using the caller's OPENAI_API_KEY."""

from __future__ import annotations

from openai import OpenAI

if __name__ == "__main__":
    response = OpenAI().responses.create(model="gpt-5.6-luna", input="Reply with ok.")
    print(response.output_text)
