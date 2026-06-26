import logging
from logging import Logger
from typing import Optional


def configure_logging(level: int = logging.INFO) -> None:

    if logging.getLogger().handlers:
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def get_logger(name: Optional[str] = None) -> Logger:
    return logging.getLogger(name if name else __name__)
