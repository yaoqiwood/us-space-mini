from fastapi import APIRouter


router = APIRouter(prefix="/entry")


@router.get("/probe")
def probe_entry_service() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "前置页服务已连接",
    }
