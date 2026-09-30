"""The model an agent runs on when no Council override names one.

Resolution, for every agent on the default or deep-reasoning tier (the
Executive, the specialists and the other prose agents):

1. a Council override for that one agent (``BaseAgent.effective_model``,
   ``Executive.stream_chat``) — checked by the callers, it still wins;
2. the model picked in Settings → Replies & cost
   (``workspace_settings.workspace_model``);
3. the env tier — ``DEFAULT_MODEL`` or ``DEEP_REASONING_MODEL``.

The routing tier (``ROUTING_MODEL``, the quick checks) and ``RESEARCH_MODEL``
are deliberately not replaced: they are the cheap background models, and a
pricier pick for the conversation should not multiply their cost.

Read at call time, never cached, so a change applies from the next call.
"""
from __future__ import annotations

from openexecutive.config import get_settings


def _workspace_model() -> str | None:
    from openexecutive.memory.workspace_settings import workspace_model

    return workspace_model()


def default_model() -> str:
    """Settings' model, else ``DEFAULT_MODEL``."""
    return _workspace_model() or get_settings().default_model


def deep_reasoning_model() -> str:
    """Settings' model, else ``DEEP_REASONING_MODEL``."""
    return _workspace_model() or get_settings().deep_reasoning_model
