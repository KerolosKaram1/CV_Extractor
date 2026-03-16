from fastapi import FastAPI

from src.api.routers.skills_router import router as skills_router


def create_app() -> FastAPI:
    """
    Application factory for the CV Skill Extraction API.
    """
    app = FastAPI(
        title="CV Skill Extractor",
        version="1.0.0",
        description="Production-oriented API for extracting candidate name and skills from CV documents using Qwen via OpenRouter.",
    )

    app.include_router(skills_router, prefix="/skills")

    return app


app = create_app()

