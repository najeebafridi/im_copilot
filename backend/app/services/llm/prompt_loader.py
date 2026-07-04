"""Load reusable prompts from the prompts directory."""

from __future__ import annotations

from pathlib import Path


class PromptLoader:
    """Read prompt text files from disk."""

    def __init__(self, prompts_dir: Path | None = None) -> None:
        """Create a loader rooted at the backend prompts directory."""

        self.prompts_dir = prompts_dir or Path(__file__).resolve().parents[3] / "prompts"

    def load(self, name: str) -> str:
        """Load a named prompt file."""

        path = self.prompts_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        return path.read_text(encoding="utf-8").strip()
