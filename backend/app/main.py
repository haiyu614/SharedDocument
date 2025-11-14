from fastapi import FastAPI

from .api.router import api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Collaborative Document Service",
        description="MVP 后端服务：提供认证、文档、版本与实时协同接口",
        version="0.1.0",
    )

    app.include_router(api_router, prefix="/api")

    @app.get("/health", tags=["system"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()

