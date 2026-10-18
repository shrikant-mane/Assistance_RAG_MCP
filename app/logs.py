import logging
from pathlib import Path
from app.config import PROJECT_ROOT

# Define the logs directory
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Define the log file
LOG_FILE = LOG_DIR / "mcp_debug.log"


def get_logger(name: str) -> logging.Logger:
    

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    # Avoid adding duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        # Write logs to the project root logs directory
        file_handler = logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)

        # Also display logs in the terminal
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger