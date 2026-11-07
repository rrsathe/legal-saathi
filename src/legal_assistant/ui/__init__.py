"""Legal Saathi UI package.

Provides Gradio-based user interface components and applications for the AI
Consumer Lawyer system.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from legal_assistant.ui.app import create_app, format_ui_provenance_with_marks

__all__ = ["create_app", "format_ui_provenance_with_marks"]


def __getattr__(name: str) -> typing.Any:
    """Lazily load UI symbols to avoid circular import and runpy warnings."""
    if name in __all__:
        import importlib

        mod = importlib.import_module("legal_assistant.ui.app")
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Return list of public symbols for PEP 562 conformance and tab completion."""
    return list(__all__)
