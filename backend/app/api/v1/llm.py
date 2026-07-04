"""LLM connectivity testing endpoint."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.llm import ChatRequest, ChatResponse
from app.services.llm.exceptions import LLMConfigurationError, LLMProviderError
from app.services.llm.service import LLMService, get_llm_service

router = APIRouter(prefix="/llm", tags=["llm"])
logger = logging.getLogger(__name__)


@router.post("/test", response_model=ChatResponse)
def test_llm(payload: ChatRequest, llm_service: LLMService = Depends(get_llm_service)) -> ChatResponse:
    """Verify that the configured LLM service is reachable."""

    try:
        return llm_service.generate(payload.message)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except LLMProviderError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

