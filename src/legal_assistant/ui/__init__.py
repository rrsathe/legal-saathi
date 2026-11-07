"""Legal Saathi UI package.

Provides Gradio-based user interface components and applications for the AI
Consumer Lawyer system.
"""

from __future__ import annotations

from legal_assistant.ui.app import create_app, format_ui_provenance_with_marks

__all__ = ["create_app", "format_ui_provenance_with_marks"]
