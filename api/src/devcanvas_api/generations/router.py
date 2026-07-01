"""generations 엔드포인트."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from devcanvas_api.generations.dependencies import get_llm_adapter
from devcanvas_api.generations.schemas import GenerationRequest, GenerationResponse
from devcanvas_api.generations.service import generate
from devcanvas_api.pipeline.llm import LLMAdapter

router = APIRouter(prefix="/generations", tags=["generations"])

# FastAPI 의존성 기본값 — 모듈 수준에서 한 번 평가(ruff B008 회피)
_llm_dep = Depends(get_llm_adapter)


@router.post("", response_model=GenerationResponse)
def create_generation(
    request: GenerationRequest,
    llm: LLMAdapter = _llm_dep,
) -> GenerationResponse:
    """생성 요청을 받아 파이프라인을 실행한다."""
    result = generate(request.to_generation_input(), llm)
    return GenerationResponse(**result.model_dump())
