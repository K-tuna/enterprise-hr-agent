"""
Query Endpoint - HR Agent 통합 API (DI 적용)
"""

from fastapi import APIRouter, HTTPException, Depends

from app.models import QueryRequest, QueryResponse
from app.core.deps import get_hr_agent
from core.agents import HRAgent
from core.types.errors import HRAgentError

router = APIRouter(prefix="/query")


@router.post(
    "",
    response_model=QueryResponse,
    summary="HR 질의 처리 (SQL + RAG 자동 라우팅)",
    description="자연어 질문을 넣으면 SQL Agent 또는 RAG Agent로 자동 라우팅하여 처리합니다.",
)
async def query(
    request: QueryRequest,
    hr_agent: HRAgent = Depends(get_hr_agent),  # DI로 주입
) -> QueryResponse:
    """
    HR Agent 통합 질의 엔드포인트
    """
    try:
        result = hr_agent.query(request.question)

        return QueryResponse(
            question=request.question,
            answer=result["answer"],  # AgentResult 사용
            agent_type=result["metadata"]["agent_type"],
            success=result["success"],
            error=result.get("error"),
        )

    except HRAgentError as e:
        raise HTTPException(
            status_code=400,
            detail={"code": e.code, "message": e.message},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"질의 처리 중 오류 발생: {str(e)}",
        )
