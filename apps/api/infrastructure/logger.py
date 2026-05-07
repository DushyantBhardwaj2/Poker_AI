import logging
import sys
import structlog
from asgi_correlation_id import correlation_id

def setup_logging():
    """
    Configures structlog to output structured JSON in production
    and human-readable logs in development.
    """
    
    # Define common processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        # Add correlation ID to every log entry
        lambda _, __, event_dict: {**event_dict, "request_id": correlation_id.get()},
    ]

    # JSON output for production, Pretty output for local dev
    if sys.stderr.isatty():
        # In a TTY (terminal), use console renderer
        renderer = structlog.dev.ConsoleRenderer()
    else:
        # In production (non-TTY), use JSON renderer for log aggregators
        renderer = structlog.processors.JSONRenderer()
        processors.append(structlog.processors.format_exc_info)

    structlog.configure(
        processors=processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Redirect standard library logging to structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

def get_logger(name: str):
    """
    Helper to get a logger instance for a given module.
    """
    return structlog.get_logger(name)
