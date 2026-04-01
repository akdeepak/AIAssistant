from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.config import settings
from app.utils.logger import configure_logging
import uvicorn

configure_logging()


def create_application() -> FastAPI:
    app = FastAPI(
        title="AI-Assistant API",
        version="1.0.0",
        description="Enterprise AI Assistant Agentic solution for knowledge base management and question answering.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
