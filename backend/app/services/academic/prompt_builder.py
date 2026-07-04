"""Build prompts for explaining structured academic database results."""

from __future__ import annotations

import json
from typing import Any

from app.services.llm.prompt_loader import PromptLoader


class AcademicPromptBuilder:
    """Create the prompt sent to the LLM for academic answers."""

    def __init__(self, prompt_loader: PromptLoader | None = None) -> None:
        """Create a builder backed by the shared prompt loader."""

        self.prompt_loader = prompt_loader or PromptLoader()

    def build(self, question: str, data: dict[str, Any]) -> str:
        """Render the SQL prompt with the supplied question and data."""

        base_prompt = self.prompt_loader.load("sql_system")
        return base_prompt.format(
            question=question,
            data=json.dumps(data, indent=2, ensure_ascii=False),
        )
