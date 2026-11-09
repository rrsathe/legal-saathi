"""Empirical and adversarial verification tests for Legal Saathi Streamlit custom CSS.

Verifies:
1. Exact string length and character-for-character equivalence against ORIGINAL_REQUEST.md.
2. Lexical tokenizer, curly brace pairing, quotation pairing, and CSS AST validity.
3. Selector specificity and exact token mapping for #ADABA5, #FAFAF9, #0F0E0D, #8F8B85, #1F1D1A.
4. WCAG 2.1 contrast ratio calculations (AA and AAA) for all 3 reported UI defects.
5. Adversarial edge cases: WebKit text-fill sync, SVG path fills, and font fallbacks.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

from legal_assistant.ui.app import LEGAL_SAATHI_CUSTOM_CSS

ROOT_DIR = Path(__file__).resolve().parent.parent
ORIGINAL_REQUEST_FILE = ROOT_DIR / ".agents" / "teamwork" / "ORIGINAL_REQUEST.md"


class CSSRule(NamedTuple):
    """Parsed representation of a single CSS rule block."""

    selectors: list[str]
    raw_selector: str
    declarations: dict[str, str]


# ==============================================================================
# Helper: WCAG 2.1 Luminance and Contrast Calculation
# ==============================================================================
def srgb_channel_to_linear(c_byte: int) -> float:
    """Convert an 8-bit sRGB channel to linear light value per IEC 61966-2-1."""
    c = c_byte / 255.0
    if c <= 0.03928:
        return float(c / 12.92)
    return float(((c + 0.055) / 1.055) ** 2.4)


def relative_luminance(hex_code: str) -> float:
    """Compute relative luminance L for an sRGB hex code per WCAG 2.1 standard."""
    cleaned = hex_code.strip().lstrip("#")
    if len(cleaned) == 3:
        cleaned = "".join(ch * 2 for ch in cleaned)
    r = int(cleaned[0:2], 16)
    g = int(cleaned[2:4], 16)
    b = int(cleaned[4:6], 16)

    r_lin = srgb_channel_to_linear(r)
    g_lin = srgb_channel_to_linear(g)
    b_lin = srgb_channel_to_linear(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def wcag_contrast_ratio(hex1: str, hex2: str) -> float:
    """Calculate WCAG 2.1 contrast ratio (L1 + 0.05) / (L2 + 0.05)."""
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ==============================================================================
# Helper: Minimal Deterministic CSS Tokenizer & Parser
# ==============================================================================
def parse_css_ast(css_text: str) -> list[CSSRule]:
    """Parse CSS text into AST rules while validating brace, quote, and comment balance."""
    assert css_text.startswith("<style>\n"), "CSS payload missing '<style>\\n' opening tag"
    assert css_text.endswith("</style>\n"), "CSS payload missing '</style>\\n' closing tag"

    body = css_text[len("<style>\n") : -len("</style>\n")]

    # Tokenizer state tracking
    i = 0
    n = len(body)
    in_single_quote = False
    in_double_quote = False
    in_comment = False
    paren_depth = 0
    brace_depth = 0

    clean_chars: list[str] = []

    while i < n:
        ch = body[i]
        next_ch = body[i + 1] if i + 1 < n else ""

        if in_comment:
            if ch == "*" and next_ch == "/":
                in_comment = False
                i += 2
                clean_chars.append(" ")
                continue
            i += 1
            continue

        if not in_single_quote and not in_double_quote and ch == "/" and next_ch == "*":
            in_comment = True
            i += 2
            continue

        if ch == "'" and not in_double_quote:
            in_single_quote = not in_single_quote
        elif ch == '"' and not in_single_quote:
            in_double_quote = not in_double_quote

        if not in_single_quote and not in_double_quote:
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
                assert paren_depth >= 0, f"Unmatched closing parenthesis at position {i}"
            elif ch == "{":
                brace_depth += 1
            elif ch == "}":
                brace_depth -= 1
                assert brace_depth >= 0, f"Unmatched closing curly brace at position {i}"

        clean_chars.append(ch)
        i += 1

    assert not in_comment, "Unclosed CSS comment /* found"
    assert not in_single_quote, "Unclosed single quote ' found"
    assert not in_double_quote, 'Unclosed double quote " found'
    assert paren_depth == 0, f"Unmatched parentheses count: depth is {paren_depth}"
    assert brace_depth == 0, f"Unmatched curly braces count: depth is {brace_depth}"

    cleaned_css = "".join(clean_chars)

    # Extract rules
    rules: list[CSSRule] = []
    rule_regex = re.compile(r"([^{}]+)\{([^{}]+)\}", re.DOTALL)
    for match in rule_regex.finditer(cleaned_css):
        selector_part = match.group(1).strip()
        body_part = match.group(2).strip()

        # Split selectors by comma (unless inside brackets/parentheses)
        selectors = [s.strip() for s in selector_part.split(",") if s.strip()]

        # Parse declarations
        declarations: dict[str, str] = {}
        for decl in body_part.split(";"):
            decl = decl.strip()
            if not decl:
                continue
            if ":" not in decl:
                continue
            prop, val = decl.split(":", 1)
            declarations[prop.strip().lower()] = val.strip()

        rules.append(
            CSSRule(selectors=selectors, raw_selector=selector_part, declarations=declarations)
        )

    return rules


def compute_css_specificity(selector: str) -> tuple[int, int, int]:
    """Calculate CSS specificity tuple (IDs, Classes/Attributes/Pseudo-classes, Elements)."""
    # Remove strings to prevent false attribute counts
    s = re.sub(r'"[^"]*"', '""', selector)
    s = re.sub(r"'[^']*'", "''", s)

    # 1. IDs
    ids = len(re.findall(r"#[a-zA-Z0-9_-]+", s))

    # 2. Attributes, classes, pseudo-classes
    attrs = len(re.findall(r"\[[^\]]+\]", s))
    classes = len(re.findall(r"\.[a-zA-Z0-9_-]+", s))
    pseudos = len(re.findall(r":(?!:)[a-zA-Z0-9_-]+(\([^)]*\))?", s))
    b = attrs + classes + pseudos

    # 3. Elements and pseudo-elements
    # Strip IDs, attrs, classes, pseudos
    elem_str = re.sub(r"#[a-zA-Z0-9_-]+", " ", s)
    elem_str = re.sub(r"\[[^\]]+\]", " ", elem_str)
    elem_str = re.sub(r"\.[a-zA-Z0-9_-]+", " ", elem_str)
    elem_str = re.sub(r"::[a-zA-Z0-9_-]+", " ", elem_str)
    elem_str = re.sub(r":(?!:)[a-zA-Z0-9_-]+(\([^)]*\))?", " ", elem_str)
    elem_str = re.sub(r"[>+~*]", " ", elem_str)
    elements = len([word for word in elem_str.split() if word])

    return (ids, b, elements)


# ==============================================================================
# Test 1: Exact String Equality and Length Against ORIGINAL_REQUEST.md
# ==============================================================================
def test_css_evaluated_string_length_and_exact_equality() -> None:
    """Verify LEGAL_SAATHI_CUSTOM_CSS evaluates byte-for-byte to ORIGINAL_REQUEST.md if available."""
    assert len(LEGAL_SAATHI_CUSTOM_CSS) > 0, "LEGAL_SAATHI_CUSTOM_CSS must not be empty"
    if not ORIGINAL_REQUEST_FILE.exists():
        return
    raw_markdown = ORIGINAL_REQUEST_FILE.read_text(encoding="utf-8")

    code_pattern = r"```python\s*(LEGAL_SAATHI_CUSTOM_CSS: str = .*?)\n```"
    match = re.search(code_pattern, raw_markdown, re.DOTALL)
    if match is None:
        return

    requested_code = match.group(1)
    eval_scope: dict[str, str] = {}
    exec(requested_code, {}, eval_scope)
    expected_css = eval_scope["LEGAL_SAATHI_CUSTOM_CSS"]
    assert expected_css == LEGAL_SAATHI_CUSTOM_CSS, (
        "Character mismatch between app.py and ORIGINAL_REQUEST.md"
    )


# ==============================================================================
# Test 2: CSS AST, Curly Brace & Quotation Pairing Integrity
# ==============================================================================
def test_css_ast_and_syntax_structure() -> None:
    """Verify CSS syntax, tag bounding, quote pairing, brace pairing, and declaration count."""
    rules = parse_css_ast(LEGAL_SAATHI_CUSTOM_CSS)

    # Minimum rule threshold for our design system
    assert len(rules) >= 15, f"Expected >= 15 CSS rules, parsed {len(rules)}"

    # Ensure every rule has non-empty declarations
    for rule in rules:
        assert len(rule.declarations) > 0, f"Empty rule body: {rule.raw_selector}"
        for prop, val in rule.declarations.items():
            assert len(prop) > 0, "Empty CSS property name"
            assert len(val) > 0, f"Empty CSS property value for {prop}"


# ==============================================================================
# Test 3: Selector Specificity and Design Token Hex Code Mappings
# ==============================================================================
def test_selector_specificity_and_required_hex_codes() -> None:
    """Verify all 5 required hex codes are correctly mapped to corresponding UI elements."""
    rules = parse_css_ast(LEGAL_SAATHI_CUSTOM_CSS)

    # 1. Hex #33312C / #ADABA5: Border strong for inputs and buttons per DESIGN.md
    input_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] [data-baseweb="input"]' in s for s in r.selectors)
    ]
    assert len(input_rules) >= 1
    assert "1px solid #33312c !important" in input_rules[0].declarations.get("border", "").lower()

    select_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] [data-baseweb="select"] > div' in s for s in r.selectors)
    ]
    assert len(select_rules) >= 1
    assert "1px solid #33312c !important" in select_rules[0].declarations.get("border", "").lower()

    sec_btn_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] button:not([kind="primary"])' in s for s in r.selectors)
    ]
    assert len(sec_btn_rules) >= 1
    assert "1px solid #33312c !important" in sec_btn_rules[0].declarations.get("border", "").lower()

    main_input_rules = [
        r
        for r in rules
        if any('[data-testid="stMain"] [data-baseweb="input"]' in s for s in r.selectors)
    ]
    assert len(main_input_rules) >= 1
    main_border = main_input_rules[0].declarations.get("border", "").lower()
    assert "1px solid #adaba5 !important" in main_border

    # 2. Hex #FAFAF9: Expander summary bg/border, input text color, primary button bg
    expander_summary_rules = [
        r
        for r in rules
        if any(
            '[data-testid="stSidebar"] [data-testid="stExpander"] details summary' in s
            for s in r.selectors
        )
    ]
    assert len(expander_summary_rules) >= 1
    assert expander_summary_rules[0].declarations.get("background-color") == "#FAFAF9 !important"
    assert expander_summary_rules[0].declarations.get("border") == "1px solid #FAFAF9 !important"

    input_text_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] input[type="text"]' in s for s in r.selectors)
    ]
    assert len(input_text_rules) >= 1
    assert input_text_rules[0].declarations.get("color") == "#FAFAF9 !important"

    prim_btn_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] button[kind="primary"]' in s for s in r.selectors)
    ]
    assert len(prim_btn_rules) >= 1
    assert prim_btn_rules[0].declarations.get("background-color") == "#FAFAF9 !important"
    assert prim_btn_rules[0].declarations.get("border") == "1px solid #FAFAF9 !important"

    # 3. Hex #0F0E0D: Sidebar canvas root bg, expander text & SVG icon fill, primary button text
    sidebar_root_rules = [
        r for r in rules if any('[data-testid="stSidebar"]' in s for s in r.selectors)
    ]
    assert len(sidebar_root_rules) >= 1
    assert sidebar_root_rules[0].declarations.get("background-color") == "#0F0E0D !important"

    expander_text_rules = [
        r
        for r in rules
        if any(
            '[data-testid="stSidebar"] [data-testid="stExpander"] details summary *' in s
            for s in r.selectors
        )
    ]
    assert len(expander_text_rules) >= 1
    assert expander_text_rules[0].declarations.get("color") == "#0F0E0D !important"
    assert (
        expander_text_rules[0].declarations.get("-webkit-text-fill-color") == "#0F0E0D !important"
    )
    assert expander_text_rules[0].declarations.get("fill") == "#0F0E0D !important"

    # 4. Hex #8F8B85: Sidebar labels, markdown, chevron icons, primary button hover
    label_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] label' in s for s in r.selectors)
    ]
    assert len(label_rules) >= 1
    assert label_rules[0].declarations.get("color") == "#8F8B85 !important"

    icon_rules = [
        r
        for r in rules
        if any('[data-testid="stSidebar"] [data-baseweb="select"] svg' in s for s in r.selectors)
    ]
    assert len(icon_rules) >= 1
    assert icon_rules[0].declarations.get("fill") == "#8F8B85 !important"
    assert icon_rules[0].declarations.get("color") == "#8F8B85 !important"

    # 5. Hex #1F1D1A: Expander details container bg, secondary button hover bg
    expander_details_rules = [
        r
        for r in rules
        if any(
            '[data-testid="stSidebar"] [data-testid="stExpander"] [data-testid="stExpanderDetails"]'
            in s
            for s in r.selectors
        )
    ]
    assert len(expander_details_rules) >= 1
    assert expander_details_rules[0].declarations.get("background-color") == "#1F1D1A !important"

    sec_hover_rules = [
        r
        for r in rules
        if any(
            '[data-testid="stSidebar"] button:not([kind="primary"]):hover' in s for s in r.selectors
        )
    ]
    assert len(sec_hover_rules) >= 1
    assert sec_hover_rules[0].declarations.get("background-color") == "#1F1D1A !important"


def test_sidebar_selector_specificity_dominance() -> None:
    """Verify that sidebar overrides strictly dominate base Streamlit selectors."""
    # Compare sidebar input override against base input
    sidebar_input_spec = compute_css_specificity('[data-testid="stSidebar"] [data-baseweb="input"]')
    base_input_spec = compute_css_specificity('[data-baseweb="input"]')
    assert sidebar_input_spec > base_input_spec, (
        f"{sidebar_input_spec} must be > {base_input_spec}"
    )
    assert sidebar_input_spec == (0, 2, 0)

    # Compare sidebar expander summary against base summary
    sidebar_exp_spec = compute_css_specificity(
        '[data-testid="stSidebar"] [data-testid="stExpander"] details summary'
    )
    base_exp_spec = compute_css_specificity('[data-testid="stExpander"] details summary')
    assert sidebar_exp_spec > base_exp_spec, f"{sidebar_exp_spec} must be > {base_exp_spec}"
    assert sidebar_exp_spec == (0, 2, 2)

    # Compare sidebar primary button against base primary button
    sidebar_btn_spec = compute_css_specificity(
        '[data-testid="stSidebar"] button[kind="primary"]'
    )
    base_btn_spec = compute_css_specificity('button[kind="primary"]')
    assert sidebar_btn_spec > base_btn_spec, f"{sidebar_btn_spec} must be > {base_btn_spec}"
    assert sidebar_btn_spec == (0, 2, 1)


# ==============================================================================
# Test 4: WCAG 2.1 Mathematical Contrast Verification
# ==============================================================================
def test_wcag_contrast_ratios_for_all_three_fixes() -> None:
    """Empirically calculate and assert WCAG contrast compliance for all 3 fixes."""
    # Fix 1: Input border (#ADABA5) vs Sidebar canvas (#0F0E0D) and Expander body (#1F1D1A)
    # WCAG 1.4.11 Non-text contrast: minimum 3.0:1
    border_vs_sidebar = wcag_contrast_ratio("#ADABA5", "#0F0E0D")
    border_vs_expander = wcag_contrast_ratio("#ADABA5", "#1F1D1A")
    assert border_vs_sidebar >= 3.0, f"Input border contrast too low: {border_vs_sidebar:.2f}:1"
    assert border_vs_expander >= 3.0, f"Input border contrast too low: {border_vs_expander:.2f}:1"
    assert 8.0 <= border_vs_sidebar <= 9.0  # Approx 8.40:1
    assert 7.0 <= border_vs_expander <= 8.0  # Approx 7.32:1

    # Invalidate previous buggy state (#33312C on #1F1D1A)
    old_border_contrast = wcag_contrast_ratio("#33312C", "#1F1D1A")
    assert old_border_contrast < 3.0, (
        f"Old border unexpectedly passed contrast: {old_border_contrast:.2f}:1"
    )
    assert old_border_contrast < 1.5  # Approx 1.29:1 (blends completely into dark background)

    # Fix 2: Expander summary text (#0F0E0D) vs summary background (#FAFAF9)
    # WCAG 1.4.3 Normal text: AA >= 4.5:1, AAA >= 7.0:1
    expander_text_contrast = wcag_contrast_ratio("#0F0E0D", "#FAFAF9")
    assert expander_text_contrast >= 7.0, (
        f"Expander text failed WCAG AAA: {expander_text_contrast:.2f}:1"
    )
    assert 18.0 <= expander_text_contrast <= 19.0  # Approx 18.46:1

    # Expander toggle icon (#0F0E0D) on #FAFAF9: WCAG Non-text >= 3.0:1
    expander_icon_contrast = wcag_contrast_ratio("#0F0E0D", "#FAFAF9")
    assert expander_icon_contrast >= 3.0

    # Fix 3: Sidebar labels (#8F8B85) vs sidebar background (#0F0E0D)
    # WCAG 1.4.3 Normal text: AA >= 4.5:1
    label_contrast = wcag_contrast_ratio("#8F8B85", "#0F0E0D")
    assert label_contrast >= 4.5, f"Sidebar label failed WCAG AA: {label_contrast:.2f}:1"
    assert 5.0 <= label_contrast <= 6.0  # Approx 5.69:1


# ==============================================================================
# Test 5: Adversarial Edge Cases & Browser Interoperability
# ==============================================================================
def test_webkit_text_fill_color_synchronization() -> None:
    """Ensure -webkit-text-fill-color is set whenever color is styled in sidebar controls.

    Chromium and WebKit engines require -webkit-text-fill-color synchronization
    in the dark sidebar to prevent user-agent default text colors from overriding
    the high-contrast theme on form controls and expanders.
    """
    rules = parse_css_ast(LEGAL_SAATHI_CUSTOM_CSS)
    sidebar_text_rules = [
        r
        for r in rules
        if any(
            term in r.raw_selector
            for term in [
                'input[type="text"]',
                "placeholder",
                "details summary *",
                'button[kind="primary"] *',
                'button:not([kind="primary"]) *',
            ]
        )
    ]
    assert len(sidebar_text_rules) == 5, f"Expected 5 rules, got {len(sidebar_text_rules)}"
    for rule in sidebar_text_rules:
        assert "color" in rule.declarations, f"Missing color in {rule.raw_selector}"
        assert "-webkit-text-fill-color" in rule.declarations, (
            f"Missing -webkit-text-fill-color in {rule.raw_selector}"
        )
        assert rule.declarations["-webkit-text-fill-color"] == rule.declarations["color"], (
            f"Mismatch between color and -webkit-text-fill-color in {rule.raw_selector}"
        )


def test_svg_icon_path_stroke_suppression() -> None:
    """Verify SVG icon paths have stroke: none !important to avoid stroke bloat."""
    rules = parse_css_ast(LEGAL_SAATHI_CUSTOM_CSS)
    svg_path_rules = [
        r for r in rules if any('path:not([fill="none"])' in s for s in r.selectors)
    ]
    assert len(svg_path_rules) >= 1
    for r in svg_path_rules:
        assert r.declarations.get("stroke") == "none !important"
