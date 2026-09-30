"""The reply-length note from Settings → Replies & cost.

The persona's Length ladder (``executive_persona._PERSONA_BODY``) lives in
the cached system block and is never formatted, so the setting cannot edit
it. Instead one of these constants rides in the USER turn as a
``<reply_length>`` block (``Executive._build_messages``), next to the
speaker's own ``<working_style>`` rules. "Standard" adds nothing — the
ladder alone, exactly as before the setting existed.

Constants, not templates: the text never varies, so the same setting
always produces the same bytes.
"""
from __future__ import annotations

SHORTER_REPLIES = (
    "The owner of this workspace asked for shorter replies across the board. "
    "Use the Length ladder one rung lower than the message would otherwise "
    "get: a how / should question gets one or two sentences, a real decision "
    "or trade-off gets under 100 words (the recommendation and the one "
    "variable that drives it). Board material or an explicit request for "
    "full analysis is still as long as it needs to be. The speaker's "
    "working style and anything they ask for in this message win over this "
    "note."
)

FULLER_REPLIES = (
    "The owner of this workspace asked for more detail in replies. Use the "
    "Length ladder one rung higher than the message would otherwise get: a "
    "factual question gets the answer plus the context behind it, a how / "
    "should question up to about 200 words, a real decision or trade-off up "
    "to about 400 words covering the drivers, the main risk and the next "
    "step. Still lead with the answer, and an acknowledgement is still one "
    "sentence. The speaker's working style and anything they ask for in "
    "this message win over this note."
)

_NOTES: dict[str, str] = {
    "shorter": SHORTER_REPLIES,
    "fuller": FULLER_REPLIES,
}


def reply_length_note(value: str | None) -> str:
    """The note for a reply length; "" for ``standard`` (or anything else)."""
    return _NOTES.get(value or "", "")
