from fastapi import FastAPI

from src.api.routers.resume_router import router as resume_router
from src.api.routers.skills_router import router as skills_router


def create_app() -> FastAPI:
    """
    Application factory for the CV parsing API.
    """
    app = FastAPI(
        title="CV Parser API",
        version="1.1.0",
        description="Production-oriented API for parsing CVs/resumes and extracting skills using rule-based logic and LLMs.",
    )

    app.include_router(resume_router)
    app.include_router(skills_router, prefix="/skills")

    return app


app = create_app()

