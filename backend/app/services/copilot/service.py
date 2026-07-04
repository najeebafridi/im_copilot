"""Grounded chat pipeline for institutional document questions."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass

from fastapi import HTTPException, status

from app.core.config import Settings, get_settings
from app.schemas.copilot import CopilotChatResponse, CopilotMetadata, CopilotSource
from app.services.copilot.answer_validator import AnswerValidator
from app.services.copilot.context_builder import ContextBuilder
from app.services.copilot.prompt_builder import PromptBuilder
from app.services.copilot.query_preprocessor import QueryPreprocessor
from app.services.documents.retrieval import RetrievalService
from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError, LLMResponseValidationError
from app.services.llm.llm_service import LLMService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class CopilotChatService:
    """Orchestrate retrieval, prompting, generation, and validation."""

    retrieval_service: RetrievalService
    llm_service: LLMService
    preprocessor: QueryPreprocessor
    context_builder: ContextBuilder
    prompt_builder: PromptBuilder
    validator: AnswerValidator
    top_k: int

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "CopilotChatService":
        """Build the service from application settings."""

        settings = settings or get_settings()
        return cls(
            retrieval_service=RetrievalService(),
            llm_service=LLMService.from_settings(settings),
            preprocessor=QueryPreprocessor(),
            context_builder=ContextBuilder(),
            prompt_builder=PromptBuilder(),
            validator=AnswerValidator(),
            top_k=settings.COPILOT_TOP_K,
        )

    def chat(self, message: str, conversation_id: str | None = None) -> CopilotChatResponse:
        """Return a grounded response for the user question."""

        logger.info("Copilot question received conversation_id=%s", conversation_id or "ignored")
        print(f"[COPILOT] question received conversation_id={conversation_id or 'ignored'}")

        total_start = time.perf_counter()
        query = self.preprocessor.preprocess(message)

        retrieval_start = time.perf_counter()
        chunks = self.retrieval_service.search(query=query, k=self.top_k)
        retrieval_latency_ms = int((time.perf_counter() - retrieval_start) * 1000)
        logger.info("Copilot retrieval latency_ms=%s retrieved_chunks=%s", retrieval_latency_ms, len(chunks))
        print(f"[COPILOT] retrieval latency_ms={retrieval_latency_ms} retrieved_chunks={len(chunks)}")

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No relevant document chunks were found for the question.",
            )

        context, sources = self.context_builder.build(chunks)
        system_prompt = self.prompt_builder.build(question=message, context=context)

        try:
            generation = self.llm_service.generate_with_metadata(message=message, system_prompt=system_prompt)
        except (LLMConfigurationError, LLMProviderError):
            raise
        except LLMResponseValidationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

        llm_latency_ms = generation.latency_ms
        logger.info(
            "Copilot llm latency_ms=%s provider=%s model=%s",
            llm_latency_ms,
            generation.response.provider,
            generation.response.model,
        )
        print(
            f"[COPILOT] llm latency_ms={llm_latency_ms} provider={generation.response.provider} model={generation.response.model}"
        )

        try:
            answer = self.validator.validate(generation.response.response)
        except LLMResponseValidationError as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
        total_latency_ms = int((time.perf_counter() - total_start) * 1000)
        logger.info(
            "Copilot total latency_ms=%s provider=%s model=%s retrieved_chunks=%s",
            total_latency_ms,
            generation.response.provider,
            generation.response.model,
            len(chunks),
        )
        print(
            f"[COPILOT] total latency_ms={total_latency_ms} provider={generation.response.provider} model={generation.response.model}"
        )

        return CopilotChatResponse(
            answer=answer,
            sources=[CopilotSource(**source) for source in sources],
            metadata=CopilotMetadata(
                provider=generation.response.provider,
                model=generation.response.model,
                cached=generation.cached,
                latency_ms=total_latency_ms,
                retrieved_chunks=len(chunks),
            ),
        )


def get_copilot_chat_service() -> CopilotChatService:
    """FastAPI dependency for the copilot chat flow."""

    return CopilotChatService.from_settings()
