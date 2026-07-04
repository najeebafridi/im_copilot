"""Construct grounded prompts for the copilot chat flow."""

from __future__ import annotations

from app.services.llm.prompt_loader import PromptLoader


class PromptBuilder:
    """Build the final prompt sent to the LLM."""

    def __init__(self, prompt_loader: PromptLoader | None = None) -> None:
        """Create a builder backed by the shared prompt loader."""

        self.prompt_loader = prompt_loader or PromptLoader()

    def build(self, question: str, context: str) -> str:
        """Combine the system instructions with retrieved context."""

        base_prompt = self.prompt_loader.load("rag_system")
        return base_prompt.format(question=question, context=context or "No context available.")
