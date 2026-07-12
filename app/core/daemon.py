from __future__ import annotations

import logging
import signal
from threading import Event

from app.core.logging import configure_logging


def run_keepalive_process(process_name: str, poll_interval_seconds: float = 1.0) -> None:
    configure_logging()
    logger = logging.getLogger(process_name)
    stop = Event()

    def _handle_signal(*_: object) -> None:
        stop.set()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    logger.info("%s skeleton process started", process_name)
    while not stop.wait(poll_interval_seconds):
        logger.debug("%s skeleton process waiting for work", process_name)
    logger.info("%s skeleton process stopped", process_name)
