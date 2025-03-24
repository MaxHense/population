"""
This module sets up a logger for the application.

The logger is configured to log messages to the standard output stream
with a specific format that includes the timestamp, log level, and message.

Attributes:
    logger (logging.Logger): The logger instance for this module.

Logging Configuration:
    - Log Level: INFO
    - Output Stream: sys.stdout
    - Format: "%(asctime)s - %(levelname)s - %(message)s"
"""
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.hasHandlers():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
