"""
Main FastAPI application for PulseCheck.
"""

# import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db.create_tables import create_tables
from .db.database import cleanup_db, init_db
from .routes import api_router
from .utils.config import app_settings
from .utils.logger import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Lifespan context manager for handling startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    app_logger.info("Starting up PulseCheck Service")

    if app_settings.CURRENT_ENV.lower() != "development":
        try:
            create_tables()
            # # Run alembic migrations
            # os.system("alembic upgrade head")
            # app_logger.info("Alembic migrations applied successfully.")
        except Exception as e:
            app_logger.error(f"Error during alembic upgrade: {str(e)}")

    # Initialize the database connection
    init_db()

    yield

    # Shutdown
    app_logger.info("Shutting down PulseCheck Service")
    cleanup_db()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    # Create FastAPI app with lifespan
    app = FastAPI(
        title="PulseCheck API",
        description="API for PulseCheck team activity tracker",
        version="1.0.0",
        lifespan=lifespan,
    )

    frontend_path = Path(app_settings.FRONTEND_BUILD_DIR).absolute()

    # Add a status check endpoint that's not protected by auth
    @app.get("/status")
    async def status_check():
        """Status check endpoint that doesn't require authentication."""
        return {
            "status": "ok",
            "environment": app_settings.CURRENT_ENV,
            "frontend_path": str(frontend_path) if frontend_path.exists() else None,
        }

    # Configure CORS origins
    if app_settings.CURRENT_ENV.lower() == "development":
        origins = [
            "http://localhost:5173",  # Vite default development server
            "http://localhost:8080",  # Your custom Vite port from vite.config.ts
            "http://127.0.0.1:8080",
            "http://127.0.0.1:5173",
            f"http://{app_settings.HOST}:{app_settings.PORT}",  # Backend
        ]
    else:
        origins = [
            f"{app_settings.PROTOCOL}://{app_settings.HOST}:{app_settings.PORT}",
        ]

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include the API router with /api prefix
    app.include_router(api_router, prefix="/api")

    if app_settings.CURRENT_ENV.lower() != "development":
        # Mount frontend static files if they exist
        app_logger.info(f"Frontend directory path: {frontend_path.absolute()}")

        if frontend_path.exists() and frontend_path.is_dir():
            app_logger.info(f"Mounting frontend files from {frontend_path}")

        # Mount assets directory for Vite assets (usually in /assets)
        assets_dir = frontend_path / "assets"
        if assets_dir.exists() and assets_dir.is_dir():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")
            print("Assets directory mounted successfully")

        # Serve common static files from Vite build
        static_files = {
            "favicon.ico": 86400,  # 24 hours
            "vite.svg": 86400,  # 24 hours
            "logo.svg": 86400,  # 24 hours
            "manifest.json": 3600,  # 1 hour
            "robots.txt": 86400,  # 24 hours
        }

        for static_file, cache_time in static_files.items():
            file_path = frontend_path / static_file
            if file_path.exists():

                @app.get(f"/{static_file}")
                async def serve_static_file(
                    static_file_name: str = static_file,
                    cache_seconds: int = cache_time,
                ):
                    """Serve static file with appropriate cache headers."""
                    return FileResponse(
                        path=str(frontend_path / static_file_name),
                        headers={"Cache-Control": f"public, max-age={cache_seconds}"},
                    )

        # Serve index.html for root path and all unmatched routes
        @app.get("/")
        @app.get("/{full_path:path}")
        async def serve_frontend(request: Request, full_path: str = ""):
            """
            Serve the Vite frontend application for all non-API routes.

            Args:
                request: FastAPI request object
                full_path: The requested path

            Returns:
                FileResponse: The index.html file

            Raises:
                HTTPException: If the path is an API route or if there's an error
            """
            # Skip API paths (they should be handled by the API router)
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="API endpoint not found")

            try:
                index_path = frontend_path / "index.html"
                if not index_path.exists():
                    raise HTTPException(status_code=404, detail="Frontend not found")

                return FileResponse(
                    path=str(index_path),
                    headers={"Cache-Control": "no-cache"},  # Don't cache index.html
                )
            except Exception as e:
                error_msg = f"Error serving frontend: {str(e)}"
                print(error_msg)
                raise HTTPException(status_code=500, detail=error_msg)

    return app


app = create_app()

if __name__ == "__main__":
    """
    Run the application using Uvicorn when executed directly.
    """
    import uvicorn

    # Run the application
    print(app_settings.CURRENT_ENV.lower())
    uvicorn.run(
        "backend.src.main:app",
        host=app_settings.HOST,
        port=app_settings.PORT,
        reload=app_settings.CURRENT_ENV.lower() == "development",
        reload_dirs=["backend"],  # Only watch the backend directory
        reload_excludes=[
            ".trunk",
            "node_modules",
            ".git",
        ],  # Exclude problematic directories
    )
