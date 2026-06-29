import os
from typing import Dict, List


class OpenAIProvider:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini").strip()

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: List[Dict[str, str]]) -> Dict[str, str]:
        if not self.is_configured():
            return {
                "status": "not_configured",
                "message": "OPENAI_API_KEY is missing from the backend environment.",
            }

        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            prompt = ""
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                prompt += f"{role.upper()}: {content}\n\n"

            response = client.responses.create(
                model=self.model,
                input=prompt,
            )

            return {
                "status": "success",
                "model": self.model,
                "message": response.output_text,
            }

        except Exception as exc:
            return {
                "status": "error",
                "model": self.model,
                "message": str(exc),
            }
