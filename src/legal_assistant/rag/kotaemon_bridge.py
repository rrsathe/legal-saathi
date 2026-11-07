"""Kotaemon Bridge Adapter for Legal Saathi.

This module bridges the Legal Saathi Statutory Chunker and Statutory Hybrid Retriever
into Cinnamon/kotaemon's component lifecycle (theflow.base.Function / BaseComponent),
supporting multi-channel streaming (chat vs. info) and interactive HTML citation
provenance rendering on native Windows.
"""

from __future__ import annotations

import html
from collections.abc import Generator, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, Field, model_validator
from theflow.base import Param

from legal_assistant.rag.hybrid_retriever import (
    RetrievedChunk,
    StatutoryHybridRetriever,
)


class KotaemonDocument(BaseModel):
    """Document representation compatible with Cinnamon/kotaemon schema."""

    text: str = Field(default="", description="Text content of the document")
    content: Any = Field(default=None, description="Raw content or object payload")
    channel: str | None = Field(
        default=None, description="Target stream channel: chat, info, plot, debug"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Metadata dictionary")
    doc_id: str | None = Field(default=None, description="Document identifier")
    source: str | None = Field(default=None, description="Source file or origin")

    @model_validator(mode="before")
    @classmethod
    def set_content_or_text(cls, data: Any) -> Any:
        """Ensure text and content fields are synchronized.

        Args:
            data: Raw model attributes.

        Returns:
            Synchronized attributes.
        """
        if isinstance(data, dict):
            if "content" in data and ("text" not in data or not data["text"]):
                data["text"] = str(data["content"])
            elif "text" in data and ("content" not in data or data["content"] is None):
                data["content"] = data["text"]
        return data

    @property
    def plain_text(self) -> str:
        """Return string representation of text or content.

        Returns:
            str: Plain text representation.
        """
        if self.text:
            return self.text
        if isinstance(self.content, str):
            return self.content
        return ""


class KotaemonRetrievedDocument(KotaemonDocument):
    """Retrieved document carrying similarity / RRF scores and retrieval metadata."""

    score: float = Field(
        default=0.0,
        description="Relevance score (e.g., fused RRF score)",
    )
    retrieval_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Retrieval-specific metadata"
    )


if TYPE_CHECKING:
    # Explicit static typing definitions for strict mypy compliance without suppressions
    class Document(KotaemonDocument):
        """Kotaemon Document static typing definition."""

    class RetrievedDocument(KotaemonRetrievedDocument):
        """Kotaemon RetrievedDocument static typing definition."""

    class FlowFunction:
        """Typed stub for theflow.base.Function during static analysis."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            """Initialize FlowFunction stub."""
else:
    try:
        from kotaemon.base import Document as _KtemDoc
        from kotaemon.base import RetrievedDocument as _KtemRetrievedDoc

        class Document(_KtemDoc):
            """Kotaemon Document subclass."""

        class RetrievedDocument(_KtemRetrievedDoc):
            """Kotaemon RetrievedDocument subclass."""

    except ImportError:

        class Document(KotaemonDocument):
            """Fallback Document conforming to Kotaemon schema."""

        class RetrievedDocument(KotaemonRetrievedDocument):
            """Fallback RetrievedDocument conforming to Kotaemon schema."""

    from theflow.base import Function as FlowFunction


class KotaemonLegalBridge(FlowFunction):
    """Bridge adapter integrating Legal Saathi RAG with Kotaemon and Gradio UI."""

    retriever: Any = Param(default=None, help="StatutoryHybridRetriever instance")
    chunker: Any = Param(default=None, help="StatutoryChunker instance")
    confidence_threshold: float = Param(
        default=0.012, help="Minimum RRF score threshold for grounding"
    )

    def __init__(
        self,
        retriever: StatutoryHybridRetriever | None = None,
        chunker: Any | None = None,
        confidence_threshold: float = 0.012,
        **kwargs: Any,
    ) -> None:
        """Initialize KotaemonLegalBridge.

        Args:
            retriever: Configured StatutoryHybridRetriever instance.
            chunker: Configured StatutoryChunker instance.
            confidence_threshold: Minimum RRF score threshold for grounding.
            **kwargs: Additional FlowFunction keyword arguments.
        """
        active_retriever = retriever or StatutoryHybridRetriever(
            min_confidence_threshold=confidence_threshold
        )
        super().__init__(
            retriever=active_retriever,
            chunker=chunker,
            confidence_threshold=confidence_threshold,
            **kwargs,
        )

    def index_statute_corpus(
        self,
        corpus_path: Path | str,
        vector_store_path: Path | str | None = None,
    ) -> int:
        """Load and index statutory corpus files from disk.

        Args:
            corpus_path: Path to statutory text file or directory.
            vector_store_path: Optional destination directory for persistent vector store.

        Returns:
            int: Count of indexed statutory chunks.

        Raises:
            FileNotFoundError: If corpus_path does not exist.
        """
        p = Path(corpus_path).resolve()
        if not p.exists():
            raise FileNotFoundError(f"Statutory corpus path not found: {p}")

        files: list[Path] = [p] if p.is_file() else sorted(p.glob("*.txt"))
        if not files:
            return 0

        all_text = ""
        for file_path in files:
            with file_path.open("r", encoding="utf-8") as f:
                all_text += f"\n\n{f.read()}"

        if self.chunker is not None:
            raw_doc = Document(text=all_text, metadata={"source": p.as_posix()})
            chunks = (
                self.chunker.run([raw_doc])
                if hasattr(self.chunker, "run")
                else self.chunker(all_text)
            )
        else:
            chunks = [
                Document(
                    text=para.strip(),
                    metadata={"statute": "Indian Consumer Law"},
                )
                for para in all_text.split("\n\n")
                if len(para.strip()) > 30
            ]

        self.retriever.index_chunks(chunks)
        return len(chunks)

    def run(self, query: str, top_k: int = 5) -> list[RetrievedDocument]:
        """Synchronous primary execution method implementing theflow Function lifecycle.

        Args:
            query: User dispute narrative or legal question.
            top_k: Number of statutory sections to retrieve.

        Returns:
            list[RetrievedDocument]: RetrievedDocument objects with RRF scores.
        """
        chunks = self.retriever.retrieve(query=query, top_k=top_k)
        retrieved_docs: list[RetrievedDocument] = []

        for chunk in chunks:
            doc = RetrievedDocument(
                text=chunk.content,
                score=chunk.score,
                metadata={
                    "chunk_id": chunk.chunk_id,
                    "statute": chunk.statute,
                    "chapter": chunk.chapter,
                    "section": chunk.section,
                    "title": chunk.title,
                    "rank": chunk.rank,
                    "bm25_rank": chunk.bm25_rank,
                    "dense_rank": chunk.dense_rank,
                },
                retrieval_metadata={
                    "rrf_score": chunk.score,
                    "retrieval_method": chunk.retrieval_method,
                    "citation_header": f"[{chunk.statute} | Sec {chunk.section} | {chunk.title}]",
                },
            )
            retrieved_docs.append(doc)

        return retrieved_docs

    def stream_retrieval(
        self,
        query: str,
        top_k: int = 5,
    ) -> Generator[Document, None, None]:
        """Multi-channel document stream yielding chat tokens and HTML citation provenance.

        Args:
            query: Dispute query string.
            top_k: Number of chunks to retrieve.

        Yields:
            Document: Documents with channel="info" and channel="chat".
        """
        chunks, confidence = self.retriever.retrieve_with_confidence(query=query, top_k=top_k)

        # 1. Emit Citation Provenance on channel="info" for side panel
        provenance_html = self.format_ui_provenance(chunks)
        yield Document(
            channel="info",
            content=provenance_html,
            metadata={
                "type": "citation_provenance",
                "top_rrf": confidence.top_rrf_score,
            },
        )

        # 2. Check Retrieval Confidence Gate
        if not confidence.confidence_passed:
            abstention_msg = (
                confidence.abstention_message or self.retriever.DEFAULT_ABSTENTION_MESSAGE
            )
            yield Document(
                channel="chat",
                content=abstention_msg,
                metadata={"abstention": True},
            )
            return

        # 3. Grounded Context Header on channel="chat"
        intro = (
            f"**Legal Grounding Verified**: Located {len(chunks)} applicable statutory provisions "
            f"under {chunks[0].statute} (Top Grounding Score: {chunks[0].score:.4f}).\n\n"
        )
        yield Document(
            channel="chat",
            content=intro,
            metadata={"grounded": True},
        )

    def format_ui_provenance(
        self,
        chunks: Sequence[RetrievedChunk | RetrievedDocument],
        cited_sections: Sequence[str] | None = None,
    ) -> str:
        """Format interactive HTML citation cards for Gradio Information Panel.

        Args:
            chunks: Retrieved chunks or documents.
            cited_sections: Optional list of sections specifically cited.

        Returns:
            str: Collapsible statutory cards with active citation markers.
        """
        if not chunks:
            return (
                "<div style='padding: 16px; color: #64748b; font-style: italic; "
                "background-color: #f8fafc; border-radius: 8px; border: 1px dashed #cbd5e1;'>"
                "No statutory provisions retrieved.</div>"
            )

        html_blocks: list[str] = [
            "<div class='legal-provenance-panel' style='font-family: -apple-system, "
            "BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;'>",
            "<h4 style='margin: 0 0 12px 0; color: #312e81; font-weight: 700;'>"
            "Verified Statutory Grounds</h4>",
        ]

        for chunk in chunks:
            if isinstance(chunk, RetrievedChunk):
                statute = chunk.statute
                section = chunk.section
                title = chunk.title
                score = chunk.score
                content_text = chunk.content
                rank = chunk.rank
            else:
                meta = getattr(chunk, "metadata", {})
                statute = str(meta.get("statute", "Indian Consumer Law"))
                section = str(meta.get("section", "Section"))
                title = str(meta.get("title", ""))
                score = float(getattr(chunk, "score", 0.0))
                content_text = str(getattr(chunk, "text", ""))
                rank = int(meta.get("rank", 1))

            # Highlighting: if section is cited, apply distinct visual marker
            is_active_citation = False
            if cited_sections:
                for cs in cited_sections:
                    if section.lower() in cs.lower() or cs.lower() in section.lower():
                        is_active_citation = True
                        break

            border_color = "#059669" if is_active_citation else "#e2e8f0"
            bg_color = "#f0fdf4" if is_active_citation else "#ffffff"
            badge = (
                "<span style='background-color: #059669; color: white; padding: 2px 8px; "
                "border-radius: 9999px; font-size: 0.72rem; font-weight: 700; "
                "letter-spacing: 0.03em; margin-left: 8px;'>[CITED IN RESPONSE]</span>"
                if is_active_citation
                else ""
            )

            safe_text = html.escape(content_text)
            e_stat = html.escape(statute)
            e_sec = html.escape(section)
            e_title = html.escape(title)
            score_badge = (
                f"<span style='background-color: #dcfce7; color: #166534; "
                f"border: 1px solid #bbf7d0; padding: 2px 8px; border-radius: 12px; "
                f"font-size: 0.78rem; font-weight: 600; white-space: nowrap;'>"
                f"RRF: {score:.4f}</span>"
            )
            card_html = (
                f"<details class='statutory-card' style='margin-bottom: 10px; "
                f"border: 1.5px solid {border_color}; border-radius: 8px; padding: 10px 14px; "
                f"background: {bg_color}; box-shadow: 0 1px 3px rgba(0,0,0,0.04);'>\n"
                f"  <summary style='font-weight: 600; cursor: pointer; color: #312e81; "
                f"display: flex; justify-content: space-between; align-items: center;'>\n"
                f"    <span>\n"
                f"      <strong style='color: #4338ca; margin-right: 4px;'>#{rank}:</strong>\n"
                f"      <span style='background-color: #e0e7ff; color: #3730a3; padding: 2px 7px; "
                f"border-radius: 4px; font-size: 0.78rem; font-weight: 600; margin-right: 6px;'>"
                f"[{e_stat} | Sec {e_sec}]</span>\n"
                f"      <span style='color: #1e1b4b; font-weight: 600;'>{e_title}</span>\n"
                f"      {badge}\n"
                f"    </span>\n"
                f"    {score_badge}\n"
                f"  </summary>\n"
                f"  <div style='margin-top: 10px; font-size: 0.88rem; line-height: 1.55; "
                f"color: #1e293b; background: #ffffff; padding: 12px; border-radius: 6px; "
                f"border-left: 4px solid #4338ca; border-top: 1px solid #f1f5f9; "
                f"border-right: 1px solid #f1f5f9; border-bottom: 1px solid #f1f5f9; "
                f"white-space: pre-wrap;'>{safe_text}</div>\n"
                f"</details>"
            )
            html_blocks.append(card_html)

        html_blocks.append("</div>")
        return "\n".join(html_blocks)
