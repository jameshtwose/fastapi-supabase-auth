import logging
import uvicorn
import os
from api import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_api() -> None:
    """Run the FastAPI application."""
    if "james" in os.environ.get("USER", ""):
        logger.info("Running in James's environment")
        uvicorn.run("api:app", host="0.0.0.0", port=8080, reload=True)
    else:
        uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    run_api()
