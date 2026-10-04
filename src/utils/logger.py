from pathlib import Path
from loguru import logger

from config.paths import LOGS


LOGS.mkdir(exist_ok=True)

logger.add(
    LOGS / "processing.log",
    rotation="10 MB",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

__all__ = ["logger"]