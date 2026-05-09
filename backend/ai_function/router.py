import json
import traceback

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from jose import jwt, JWTError

from .config import load_config
from .providers import get_provider
from .skills import get_skill, list_skills

router = APIRouter(prefix="/api/ai", tags=["ai"])

security = HTTPBearer(auto_error=False)

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="无效的凭证")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="凭证已过期或无效")


class AIRequest(BaseModel):
    content: str | None = None
    selected_text: str | None = None
    instruction: str | None = None
    topic: str | None = None
    outline: str | None = None


@router.get("/skills")
def get_skills():
    return list_skills()


@router.post("/skills/{skill_name}")
async def run_skill(skill_name: str, req: AIRequest, username: str = Depends(require_auth)):
    try:
        config = load_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))

    skill_config = config.skills.get(skill_name)
    if not skill_config:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_name}' not found")

    provider_config = config.providers.get(skill_config.provider)
    if not provider_config:
        raise HTTPException(
            status_code=500,
            detail=f"Provider '{skill_config.provider}' not configured",
        )

    try:
        skill = get_skill(skill_name)
        messages = skill.build_messages(
            content=req.content,
            selected_text=req.selected_text,
            instruction=req.instruction,
            topic=req.topic,
            outline=req.outline,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    provider = get_provider(
        name=provider_config.name,
        api_key=provider_config.api_key,
        base_url=provider_config.base_url,
        extra_body=provider_config.extra_body,
    )
    model = skill_config.model or provider_config.default_model

    async def event_stream():
        try:
            async for chunk in provider.stream_chat(
                messages=messages,
                model=model,
                temperature=skill_config.temperature,
                max_tokens=skill_config.max_tokens,
            ):
                yield f"data: {json.dumps({'chunk': chunk}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            traceback.print_exc()
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
