"""Empirical Stress Test for render_editorial_table in src/legal_assistant/ui/app.py.

Conducted by teamwork_challenger (Challenger 2).
"""

from __future__ import annotations

import sys
import time

from markdown_it import MarkdownIt

from legal_assistant.ui.app import render_editorial_table

md_commonmark = MarkdownIt("commonmark")
md_default = MarkdownIt()


def check_no_pre_code(html_str: str, label: str) -> None:
    """Ensure CommonMark rendering does not create pre/code blocks."""
    for parser_name, parser in [("commonmark", md_commonmark), ("default", md_default)]:
        rendered = parser.render(html_str)
        assert "<pre><code>" not in rendered, (
            f"FAIL [{label} with {parser_name}]: Rendered markdown contains <pre><code> block!\n"
            f"Snippet: {rendered[:300]}"
        )
        assert "<pre>" not in rendered, (
            f"FAIL [{label} with {parser_name}]: Rendered markdown contains <pre> block!\n"
            f"Snippet: {rendered[:300]}"
        )


def test_empty_headers_empty_rows() -> None:
    print("--- 1. Testing Empty Headers and Empty Rows ---")
    out = render_editorial_table([], [])
    assert "<table" not in out, "Empty table should not render <table> tag"
    assert "No records available." in out, "Should display fallback message"
    assert "#706D66" in out, "Should use Harvey muted text color token #706D66"
    check_no_pre_code(out, "Empty headers empty rows")
    print("  PASS: Empty headers & empty rows handled cleanly.")


def test_nonempty_headers_empty_rows() -> None:
    print("--- 2. Testing Non-Empty Headers and Empty Rows ---")
    out = render_editorial_table(["Col A", "Col B", "Col C"], [])
    assert "<table" not in out
    assert "No records available." in out
    check_no_pre_code(out, "Non-empty headers empty rows")
    print("  PASS: Non-empty headers with empty rows handled cleanly.")


def test_empty_headers_nonempty_rows() -> None:
    print("--- 3. Testing Empty Headers and Non-Empty Rows ---")
    rows = [["Val 1A", "Val 1B"], ["Val 2A", "Val 2B"]]
    out = render_editorial_table([], rows)
    assert "<table style=" in out
    assert "<thead><tr></tr></thead>" in out
    assert "Val 1A" in out
    assert "Val 2B" in out
    check_no_pre_code(out, "Empty headers non-empty rows")
    print("  PASS: Empty headers with non-empty rows rendered valid HTML table.")


def test_heterogeneous_datatypes() -> None:
    print("--- 4. Testing Heterogeneous Datatypes (None, int, float, bool, multiline, empty) ---")
    headers = [
        "Header None",
        "Header Int",
        "Header Float",
        "Header Bool True",
        "Header Bool False",
        "Header Multiline",
        "Header Empty",
    ]
    rows = [
        [
            None,
            42,
            3.14159265,
            True,
            False,
            "Line 1: Statutory Claim\nLine 2: Limitation Period\nLine 3: Prayer for Relief",
            "",
        ],
        [
            None,
            -999,
            0.0,
            False,
            True,
            "Single line after multiline",
            "Non-empty text",
        ],
    ]
    # Intentionally testing runtime robustness with heterogeneous datatypes.
    out = render_editorial_table(headers, rows)  # type: ignore[arg-type]

    assert "<table" in out
    # Cell string conversions
    assert ">None<" in out
    assert ">42<" in out
    assert ">-999<" in out
    assert ">3.14159265<" in out
    assert ">0.0<" in out
    assert ">True<" in out
    assert ">False<" in out
    assert "Line 1: Statutory Claim\nLine 2: Limitation Period\nLine 3: Prayer for Relief" in out
    assert "><" in out  # empty string cell

    # Structural styling checks
    assert "word-break: break-word" in out
    assert "white-space: normal" in out
    assert "border-top: 2px solid #0F0E0D" in out
    assert "border-bottom: 1px solid #CCCAC6" in out

    check_no_pre_code(out, "Heterogeneous datatypes")
    print("  PASS: None, int, float, bool, multiline strings, empty cells converted safely.")


def test_xss_injection_and_html_escaping() -> None:
    print("--- 5. Testing Adversarial XSS Injection Strings & Character Escaping ---")
    xss_headers = [
        "<script>alert('XSS-H1')</script>",
        "<img src=x onerror=alert('XSS-H2')>",
        "&amp; < > \" ' Header",
    ]
    xss_rows = [
        [
            "<img src=x onerror=alert(1)>",
            "<script>alert('pwned')</script>",
            "&amp; &lt; &gt; &quot; &#39;",
        ],
        [
            "<svg/onload=alert('svg')>",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<body onload=alert('body')>",
        ],
        [
            "<style>body{display:none}</style>",
            "<a href='javascript:void(0)'>malicious link</a>",
            "\"double quoted\" and 'single quoted' and `backticks`",
        ],
    ]

    out = render_editorial_table(xss_headers, xss_rows)

    # 1. Zero raw dangerous tags
    raw_unauthorized_tags = [
        "<script>",
        "</script>",
        "<img src=x",
        "<svg",
        "<iframe",
        "<body",
        "<style>",
        "</style>",
        "<a href=",
    ]
    for tag in raw_unauthorized_tags:
        assert tag not in out, (
            f"CRITICAL SECURITY FAIL: Found unescaped tag {tag!r} in rendered HTML!"
        )

    # 2. Confirm html.escape was applied to headers
    assert (
        "&lt;script&gt;alert(&#x27;XSS-H1&#x27;)&lt;/script&gt;" in out
        or "&lt;script&gt;alert('XSS-H1')&lt;/script&gt;" in out
    )
    assert (
        "&lt;img src=x onerror=alert(&#x27;XSS-H2&#x27;)&gt;" in out
        or "&lt;img src=x onerror=alert('XSS-H2')&gt;" in out
    )

    # 3. Confirm html.escape was applied to cell values
    assert "&lt;img src=x onerror=alert(1)&gt;" in out
    assert (
        "&lt;script&gt;alert(&#x27;pwned&#x27;)&lt;/script&gt;" in out
        or "&lt;script&gt;alert('pwned')&lt;/script&gt;" in out
    )
    assert (
        "&lt;svg/onload=alert(&#x27;svg&#x27;)&gt;" in out
        or "&lt;svg/onload=alert('svg')&gt;" in out
    )
    assert (
        "&lt;iframe src=&#x27;javascript:alert(1)&#x27;&gt;&lt;/iframe&gt;" in out
        or "&lt;iframe src='javascript:alert(1)'&gt;&lt;/iframe&gt;" in out
    )
    assert "&amp;amp;" in out

    # 4. Confirm table remains syntactically valid
    assert out.startswith("<div style='width: 100%; overflow-x: auto; margin-bottom: 24px;'>")
    assert (
        "<table style='width: 100%; border-collapse: collapse; "
        "border-top: 2px solid #0F0E0D; border-bottom: 1px solid #CCCAC6;'>" in out
    )
    assert "<thead><tr>" in out
    assert "</tr></thead>" in out
    assert "<tbody>" in out
    assert "</tbody>" in out
    assert "</table>" in out
    assert out.endswith("</div>")

    # 5. Confirm no pre/code blocks generated under markdown parsers
    check_no_pre_code(out, "XSS injection table")
    print("  PASS: All XSS vectors sanitized with html.escape and valid HTML table rendered.")


def test_asymmetric_ragged_rows() -> None:
    print("--- 6. Testing Asymmetric / Ragged Rows ---")
    headers = ["Col 1", "Col 2", "Col 3"]
    ragged_rows = [
        ["Single Item"],
        ["Item 1", "Item 2", "Item 3", "Extra Item 4", "Extra Item 5"],
        [],
    ]
    out = render_editorial_table(headers, ragged_rows)
    assert "<table" in out
    assert ">Single Item<" in out
    assert ">Extra Item 5<" in out
    assert "<tr></tr>" in out  # empty row produces empty tr
    check_no_pre_code(out, "Ragged rows")
    print("  PASS: Asymmetric ragged rows rendered without IndexError or crash.")


def test_large_volume_performance() -> None:
    print("--- 7. Testing High Volume Performance Stress (2,000 rows x 8 columns) ---")
    headers = [f"Statutory Provision {i}" for i in range(8)]
    rows = [
        [
            f"CPA 2019 Sec {r} Sub-clause {c}: Consumer Grievance Remediation Record"
            for c in range(8)
        ]
        for r in range(2000)
    ]
    t0 = time.perf_counter()
    out = render_editorial_table(headers, rows)
    elapsed = time.perf_counter() - t0

    assert len(out) > 1_000_000, f"Expected >1MB output, got {len(out)} bytes"
    assert elapsed < 1.0, f"Rendering 2,000 rows took too long: {elapsed:.3f}s"
    print(f"  PASS: 2,000 rows x 8 cols ({len(out):,} bytes) rendered in {elapsed * 1000:.1f}ms.")


if __name__ == "__main__":
    print("=====================================================================")
    print("Starting Empirical Stress Tests for render_editorial_table")
    print("=====================================================================")
    try:
        test_empty_headers_empty_rows()
        test_nonempty_headers_empty_rows()
        test_empty_headers_nonempty_rows()
        test_heterogeneous_datatypes()
        test_xss_injection_and_html_escaping()
        test_asymmetric_ragged_rows()
        test_large_volume_performance()
        print("=====================================================================")
        print("ALL 7 EMPIRICAL EDITORIAL TABLE STRESS TESTS PASSED SUCCESSFULLY!")
        print("=====================================================================")
    except Exception as e:
        print(f"FAILED with exception: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
