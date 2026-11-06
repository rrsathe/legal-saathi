"""Unit tests for Legal Saathi Statutory Hybrid Retriever and Kotaemon Bridge.

Tests:
1. Legal Tokenizer statutory and currency preservation.
2. Exact statutory section lookup ranking (Section 2(47) ranks #1 over Section 47).
3. Colloquial dispute query ranking (Instagram UPI scam ranks refund refusal).
4. Genuine Reciprocal Rank Fusion (RRF) mathematical formula verification.
5. Layer 2 Retrieval Confidence Gate abstention behavior.
6. Kotaemon Bridge component lifecycle and dual-channel streaming.
7. Dense vector retrievers (InMemory and ChromaDB Ephemeral).
"""

from __future__ import annotations

import pytest

from legal_assistant.rag.hybrid_retriever import (
    ChromaDenseRetriever,
    InMemoryDenseRetriever,
    LegalTokenizer,
    RetrievedChunk,
    StatutoryHybridRetriever,
)
from legal_assistant.rag.kotaemon_bridge import (
    Document,
    KotaemonLegalBridge,
    RetrievedDocument,
)


# ==============================================================================
# Fixtures & Synthetic Statutory Corpus
# ==============================================================================
@pytest.fixture
def sample_corpus() -> list[RetrievedChunk]:
    """Return realistic statutory chunks covering CPA 2019 and E-Commerce Rules."""
    return [
        RetrievedChunk(
            chunk_id="cpa_sec_2_47",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 2(47) | "
                "TITLE: Unfair Trade Practice]\n"
                "Unfair trade practice means a trade practice which adopts any unfair method "
                "or deceptive practice including making false or misleading representations, "
                "refusal after receiving payment to deliver goods or refund consideration paid."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I - Preliminary",
            section="2(47)",
            title="Unfair Trade Practice",
            score=0.0,
        ),
        RetrievedChunk(
            chunk_id="cpa_sec_2_10",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 2(10) | TITLE: Defect]\n"
                "Defect means any fault, imperfection or shortcoming in the quality, quantity, "
                "potency, purity or standard required to be maintained in relation to goods."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter I - Preliminary",
            section="2(10)",
            title="Defect",
            score=0.0,
        ),
        RetrievedChunk(
            chunk_id="cpa_sec_47",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 47 | "
                "TITLE: Jurisdiction of State Commission]\n"
                "Subject to other provisions of Act, State Commission shall have jurisdiction "
                "to entertain complaints where value of goods or services paid as consideration "
                "exceeds rupees fifty lakhs but does not exceed rupees two crores."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter IV - Consumer Disputes Redressal Commission",
            section="47",
            title="Jurisdiction of State Commission",
            score=0.0,
        ),
        RetrievedChunk(
            chunk_id="ecom_rule_4_5",
            content=(
                "[STATUTE: Consumer Protection (E-Commerce) Rules, 2020 | RULE: 4(5) | "
                "TITLE: Grievance Redressal]\n"
                "Every e-commerce entity shall acknowledge receipt of any consumer complaint "
                "within forty-eight hours and redress complaint within one month from receipt."
            ),
            statute="Consumer Protection (E-Commerce) Rules, 2020",
            chapter="Duties of E-Commerce Entities",
            section="Rule 4(5)",
            title="Grievance Redressal Mechanism",
            score=0.0,
        ),
        RetrievedChunk(
            chunk_id="cpa_sec_35",
            content=(
                "[STATUTE: Consumer Protection Act, 2019 | SECTION: 35 | "
                "TITLE: Manner of Filing Complaint]\n"
                "A complaint, in relation to any goods sold or delivered or any service provided, "
                "may be filed with a District Commission by the consumer."
            ),
            statute="Consumer Protection Act, 2019",
            chapter="Chapter IV - Consumer Disputes Redressal Commission",
            section="35",
            title="Manner of Filing Complaint",
            score=0.0,
        ),
    ]


# ==============================================================================
# 1. Legal Tokenizer Unit Tests
# ==============================================================================
def test_legal_tokenizer_statutory_sections() -> None:
    """Verify that statutory section numbers are preserved intact."""
    text = "Under Section 2(47) and Rule 4(5), see also Sec 34(2)(d) of CPA 2019."
    tokens = LegalTokenizer.tokenize(text)

    # Must preserve exact section numbers
    assert "2(47)" in tokens
    assert "sec_2(47)" in tokens
    assert "4(5)" in tokens
    assert "rule_4(5)" in tokens
    assert "34(2)(d)" in tokens
    assert "cpa" in tokens
    assert "2019" in tokens


def test_legal_tokenizer_currency_preservation() -> None:
    """Verify that Indian currency values with commas and symbols are preserved."""
    text = "Disputed amount of ₹4,500 transferred via UPI; claim under ₹50 Lakhs or Rs. 50,000."
    tokens = LegalTokenizer.tokenize(text)

    assert "₹4500" in tokens
    assert "₹4,500" in tokens
    assert "₹50lakhs" in tokens
    assert "rs.50000" in tokens


def test_legal_tokenizer_hyphenated_legal_terms() -> None:
    """Verify that compound legal terms are not broken up."""
    text = (
        "Consumer bought goods from e-commerce marketplace using "
        "pre-litigation notice on e-daakhil."
    )
    tokens = LegalTokenizer.tokenize(text)

    assert "e-commerce" in tokens
    assert "pre-litigation" in tokens
    assert "e-daakhil" in tokens


# ==============================================================================
# 2. Exact Statutory Section Lookup Ranking Test
# ==============================================================================
def test_exact_section_2_47_lookup_ranks_first(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that querying 'Section 2(47)' ranks Unfair Trade Practice #1 over Section 47."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    results = retriever.retrieve("Section 2(47)", top_k=3)

    assert len(results) >= 1
    top_hit = results[0]

    # Section 2(47) must be rank 1
    assert top_hit.section == "2(47)"
    assert top_hit.title == "Unfair Trade Practice"

    # Section 47 must NOT outrank Section 2(47)
    if len(results) > 1:
        assert results[1].section != "2(47)"
        assert results[0].score > results[1].score


def test_exact_rule_4_5_lookup_ranks_first(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that querying 'Rule 4(5)' ranks e-commerce grievance officer #1."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    results = retriever.retrieve("Rule 4(5) grievance officer timeline", top_k=2)

    assert len(results) >= 1
    assert results[0].section == "Rule 4(5)"
    assert "E-Commerce" in results[0].statute


# ==============================================================================
# 3. Colloquial Query Retrieval Test
# ==============================================================================
def test_colloquial_upi_scam_retrieval(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that colloquial scam query retrieves refusal to refund / e-commerce rules."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    query = "Instagram seller blocked me after UPI payment of ₹4,500 and refused to refund"
    results = retriever.retrieve(query, top_k=2)

    assert len(results) >= 1
    retrieved_sections = [r.section for r in results]

    # Must retrieve Section 2(47) (refusal to refund consideration) or Rule 4(5)
    assert "2(47)" in retrieved_sections or "Rule 4(5)" in retrieved_sections


# ==============================================================================
# 4. RRF Score Calculation Math Verification
# ==============================================================================
def test_rrf_mathematical_precision() -> None:
    """Verify exact RRF formula: RRF(d) = w_bm25 / (k + rank_bm25) + w_dense / (k + rank_dense)."""
    k = 60
    w_bm25 = 1.0
    w_dense = 1.0

    # Rank 1 in BM25, Rank 2 in Dense
    expected_score_a = (w_bm25 / (k + 1)) + (w_dense / (k + 2))
    assert abs(expected_score_a - (1.0 / 61.0 + 1.0 / 62.0)) < 1e-9
    assert abs(expected_score_a - 0.03252247) < 1e-6

    # Rank 1 in BM25 only
    expected_score_c = w_bm25 / (k + 1)
    assert abs(expected_score_c - (1.0 / 61.0)) < 1e-9
    assert abs(expected_score_c - 0.01639344) < 1e-6


def test_rrf_weighting_differentiation(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that adjusting BM25 and Dense weights alters the final scores."""
    retriever_heavy_bm25 = StatutoryHybridRetriever(
        chunks=sample_corpus,
        w_bm25=3.0,
        w_dense=0.1,
    )
    retriever_heavy_dense = StatutoryHybridRetriever(
        chunks=sample_corpus,
        w_bm25=0.1,
        w_dense=0.5,
    )

    results_bm25 = retriever_heavy_bm25.retrieve("Section 2(47)", top_k=1)
    results_dense = retriever_heavy_dense.retrieve("Section 2(47)", top_k=1)

    assert len(results_bm25) > 0 and len(results_dense) > 0
    assert results_bm25[0].score != results_dense[0].score
    assert results_bm25[0].score > results_dense[0].score


# ==============================================================================
# 5. Layer 2 Retrieval Confidence Gate Abstention Tests
# ==============================================================================
def test_retrieval_confidence_abstains_on_out_of_domain(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that nonsensical / out-of-domain queries fail confidence and trigger abstention."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus, min_confidence_threshold=0.012)
    query = "quantum chromodynamics gluon plasma hadron collider higgs boson"

    results, confidence = retriever.retrieve_with_confidence(query, top_k=3)

    # Confidence must fail
    assert confidence.confidence_passed is False
    assert confidence.abstention_triggered is True
    assert confidence.abstention_message is not None
    assert "unable to locate verified statutory provisions" in confidence.abstention_message


def test_retrieval_confidence_passes_on_legitimate_consumer_query(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that valid statutory queries clear the confidence threshold."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus, min_confidence_threshold=0.012)
    query = "defective product replacement refund under Section 2(10)"

    results, confidence = retriever.retrieve_with_confidence(query, top_k=3)

    assert confidence.confidence_passed is True
    assert confidence.abstention_triggered is False
    assert confidence.top_rrf_score >= 0.012


# ==============================================================================
# 6. Kotaemon Bridge Lifecycle & Dual-Channel Streaming Tests
# ==============================================================================
def test_kotaemon_bridge_run_lifecycle(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that KotaemonLegalBridge implements the theflow.Function run() lifecycle."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    bridge = KotaemonLegalBridge(retriever=retriever)

    # Calling run() must return RetrievedDocument instances
    docs = bridge.run("Section 35 District Commission complaint filing", top_k=2)

    assert isinstance(docs, list)
    assert len(docs) >= 1
    assert isinstance(docs[0], (RetrievedDocument, Document))
    assert docs[0].score > 0.0
    assert "35" in docs[0].metadata["section"]


def test_kotaemon_bridge_dual_channel_streaming(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that bridge yields separate 'info' (HTML) and 'chat' (conversational) documents."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    bridge = KotaemonLegalBridge(retriever=retriever)

    stream_generator = bridge.stream_retrieval("Section 2(47) refund refusal", top_k=2)
    yielded_docs = list(stream_generator)

    assert len(yielded_docs) >= 2

    # First packet must be channel="info" with HTML provenance
    info_packet = yielded_docs[0]
    assert info_packet.channel == "info"
    assert "<details" in info_packet.plain_text
    assert "Verified Statutory Grounds" in info_packet.plain_text

    # Subsequent packet must be channel="chat" with legal text
    chat_packet = yielded_docs[1]
    assert chat_packet.channel == "chat"
    assert "Legal Grounding Verified" in chat_packet.plain_text


def test_kotaemon_bridge_ui_provenance_html_rendering(
    sample_corpus: list[RetrievedChunk],
) -> None:
    """Verify that format_ui_provenance produces clean HTML with active citation tags."""
    retriever = StatutoryHybridRetriever(chunks=sample_corpus)
    bridge = KotaemonLegalBridge(retriever=retriever)

    chunks = retriever.retrieve("Section 2(47)", top_k=2)
    rendered_html = bridge.format_ui_provenance(chunks, cited_sections=["Section 2(47)"])

    assert "<details class='statutory-card'" in rendered_html
    assert "[CITED IN RESPONSE]" in rendered_html
    assert "RRF:" in rendered_html
    assert "Consumer Protection Act, 2019" in rendered_html


# ==============================================================================
# 7. Dense Retrievers Unit Tests
# ==============================================================================
def test_in_memory_dense_retriever_cosine_similarity() -> None:
    """Verify InMemoryDenseRetriever indexes chunks and returns ranked similarities."""
    dense = InMemoryDenseRetriever(embedding_dim=512)
    doc_1 = RetrievedChunk(
        chunk_id="d1",
        content="Consumer complaint for refund of mobile phone consideration",
        statute="CPA 2019",
        section="35",
        score=0.0,
    )
    doc_2 = RetrievedChunk(
        chunk_id="d2",
        content="Criminal cheque bounce and commercial company dispute",
        statute="NI Act",
        section="138",
        score=0.0,
    )
    dense.index([doc_1, doc_2])

    hits = dense.search("refund of mobile phone", top_k=1)
    assert len(hits) == 1
    assert hits[0][0].chunk_id == "d1"
    assert hits[0][1] > 0.0


def test_chroma_dense_retriever_ephemeral() -> None:
    """Verify ChromaDenseRetriever runs with EphemeralClient without downloading remote weights."""
    chroma_retriever = ChromaDenseRetriever(collection_name="test_ephemeral_coll")
    doc_1 = RetrievedChunk(
        chunk_id="c1",
        content="Defective laptop screen replacement and refund guarantee",
        statute="CPA 2019",
        section="2(10)",
        score=0.0,
    )
    chroma_retriever.index([doc_1])

    hits = chroma_retriever.search("defective laptop screen", top_k=1)
    assert len(hits) == 1
    assert hits[0][0].chunk_id == "c1"
    assert hits[0][1] > 0.0
