# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

import json
import logging
import os
import sys
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""

    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if they exist
        if hasattr(record, "agent"):
            log_obj["agent"] = record.agent
        if hasattr(record, "session_id"):
            log_obj["session_id"] = record.session_id
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


class ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for console output"""

    def format(self, record):
        # Add color coding for different log levels
        colors = {
            "DEBUG": "\033[36m",  # Cyan
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[35m",  # Magenta
        }
        reset = "\033[0m"

        color = colors.get(record.levelname, "")

        # Format: [TIME] [LEVEL] module.function:line - message
        formatted_time = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        location = f"{record.module}.{record.funcName}:{record.lineno}"

        log_line = f"[{formatted_time}] {color}[{record.levelname:8}]{reset} {location:30} - {record.getMessage()}"

        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)

        return log_line


def setup_logging(
    name: str = "lamina",
    level: str = None,
    enable_stdout: bool = True,
    enable_structured: bool = True,
    agent_name: str | None = None,
) -> logging.Logger:
    """
    Set up unified logging for the application.

    Args:
        name: Logger name (usually __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_stdout: Whether to enable console output
        enable_structured: Whether to enable structured JSON logging
        agent_name: Agent name to include in structured logs

    Returns:
        Configured logger instance
    """

    # Get log level from environment or use provided level
    if level is None:
        level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Clear existing handlers to avoid duplicates
    logger.handlers.clear()

    # Add console handler for human-readable output
    if enable_stdout:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level))
        console_handler.setFormatter(ConsoleFormatter())
        logger.addHandler(console_handler)

    # Add structured handler for Vector/Loki ingestion
    if enable_structured:
        # This will output to stdout but with JSON format
        # Vector will parse this from the container logs
        structured_handler = logging.StreamHandler(sys.stderr)
        structured_handler.setLevel(getattr(logging, level))
        structured_handler.setFormatter(StructuredFormatter())
        logger.addHandler(structured_handler)

    # Store agent name in logger for context
    if agent_name:
        logger.agent_name = agent_name

    # Prevent propagation to root logger to avoid duplicate logs
    logger.propagate = False

    return logger


def get_logger(name: str, agent_name: str | None = None) -> logging.Logger:
    """
    Get a logger instance with unified configuration.

    Args:
        name: Logger name (usually __name__)
        agent_name: Optional agent name for context

    Returns:
        Configured logger instance
    """
    return setup_logging(name, agent_name=agent_name)


class LogContext:
    """Context manager for adding extra fields to log records"""

    def __init__(self, logger: logging.Logger, **extra_fields):
        self.logger = logger
        self.extra_fields = extra_fields
        self.original_makeRecord = None

    def __enter__(self):
        self.original_makeRecord = self.logger.makeRecord

        def makeRecord(
            name, level, fn, lno, msg, args, exc_info, func=None, extra=None, sinfo=None
        ):
            if extra is None:
                extra = {}
            extra.update(self.extra_fields)
            return self.original_makeRecord(
                name, level, fn, lno, msg, args, exc_info, func, extra, sinfo
            )

        self.logger.makeRecord = makeRecord
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.makeRecord = self.original_makeRecord
