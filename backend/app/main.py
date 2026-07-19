from fastapi import FastAPI

from app.api.router import api_router


app = FastAPI(
    title="Couple Space API",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)
app.include_router(api_router)


@app.get("/health", include_in_schema=False)
def root_health_check() -> dict[str, str]:
    return {"status": "ok"}
