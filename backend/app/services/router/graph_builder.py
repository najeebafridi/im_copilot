"""Thin orchestration layer that dispatches to existing backend services."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.copilot import CopilotChatResponse, CopilotDebug, CopilotMetadata, CopilotSource
from app.services.router.config_loader import get_router_config
from app.services.academic.service import AcademicQueryService
from app.services.copilot.service import CopilotChatService
from app.services.router.router_service import RouterDecision


@dataclass(slots=True)
class RouterGraphBuilder:
    """Route requests to the existing node services."""

    def build_response(
        self,
        decision: RouterDecision,
        message: str,
        conversation_id: str | None,
        academic_service: AcademicQueryService,
        policy_service: CopilotChatService,
        current_user: User | None = None,
    ) -> CopilotChatResponse:
        """Return the final routed response."""

        if decision.selected_intent == "GREETING":
            return self._build_greeting_response(decision)
        if decision.selected_intent == "ACADEMIC":
            if current_user is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication is required.")
            response = academic_service.answer(message=message, current_user=current_user, conversation_id=conversation_id)
            return self._attach_debug(response, decision)
        if decision.selected_intent == "POLICY":
            response = policy_service.chat(message=message, conversation_id=conversation_id)
            return self._attach_debug(response, decision)
        return self._build_fallback_response(decision)

    def _build_greeting_response(self, decision: RouterDecision) -> CopilotChatResponse:
        """Build a friendly greeting without calling the LLM."""

        response = CopilotChatResponse(
            answer="Hello! I can help with student academic data and university policy questions.",
            sources=[],
            metadata=CopilotMetadata(
                provider="router",
                model="router",
                cached=False,
                latency_ms=decision.routing_time_ms,
                retrieved_chunks=0,
            ),
        )
        return self._attach_debug(response, decision)

    def build_auth_required_response(self, decision: RouterDecision) -> CopilotChatResponse:
        """Build a polite login-required response without calling the LLM."""

        response = CopilotChatResponse(
            answer=(
                "I can help with personal academic details like CGPA, attendance, courses, and grades, "
                "but you need to log in with a student account first."
            ),
            sources=[],
            metadata=CopilotMetadata(
                provider="router",
                model="router",
                cached=False,
                latency_ms=decision.routing_time_ms,
                retrieved_chunks=0,
            ),
        )
        return self._attach_debug(response, decision)

    def _build_fallback_response(self, decision: RouterDecision) -> CopilotChatResponse:
        """Build the configured fallback response without calling the LLM."""

        fallback_response = get_router_config().fallback_response
        response = CopilotChatResponse(
            answer=fallback_response,
            sources=[],
            metadata=CopilotMetadata(
                provider="router",
                model="router",
                cached=False,
                latency_ms=decision.routing_time_ms,
                retrieved_chunks=0,
            ),
        )
        return self._attach_debug(response, decision)

    def _attach_debug(self, response: CopilotChatResponse, decision: RouterDecision) -> CopilotChatResponse:
        """Attach router debug information when enabled."""

        debug_payload = decision.debug_payload()
        if debug_payload is None:
            return response
        return response.model_copy(update={"debug": CopilotDebug(**debug_payload)})
