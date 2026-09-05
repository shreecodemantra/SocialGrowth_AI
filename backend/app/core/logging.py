"""
Structured logging setup.

Emits structured (optionally JSON) logs carrying request_id / user_id /
workspace_id context so operations can be traced across services. Never log
secrets: passwords, OAuth tokens, API keys, or raw PII.
"""
import contextvars
import logging
import sys

import structlog

from app.core.config import settings

request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)
user_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("user_id", default=None)
workspace_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar("workspace_id", default=None)


def _bind_context(_, __, event_dict):
    if (rid := request_id_ctx.get()) is not None:
        event_dict["request_id"] = rid
    if (uid := user_id_ctx.get()) is not None:
        event_dict["user_id"] = uid
    if (wid := workspace_id_ctx.get()) is not None:
        event_dict["workspace_id"] = wid
    return event_dict


# Fields that must never be emitted, even accidentally by a caller.
_REDACT_KEYS = {"password", "access_token", "refresh_token", "api_key", "authorization", "secret"}


def _redact_sensitive(_, __, event_dict):
    for key in list(event_dict.keys()):
        if key.lower() in _REDACT_KEYS:
            event_dict[key] = "***REDACTED***"
    return event_dict


def configure_logging() -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )

    renderer = structlog.processors.JSONRenderer() if settings.LOG_JSON else structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            _bind_context,
            _redact_sensitive,
            structlog.processors.StackInfoRenderer(),
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None):
    return structlog.get_logger(name)
