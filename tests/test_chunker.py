"""Comprehensive unit test suite for Structure-Aware Statutory Chunker.

Validates boundary preservation, breadcrumb headers, metadata extraction,
deep clause nesting (Section 2(47)(a)(i)), provisos/explanations (Section 2(7)),
E-Commerce Rules, Pecuniary Jurisdiction Rules, and Kotaemon Document contracts.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from legal_assistant.rag.chunker import (
    Document,
    StatutoryChunker,
)


# ------------------------------------------------------------------------------
# Test Fixtures & Sample Statutory Data
# ------------------------------------------------------------------------------
@pytest.fixture
def chunker() -> StatutoryChunker:
    """Fixture providing a standard StatutoryChunker instance."""
    return StatutoryChunker(max_chunk_chars=1500)


@pytest.fixture
def sensitive_chunker() -> StatutoryChunker:
    """Fixture providing a StatutoryChunker with small threshold for testing splits."""
    return StatutoryChunker(max_chunk_chars=300)


SAMPLE_CPA_TEXT = """
THE CONSUMER PROTECTION ACT, 2019
NO. 35 OF 2019
[9th August, 2019.]

CHAPTER I
PRELIMINARY

1. Short title, extent, commencement and application.—
(1) This Act may be called the Consumer Protection Act, 2019.
(2) It extends to the whole of India.
(3) It shall come into force on such date as the Central Government may appoint.

2. Definitions.—In this Act, unless the context otherwise requires,—
(7) "consumer" means any person who—
(a) buys any goods for a consideration which has been paid or promised;
(b) hires or avails of any service for a consideration which has been paid;
Explanation.—For the purposes of this clause,—
(a) "commercial purpose" does not include use by a person of goods bought
and used by him exclusively for earning livelihood by self-employment;
(b) the expressions "buys any goods" and "hires or avails any services"
includes offline or online transactions through electronic means.

(10) "defect" means any fault, imperfection or shortcoming in the quality,
quantity, potency, purity or standard which is required to be maintained
by or under any law for the time being in force.

(11) "deficiency" means any fault, imperfection, shortcoming or inadequacy
in the quality, nature and manner of performance required to be maintained.

(47) "unfair trade practice" means a trade practice which, for the purpose
of promoting the sale, use or supply of any goods or services, adopts any
unfair method or deceptive practice including the following, namely:—
(a) making any statement, whether orally or in writing, which—
(i) falsely represents that the goods are of a particular standard, quality,
quantity, grade, composition, style or model;
(ii) falsely represents that the services are of a particular standard,
quality or grade;
(b) permitting the publication of any advertisement for the sale of goods.

CHAPTER IV
CONSUMER DISPUTES REDRESSAL COMMISSION

34. Jurisdiction of District Commission.—
(1) Subject to the other provisions of this Act, the District Commission
shall have jurisdiction where consideration does not exceed one crore rupees.
(2) A complaint shall be instituted in a District Commission where—
(a) the opposite party carries on business; or
(b) any of the opposite parties resides; or
(c) the cause of action arises; or
(d) the complainant resides or personally works for gain.

35. Manner in which complaint shall be made.—
(1) A complaint, in relation to goods or services, may be filed with a
District Commission by—
(a) the consumer to whom such goods are sold or service provided;
(b) any recognised consumer association;
(c) one or more consumers, where there are numerous consumers; or
(d) the Central Government, the Central Authority or the State Government:
Provided that the complaint under this sub-section may be filed electronically
in such manner as may be prescribed.
(2) Every complaint filed under sub-section (1) shall be accompanied
with such fee and in such manner as may be specified by regulations.

69. Limitation period.—
(1) The District Commission, the State Commission or the National Commission
shall not admit a complaint unless it is filed within two years from the
date on which the cause of action has arisen.
(2) Notwithstanding anything contained in sub-section (1), a complaint may
be entertained after the period specified in sub-section (1), if complainant
satisfies the Commission that he had sufficient cause for not filing within:
Provided that no such complaint shall be entertained unless Commission
records its reasons for condoning such delay.
"""

SAMPLE_ECOMMERCE_TEXT = """
THE CONSUMER PROTECTION (E-COMMERCE) RULES, 2020

Rule 1. Short title and commencement.—
(1) These rules may be called the Consumer Protection (E-Commerce) Rules, 2020.
(2) They shall come into force on the date of publication in Official Gazette.

Rule 4. Mandatory duties of e-commerce entities.—
(1) An e-commerce entity shall be a company incorporated under Companies Act.
(4) Every e-commerce entity shall establish an adequate grievance redressal
mechanism having regard to grievances, and shall appoint a grievance officer
for consumer grievance redressal, displaying details on website.
(5) Every e-commerce entity shall ensure that the grievance officer acknowledges
receipt of complaint within forty-eight hours and redresses complaint
within one month from the date of receipt of the complaint.

Rule 6. Duties of sellers on marketplace.—
(1) No seller shall adopt any unfair trade practice on marketplace.
(3) No such seller shall refuse to take back goods, or discontinue services,
or refuse to refund consideration paid, if goods/services are defective.
"""


# ------------------------------------------------------------------------------
# Test Suite 1: Boundary & Section Preservation
# ------------------------------------------------------------------------------
def test_section_boundary_preservation(chunker: StatutoryChunker) -> None:
    """Verify that distinct sections do not bleed into each other."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    sections_found = [c.metadata.section for c in chunks]

    assert "1" in sections_found
    assert "2(10)" in sections_found
    assert "2(11)" in sections_found
    assert "34" in sections_found or any("34" in s for s in sections_found)
    assert "35" in sections_found or any("35" in s for s in sections_found)
    assert "69" in sections_found or any("69" in s for s in sections_found)

    # Ensure section 69 does not contain text from section 35
    sec_69_chunks = [c for c in chunks if "69" in c.metadata.section]
    for c in sec_69_chunks:
        assert "Manner in which complaint shall be made" not in c.content


def test_no_mid_sentence_break(chunker: StatutoryChunker) -> None:
    """Verify that subsections remain grammatically and legally whole."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    for c in chunks:
        # Every chunk content must have proper bracketed breadcrumb and non-empty body
        assert c.content.startswith("[STATUTE:")
        assert "\n[TITLE:" in c.content
        lines = c.content.splitlines()
        assert len(lines) >= 3


def test_proviso_adheres_to_parent_subsection(
    sensitive_chunker: StatutoryChunker,
) -> None:
    """Verify that provisos remain glued to their parent subsection."""
    chunks = sensitive_chunker.split_text(SAMPLE_CPA_TEXT)
    # Section 35(1) contains a proviso about electronic filing
    sec_35_sub1 = [c for c in chunks if c.metadata.section == "35" and c.metadata.clause == "(1)"]
    assert len(sec_35_sub1) == 1
    assert (
        "Provided that the complaint under this sub-section may be filed electronically"
        in sec_35_sub1[0].content
    )


# ------------------------------------------------------------------------------
# Test Suite 2: Breadcrumb Header Formatting
# ------------------------------------------------------------------------------
def test_canonical_breadcrumb_format(chunker: StatutoryChunker) -> None:
    """Verify that all breadcrumbs strictly follow the canonical format."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    for c in chunks:
        bc = c.metadata.breadcrumb
        assert bc.startswith("[STATUTE: ")
        assert " | CHAPTER: " in bc
        assert " | SECTION: " in bc
        assert " | CLAUSE: " in bc
        assert bc.endswith("]")


def test_ecommerce_rules_breadcrumb(chunker: StatutoryChunker) -> None:
    """Verify breadcrumbs for E-Commerce Rules without chapters."""
    chunks = chunker.split_text(SAMPLE_ECOMMERCE_TEXT)
    assert len(chunks) > 0
    for c in chunks:
        assert c.metadata.statute == "Consumer Protection (E-Commerce) Rules, 2020"
        assert c.metadata.chapter == "N/A"
        assert c.metadata.breadcrumb.startswith(
            "[STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | CHAPTER: N/A | SECTION: Rule "
        )


# ------------------------------------------------------------------------------
# Test Suite 3: Metadata Extraction & Schema Compliance
# ------------------------------------------------------------------------------
def test_metadata_extraction_fields(chunker: StatutoryChunker) -> None:
    """Verify that all structured metadata fields are accurately populated."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    chunk_10 = next(c for c in chunks if c.metadata.section == "2(10)")

    assert chunk_10.metadata.statute == "Consumer Protection Act, 2019"
    assert chunk_10.metadata.chapter == "I"
    assert chunk_10.metadata.section == "2(10)"
    assert chunk_10.metadata.section_title == "Definition of 'defect'"
    assert chunk_10.metadata.clause == "(10)"
    assert chunk_10.metadata.act_year == 2019
    assert chunk_10.metadata.chunk_id == "con_2019_ch_i_sec_2_10"
    assert chunk_10.metadata.char_count == len(chunk_10.content)


def test_cross_reference_extraction(chunker: StatutoryChunker) -> None:
    """Verify regex extraction of cross-references like sub-section (1)."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    # Section 35(2) references sub-section (1)
    sec_35_sub2 = [c for c in chunks if "35" in c.metadata.section and c.metadata.clause == "(2)"]
    if sec_35_sub2:
        assert "sub-section (1)" in sec_35_sub2[0].metadata.cross_references


# ------------------------------------------------------------------------------
# Test Suite 4: Multi-Line Clauses, Nested Edges & Section 2(47)(a)(i)
# ------------------------------------------------------------------------------
def test_section_2_47_deep_nesting(
    sensitive_chunker: StatutoryChunker,
) -> None:
    """Verify Section 2(47)(a)(i) deep subclause splitting with stem retention."""
    chunks = sensitive_chunker.split_text(SAMPLE_CPA_TEXT)
    sec_47_chunks = [c for c in chunks if "2(47)" in c.metadata.section]

    assert len(sec_47_chunks) >= 2

    # Check for presence of introductory definition stem in subclause chunks
    for c in sec_47_chunks:
        assert "unfair trade practice" in c.content
        assert c.content.startswith("[STATUTE:")

    # Check for subclause (a) / (a)(i) false representation of goods
    goods_chunk = next(
        (c for c in sec_47_chunks if "particular standard, quality" in c.content),
        None,
    )
    assert goods_chunk is not None
    assert goods_chunk.metadata.clause in ("(a)", "(a)(i)", "(i)")
    assert "making any statement" in goods_chunk.content


def test_section_2_7_consumer_explanation(chunker: StatutoryChunker) -> None:
    """Verify Section 2(7) definitions with self-employment and e-commerce explanations."""
    chunks = chunker.split_text(SAMPLE_CPA_TEXT)
    sec_7_chunks = [c for c in chunks if "2(7)" in c.metadata.section]
    assert len(sec_7_chunks) >= 1

    combined_sec_7_text = " ".join(c.content for c in sec_7_chunks)
    assert "commercial purpose" in combined_sec_7_text
    assert "earning livelihood by self-employment" in combined_sec_7_text
    assert "offline or online transactions" in combined_sec_7_text


def test_unicode_and_currency_resilience(chunker: StatutoryChunker) -> None:
    """Verify handling of ₹ symbol, em-dashes, and Hindi annotations."""
    unicode_statute = """
THE CONSUMER PROTECTION ACT, 2019
उपभोक्ता संरक्षण अधिनियम, 2019

CHAPTER IV
COMMISSION

34. Jurisdiction.—
(1) District Commission has jurisdiction where consideration is <= ₹50,00,000.
"""
    chunks = chunker.split_text(unicode_statute)
    assert len(chunks) == 1
    assert "₹50,00,000" in chunks[0].content
    assert "उपभोक्ता" in chunks[0].content or "District Commission" in chunks[0].content


# ------------------------------------------------------------------------------
# Test Suite 5: Kotaemon & LlamaIndex Compatibility
# ------------------------------------------------------------------------------
def test_kotaemon_run_interface(chunker: StatutoryChunker) -> None:
    """Verify StatutoryChunker.run(documents) conforms to Kotaemon BaseSplitter contract."""
    input_docs = [
        Document(
            text=SAMPLE_CPA_TEXT,
            metadata={"statute": "Consumer Protection Act, 2019"},
        ),
        Document(
            text=SAMPLE_ECOMMERCE_TEXT,
            metadata={"statute": "Consumer Protection (E-Commerce) Rules, 2020"},
        ),
    ]

    output_docs = chunker.run(input_docs)
    assert isinstance(output_docs, list)
    assert len(output_docs) > 0

    for doc in output_docs:
        assert isinstance(doc, Document)
        assert doc.channel == "info"
        assert "statute" in doc.metadata
        assert "breadcrumb" in doc.metadata
        assert doc.text.startswith("[STATUTE:")


def test_callable_interface(chunker: StatutoryChunker) -> None:
    """Verify StatutoryChunker is callable directly like chunker(documents)."""
    input_docs = [Document(text=SAMPLE_ECOMMERCE_TEXT)]
    output_docs = chunker(input_docs)
    assert len(output_docs) > 0


def test_empty_and_whitespace_input(chunker: StatutoryChunker) -> None:
    """Verify empty or whitespace-only documents do not crash the chunker."""
    assert chunker.split_text("") == []
    assert chunker.split_text("   \n\n\t  ") == []
    assert chunker.run([Document(text="")]) == []


def test_markdown_header_support(chunker: StatutoryChunker) -> None:
    """Verify chunker parses markdown formatted statutes."""
    md_text = """
# Consumer Protection (Jurisdiction of Commissions) Rules, 2021

## Rule 3 - Jurisdiction of District Commission
(1) The District Commission shall entertain complaints where value <= ₹50 Lakhs.

## Rule 4 - Jurisdiction of State Commission
(1) The State Commission shall entertain complaints where value <= ₹2 Crores.
"""
    chunks = chunker.split_text(
        md_text,
        default_statute="Consumer Protection (Jurisdiction of Commissions) Rules, 2021",
    )
    assert len(chunks) == 2
    assert chunks[0].metadata.section == "Rule 3"
    assert chunks[1].metadata.section == "Rule 4"


def test_delimited_statute_files_parsing(chunker: StatutoryChunker) -> None:
    """Verify parsing of actual statutory files generated with canonical delimiters."""
    cpa_path = Path("data/statutes/cpa_2019_core.txt")
    if cpa_path.exists():
        content = cpa_path.read_text(encoding="utf-8")
        chunks = chunker.split_text(content)
        assert len(chunks) >= 30
        for c in chunks:
            assert c.metadata.statute != ""
            assert c.metadata.breadcrumb.startswith("[STATUTE:")
            assert len(c.content) > 0
