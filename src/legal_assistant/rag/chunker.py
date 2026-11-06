"""Structure-aware legal chunker preserving statutory hierarchies.

Splits Indian statutory texts (CPA 2019, E-Commerce Rules 2020, 2021 Pecuniary
Rules, e-Daakhil procedures) into atomic, semantically coherent chunks with
canonical breadcrumb headers and structured metadata. Conforms to Kotaemon's
BaseSplitter and Document interfaces.
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field, model_validator


# ------------------------------------------------------------------------------
# Kotaemon / LlamaIndex Compatibility Layer
# ------------------------------------------------------------------------------
class Document(BaseModel):
    """Document conforming to Kotaemon Document schema."""

    text: str = ""
    content: Any = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    channel: str | None = None
    source: str | None = None
    doc_id: str | None = None

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
            if "content" in data and "text" not in data:
                data["text"] = str(data["content"])
            elif "text" in data and "content" not in data:
                data["content"] = data["text"]
        return data


class BaseSplitter:
    """BaseSplitter conforming to Kotaemon BaseSplitter interface."""

    def run(self, documents: list[Document], **kwargs: Any) -> list[Document]:
        """Execute chunking over documents.

        Args:
            documents: Input documents to chunk.
            **kwargs: Additional execution options.

        Raises:
            NotImplementedError: In base class.
        """
        raise NotImplementedError

    def __call__(self, documents: list[Document], **kwargs: Any) -> list[Document]:
        """Allow instance to be called directly.

        Args:
            documents: Input documents to chunk.
            **kwargs: Additional execution options.

        Returns:
            list[Document]: Output documents.
        """
        return self.run(documents, **kwargs)


# ------------------------------------------------------------------------------
# Data Models
# ------------------------------------------------------------------------------
class StatutoryChunkMetadata(BaseModel):
    """Structured legal metadata extracted from statutory chunks."""

    statute: str = Field(description="Official name of the Act or Rules")
    chapter: str = Field(description="Chapter Roman numeral or 'N/A'")
    section: str = Field(description="Section number or Rule number")
    section_title: str = Field(description="Title or descriptive subject of the section")
    clause: str = Field(description="Subsection or clause identifier")
    act_year: int = Field(description="Calendar year of enactment or notification")
    chunk_id: str = Field(description="Unique deterministic chunk slug")
    breadcrumb: str = Field(description="Canonical statutory breadcrumb string")
    cross_references: list[str] = Field(
        default_factory=list, description="Cross-referenced sections or rules"
    )
    char_count: int = Field(default=0, description="Character count of chunk body")


class StatutoryChunk(BaseModel):
    """Data carrier representing a structure-aware statutory chunk."""

    chunk_id: str
    content: str
    metadata: StatutoryChunkMetadata

    def to_document(self) -> Document:
        """Convert chunk into a Kotaemon-compatible Document instance.

        Returns:
            Document: Kotaemon Document with text, metadata, and info channel.
        """
        meta_dict = self.metadata.model_dump()
        return Document(
            text=self.content,
            metadata=meta_dict,
            doc_id=self.chunk_id,
            channel="info",
        )


# ------------------------------------------------------------------------------
# Statutory Chunker Implementation
# ------------------------------------------------------------------------------
class StatutoryChunker(BaseSplitter):
    """Structure-aware legal chunker preserving statutory hierarchies.

    Preserves Act > Chapter > Section > Sub-clause hierarchies, prepends
    standardized breadcrumbs, extracts structured metadata, and maintains atomic
    sub-clause boundaries.
    """

    def __init__(self, max_chunk_chars: int = 1500) -> None:
        """Initialize the statutory chunker.

        Args:
            max_chunk_chars: Maximum character budget before splitting a section
                into individual subsections or clauses.
        """
        super().__init__()
        self.max_chunk_chars = max_chunk_chars

    @staticmethod
    def extract_year(statute_name: str) -> int:
        """Extract four-digit enactment year from statute name.

        Args:
            statute_name: Official name of the statute.

        Returns:
            int: Enactment year or default 2019.
        """
        match = re.search(r"\b(19\d\d|20\d\d)\b", statute_name)
        return int(match.group(1)) if match else 2019

    @staticmethod
    def extract_cross_references(text: str) -> list[str]:
        """Extract explicit statutory cross-references using regex.

        Args:
            text: Text content of the statutory chunk.

        Returns:
            list[str]: Sorted list of unique referenced sections or rules.
        """
        patterns = [
            r"\b(?:Section|Sec\.?)\s*(\d+[A-Za-z]?(?:\(\d+\))*(?:\([a-z]+\))*)",
            r"\bRule\s*(\d+[A-Za-z]?(?:\(\d+\))*)",
            r"\bsub-section\s*\(([0-9]+)\)",
            r"\bclause\s*\(([0-9a-zA-Z]+)\)",
            r"\bChapter\s*([IVXLCDM\d]+)",
        ]
        refs: set[str] = set()
        for p in patterns:
            for m in re.finditer(p, text, re.IGNORECASE):
                refs.add(m.group(0).strip())
        return sorted(refs)

    @staticmethod
    def parse_statute_name(text: str, default: str = "Consumer Protection Act, 2019") -> str:
        """Detect and normalize statute name from document header.

        Args:
            text: Raw document text.
            default: Fallback statute name if not detected in text.

        Returns:
            str: Normalized statutory name.
        """
        statute_match = re.search(
            r"^(?:THE\s+)?([A-Z\s\(\)\-,]+(?:ACT|RULES|REGULATIONS|GUIDELINES)[A-Z\s\(\)\-,0-9]*)\b",
            text,
            re.MULTILINE,
        )
        if statute_match:
            raw = statute_match.group(0).strip().title()
            if "Consumer Protection Act" in raw:
                return "Consumer Protection Act, 2019"
            if "E-Commerce" in raw or "Ecommerce" in raw:
                return "Consumer Protection (E-Commerce) Rules, 2020"
            if "Jurisdiction" in raw:
                return "Consumer Protection (Jurisdiction of Commissions) Rules, 2021"
            return raw
        return default

    def split_text(
        self,
        text: str,
        default_statute: str = "Consumer Protection Act, 2019",
        default_chapter: str = "N/A",
    ) -> list[StatutoryChunk]:
        """Parse raw statutory text into hierarchical statutory chunks.

        Supports both canonical delimiter blocks (`====...====` with metadata
        headers) and bare statutory text formatted with Chapter and Section headers.

        Args:
            text: Full raw statutory text.
            default_statute: Default statute name if undetected.
            default_chapter: Default chapter identifier if undetected.

        Returns:
            list[StatutoryChunk]: List of structured statutory chunks.
        """
        if not text.strip():
            return []

        # Check if text contains canonical delimiter blocks
        if re.search(r"(?m)^={60,}", text):
            return self._split_delimited_text(
                text,
                default_statute=default_statute,
                default_chapter=default_chapter,
            )

        statute = self.parse_statute_name(text, default=default_statute)
        act_year = self.extract_year(statute)

        # Detect Chapter divisions
        chapter_regex = re.compile(
            r"(?:^|\n)(?:#{1,3}\s*)?(CHAPTER\s+([IVXLCDM\d]+))\s*\n+([A-Z\s,\-]+)(?=\n)",
            re.IGNORECASE,
        )
        chapters: list[tuple[str, str, str]] = []
        ch_matches = list(chapter_regex.finditer(text))

        if ch_matches:
            for i, match in enumerate(ch_matches):
                ch_num = match.group(2).strip().upper()
                ch_title = match.group(3).strip().title()
                start_pos = match.end()
                end_pos = ch_matches[i + 1].start() if i + 1 < len(ch_matches) else len(text)
                ch_content = text[start_pos:end_pos].strip()
                chapters.append((ch_num, ch_title, ch_content))
        else:
            chapters.append((default_chapter, "General", text))

        chunks: list[StatutoryChunk] = []

        # Section or Rule regex supporting Bare Acts, Rules, and Markdown
        section_regex = re.compile(
            r"(?:^|\n)\s*(?:#{1,6}\s*)?(?:"
            r"(?:Section|Sec\.?)\s*(\d+[A-Za-z]?)|"
            r"Rule\s*(\d+[A-Za-z]?)|"
            r"(\d+[A-Za-z]?)\."
            r")\s*[:\-\.]?\s*([^\n\r—]+?)(?:\.—|—|--|:|\n)",
            re.MULTILINE,
        )

        for ch_num, ch_title, ch_content in chapters:
            sec_matches = list(section_regex.finditer(ch_content))
            if not sec_matches:
                if ch_content.strip():
                    breadcrumb = (
                        f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                        f"SECTION: General | CLAUSE: General]"
                    )
                    content = f"{breadcrumb}\n[TITLE: {ch_title}]\n{ch_content.strip()}"
                    sec_clean = "general"
                    chunk_id = f"{statute[:3].lower()}_{act_year}_ch_{ch_num.lower()}_{sec_clean}"
                    chunks.append(
                        StatutoryChunk(
                            chunk_id=chunk_id,
                            content=content,
                            metadata=StatutoryChunkMetadata(
                                statute=statute,
                                chapter=ch_num,
                                section="General",
                                section_title=ch_title,
                                clause="General",
                                act_year=act_year,
                                chunk_id=chunk_id,
                                breadcrumb=breadcrumb,
                                cross_references=self.extract_cross_references(content),
                                char_count=len(content),
                            ),
                        )
                    )
                continue

            for i, s_match in enumerate(sec_matches):
                if s_match.group(1):
                    sec_num = s_match.group(1).strip()
                elif s_match.group(2):
                    sec_num = f"Rule {s_match.group(2).strip()}"
                else:
                    sec_num = s_match.group(3).strip()

                sec_title = s_match.group(4).strip().rstrip(".-—")
                sec_body_start = s_match.end()
                sec_body_end = (
                    sec_matches[i + 1].start() if i + 1 < len(sec_matches) else len(ch_content)
                )
                sec_body = ch_content[sec_body_start:sec_body_end].strip()

                is_definitions = sec_num == "2" or "definition" in sec_title.lower()

                if is_definitions:
                    self._parse_definitions(
                        sec_body=sec_body,
                        statute=statute,
                        ch_num=ch_num,
                        act_year=act_year,
                        chunks=chunks,
                    )
                else:
                    self._parse_section(
                        sec_num=sec_num,
                        sec_title=sec_title,
                        sec_body=sec_body,
                        statute=statute,
                        ch_num=ch_num,
                        act_year=act_year,
                        chunks=chunks,
                    )

        return chunks

    def _split_delimited_text(
        self,
        text: str,
        default_statute: str = "Consumer Protection Act, 2019",
        default_chapter: str = "N/A",
    ) -> list[StatutoryChunk]:
        """Parse structured statutory text formatted with canonical delimiters.

        Args:
            text: Delimited statutory text.
            default_statute: Default statute name if undetected.
            default_chapter: Default chapter identifier if undetected.

        Returns:
            list[StatutoryChunk]: List of parsed statutory chunks.
        """
        raw_blocks = re.split(r"(?m)^={60,}\r?\n", text)
        chunks: list[StatutoryChunk] = []

        i = 0
        while i < len(raw_blocks):
            block = raw_blocks[i].strip()
            if not block:
                i += 1
                continue

            # Check if this block is a metadata header block
            if "STATUTE:" in block and "SECTION:" in block:
                meta_block = block
                body_block = raw_blocks[i + 1].strip() if i + 1 < len(raw_blocks) else ""
                i += 2

                statute = self._extract_header_val(meta_block, "STATUTE", default_statute)
                chapter = self._extract_header_val(meta_block, "CHAPTER", default_chapter)
                section = self._extract_header_val(meta_block, "SECTION", "General")
                title = self._extract_header_val(meta_block, "TITLE", "Statutory Provision")
                clause = self._extract_header_val(meta_block, "CLAUSE", "General")
                act_year_str = self._extract_header_val(meta_block, "ACT_YEAR", "2019")
                act_year = (
                    int(act_year_str) if act_year_str.isdigit() else self.extract_year(statute)
                )

                # Extract cross-references
                cross_refs_raw = self._extract_header_val(meta_block, "CROSS_REFS", "")
                cross_refs = (
                    [r.strip() for r in cross_refs_raw.split(",") if r.strip()]
                    if cross_refs_raw
                    else self.extract_cross_references(body_block)
                )

                # Canonical breadcrumb
                breadcrumb = (
                    f"[STATUTE: {statute} | CHAPTER: {chapter} | "
                    f"SECTION: {section} | CLAUSE: {clause}]"
                )
                content = f"{breadcrumb}\n[TITLE: {title}]\n{body_block}"

                # Generate clean chunk ID
                sec_clean = re.sub(r"[^\w]", "_", section).lower()
                ch_clean = re.sub(r"[^\w]", "_", chapter).lower()
                chunk_id = f"{statute[:3].lower()}_{act_year}_ch_{ch_clean}_sec_{sec_clean}"

                chunks.append(
                    StatutoryChunk(
                        chunk_id=chunk_id,
                        content=content,
                        metadata=StatutoryChunkMetadata(
                            statute=statute,
                            chapter=chapter,
                            section=section,
                            section_title=title,
                            clause=clause,
                            act_year=act_year,
                            chunk_id=chunk_id,
                            breadcrumb=breadcrumb,
                            cross_references=cross_refs,
                            char_count=len(content),
                        ),
                    )
                )
            else:
                i += 1

        return chunks

    @staticmethod
    def _extract_header_val(header_text: str, key: str, default: str) -> str:
        """Extract value of a key-value pair from header block.

        Args:
            header_text: Text of header block.
            key: Field key (e.g. 'STATUTE', 'SECTION').
            default: Fallback if key is missing.

        Returns:
            str: Extracted value.
        """
        match = re.search(rf"^{key}:\s*(.+)$", header_text, re.MULTILINE)
        return match.group(1).strip() if match else default

    def _parse_definitions(
        self,
        sec_body: str,
        statute: str,
        ch_num: str,
        act_year: int,
        chunks: list[StatutoryChunk],
    ) -> None:
        """Parse Section 2 definition clauses (e.g., 2(7), 2(10), 2(47)).

        Args:
            sec_body: Text content of Section 2.
            statute: Name of the statute.
            ch_num: Chapter number.
            act_year: Year of the Act.
            chunks: Destination accumulator for generated chunks.
        """
        def_regex = re.compile(
            r"(?:^|\n)\(([0-9]+)\)\s*(?:“|\"|')?([a-zA-Z\s\-]+?)(?:”|\"|')?\s+(?:means|includes)\b",
            re.MULTILINE,
        )
        def_matches = list(def_regex.finditer(sec_body))
        if not def_matches:
            breadcrumb = f"[STATUTE: {statute} | CHAPTER: {ch_num} | SECTION: 2 | CLAUSE: General]"
            content = f"{breadcrumb}\n[TITLE: Definitions]\n{sec_body}"
            chunk_id = f"{statute[:3].lower()}_{act_year}_ch_{ch_num.lower()}_sec_2"
            chunks.append(
                StatutoryChunk(
                    chunk_id=chunk_id,
                    content=content,
                    metadata=StatutoryChunkMetadata(
                        statute=statute,
                        chapter=ch_num,
                        section="2",
                        section_title="Definitions",
                        clause="General",
                        act_year=act_year,
                        chunk_id=chunk_id,
                        breadcrumb=breadcrumb,
                        cross_references=self.extract_cross_references(content),
                        char_count=len(content),
                    ),
                )
            )
            return

        for d_i, d_match in enumerate(def_matches):
            def_num = d_match.group(1)
            term_name = d_match.group(2).strip()
            d_start = d_match.start()
            d_end = def_matches[d_i + 1].start() if d_i + 1 < len(def_matches) else len(sec_body)
            def_text = sec_body[d_start:d_end].strip()

            effective_sec = f"2({def_num})"
            effective_title = f"Definition of '{term_name}'"

            # Check if definition exceeds chunk limit and has nested subclauses
            if len(def_text) > self.max_chunk_chars:
                sub_regex = re.compile(r"(?:^|\n)\(([a-z])\)\s+", re.MULTILINE)
                raw_matches = list(sub_regex.finditer(def_text))
                # Only keep alphabetical clauses that follow sequential order
                # to prevent roman numerals like (i) being misidentified as clause (i)
                sub_matches: list[re.Match[str]] = []
                expected_ord = ord("a")
                for m in raw_matches:
                    if ord(m.group(1)) == expected_ord:
                        sub_matches.append(m)
                        expected_ord += 1

                if sub_matches:
                    stem = def_text[: sub_matches[0].start()].strip()
                    for s_i, sub_m in enumerate(sub_matches):
                        sub_letter = sub_m.group(1)
                        sub_start = sub_m.start()
                        sub_end = (
                            sub_matches[s_i + 1].start()
                            if s_i + 1 < len(sub_matches)
                            else len(def_text)
                        )
                        sub_text = def_text[sub_start:sub_end].strip()

                        # Check for roman numeral sub-subclauses (i), (ii) within subclause
                        roman_regex = re.compile(r"(?:^|\n)\(([ivxlcdm]+)\)\s+", re.MULTILINE)
                        roman_matches = list(roman_regex.finditer(sub_text))

                        if len(sub_text) > self.max_chunk_chars and roman_matches:
                            sub_stem = sub_text[: roman_matches[0].start()].strip()
                            for r_i, r_m in enumerate(roman_matches):
                                roman_num = r_m.group(1)
                                r_start = r_m.start()
                                r_end = (
                                    roman_matches[r_i + 1].start()
                                    if r_i + 1 < len(roman_matches)
                                    else len(sub_text)
                                )
                                roman_text = sub_text[r_start:r_end].strip()
                                clause_id = f"({sub_letter})({roman_num})"
                                breadcrumb = (
                                    f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                                    f"SECTION: {effective_sec} | CLAUSE: {clause_id}]"
                                )
                                content = (
                                    f"{breadcrumb}\n[TITLE: {effective_title}]\n"
                                    f"{stem}\n{sub_stem}\n{roman_text}"
                                )
                                chunk_id = (
                                    f"{statute[:3].lower()}_{act_year}_ch_"
                                    f"{ch_num.lower()}_sec_2_{def_num}_cl_"
                                    f"{sub_letter}_{roman_num}"
                                )
                                chunks.append(
                                    StatutoryChunk(
                                        chunk_id=chunk_id,
                                        content=content,
                                        metadata=StatutoryChunkMetadata(
                                            statute=statute,
                                            chapter=ch_num,
                                            section=effective_sec,
                                            section_title=effective_title,
                                            clause=clause_id,
                                            act_year=act_year,
                                            chunk_id=chunk_id,
                                            breadcrumb=breadcrumb,
                                            cross_references=self.extract_cross_references(content),
                                            char_count=len(content),
                                        ),
                                    )
                                )
                            continue

                        clause_id = f"({sub_letter})"
                        breadcrumb = (
                            f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                            f"SECTION: {effective_sec} | CLAUSE: {clause_id}]"
                        )
                        content = f"{breadcrumb}\n[TITLE: {effective_title}]\n{stem}\n{sub_text}"
                        chunk_id = (
                            f"{statute[:3].lower()}_{act_year}_ch_"
                            f"{ch_num.lower()}_sec_2_{def_num}_cl_{sub_letter}"
                        )
                        chunks.append(
                            StatutoryChunk(
                                chunk_id=chunk_id,
                                content=content,
                                metadata=StatutoryChunkMetadata(
                                    statute=statute,
                                    chapter=ch_num,
                                    section=effective_sec,
                                    section_title=effective_title,
                                    clause=clause_id,
                                    act_year=act_year,
                                    chunk_id=chunk_id,
                                    breadcrumb=breadcrumb,
                                    cross_references=self.extract_cross_references(content),
                                    char_count=len(content),
                                ),
                            )
                        )
                    continue

            # Standard definition fitting within size budget
            clause_id = f"({def_num})"
            breadcrumb = (
                f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                f"SECTION: {effective_sec} | CLAUSE: {clause_id}]"
            )
            content = f"{breadcrumb}\n[TITLE: {effective_title}]\n{def_text}"
            chunk_id = f"{statute[:3].lower()}_{act_year}_ch_{ch_num.lower()}_sec_2_{def_num}"
            chunks.append(
                StatutoryChunk(
                    chunk_id=chunk_id,
                    content=content,
                    metadata=StatutoryChunkMetadata(
                        statute=statute,
                        chapter=ch_num,
                        section=effective_sec,
                        section_title=effective_title,
                        clause=clause_id,
                        act_year=act_year,
                        chunk_id=chunk_id,
                        breadcrumb=breadcrumb,
                        cross_references=self.extract_cross_references(content),
                        char_count=len(content),
                    ),
                )
            )

    def _parse_section(
        self,
        sec_num: str,
        sec_title: str,
        sec_body: str,
        statute: str,
        ch_num: str,
        act_year: int,
        chunks: list[StatutoryChunk],
    ) -> None:
        """Parse standard section or rule with sub-sections.

        Args:
            sec_num: Section or Rule number.
            sec_title: Section title.
            sec_body: Body text of the section.
            statute: Statute name.
            ch_num: Chapter Roman numeral.
            act_year: Year of statute.
            chunks: Destination accumulator.
        """
        subsec_regex = re.compile(r"(?:^|\n)\(([0-9]+)\)\s+", re.MULTILINE)
        subsec_matches = list(subsec_regex.finditer(sec_body))

        sec_clean = re.sub(r"[^\w]", "_", sec_num).lower()

        # If fits within max_chunk_chars or no numbered subsections, keep intact as atomic section
        if len(sec_body) <= self.max_chunk_chars or not subsec_matches:
            clause_id = "General"
            breadcrumb = (
                f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                f"SECTION: {sec_num} | CLAUSE: {clause_id}]"
            )
            content = f"{breadcrumb}\n[TITLE: {sec_title}]\n{sec_body}"
            chunk_id = f"{statute[:3].lower()}_{act_year}_ch_{ch_num.lower()}_sec_{sec_clean}"
            chunks.append(
                StatutoryChunk(
                    chunk_id=chunk_id,
                    content=content,
                    metadata=StatutoryChunkMetadata(
                        statute=statute,
                        chapter=ch_num,
                        section=sec_num,
                        section_title=sec_title,
                        clause=clause_id,
                        act_year=act_year,
                        chunk_id=chunk_id,
                        breadcrumb=breadcrumb,
                        cross_references=self.extract_cross_references(content),
                        char_count=len(content),
                    ),
                )
            )
        else:
            # Multi-subsection splitting: never break inside a subsection
            stem = sec_body[: subsec_matches[0].start()].strip()
            for sub_i, sub_m in enumerate(subsec_matches):
                sub_num = sub_m.group(1)
                sub_start = sub_m.start()
                sub_end = (
                    subsec_matches[sub_i + 1].start()
                    if sub_i + 1 < len(subsec_matches)
                    else len(sec_body)
                )
                sub_text = sec_body[sub_start:sub_end].strip()
                clause_id = f"({sub_num})"
                breadcrumb = (
                    f"[STATUTE: {statute} | CHAPTER: {ch_num} | "
                    f"SECTION: {sec_num} | CLAUSE: {clause_id}]"
                )
                body_text = f"{stem}\n{sub_text}" if stem else sub_text
                content = f"{breadcrumb}\n[TITLE: {sec_title}]\n{body_text}"
                chunk_id = (
                    f"{statute[:3].lower()}_{act_year}_ch_"
                    f"{ch_num.lower()}_sec_{sec_clean}_sub_{sub_num}"
                )
                chunks.append(
                    StatutoryChunk(
                        chunk_id=chunk_id,
                        content=content,
                        metadata=StatutoryChunkMetadata(
                            statute=statute,
                            chapter=ch_num,
                            section=sec_num,
                            section_title=sec_title,
                            clause=clause_id,
                            act_year=act_year,
                            chunk_id=chunk_id,
                            breadcrumb=breadcrumb,
                            cross_references=self.extract_cross_references(content),
                            char_count=len(content),
                        ),
                    )
                )

    def run(self, documents: list[Document], **kwargs: Any) -> list[Document]:
        """Execute statutory chunking over a list of documents.

        Args:
            documents: Input documents conforming to Kotaemon Document contract.
            **kwargs: Additional pipeline keyword arguments.

        Returns:
            list[Document]: Output documents with breadcrumbs and legal metadata.
        """
        output_docs: list[Document] = []
        for doc in documents:
            text = doc.text or (str(doc.content) if doc.content else "")
            default_statute = doc.metadata.get("statute", "Consumer Protection Act, 2019")
            default_chapter = doc.metadata.get("chapter", "N/A")
            chunks = self.split_text(
                text=text,
                default_statute=default_statute,
                default_chapter=default_chapter,
            )
            for chunk in chunks:
                output_docs.append(chunk.to_document())
        return output_docs

    def __call__(self, documents: list[Document], **kwargs: Any) -> list[Document]:
        """Allow instance to be called directly like a function.

        Args:
            documents: Input documents conforming to Kotaemon Document contract.
            **kwargs: Additional pipeline keyword arguments.

        Returns:
            list[Document]: Output documents with breadcrumbs and legal metadata.
        """
        return self.run(documents, **kwargs)
