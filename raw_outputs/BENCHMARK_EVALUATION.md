# Legal Saathi — Master Benchmark Evaluation Report

**Generated**: 2026-11-07 10:42:57 UTC  
**Execution Mode**: mock_llm (mock / mock-llama3.1:8b)  
**Corpus Tested**: CPA 2019, 2021 Pecuniary Rules, E-Commerce Rules 2020, e-Daakhil/NCH Guidelines  
**Total Latency**: 0.3679 seconds  

---

## 1. Executive Performance Dashboard

| Benchmark Metric | Target Standard | Achieved Score | Status |
|:-----------------|:---------------:|:--------------:|:------:|
| **Scope Detection Accuracy** | 100.0% | **100.0% (5/5)** | PASS |
| **Hybrid Retrieval Precision** | >= 80.0% | **100.0%** | PASS |
| **Citation Verification Pass Rate** | 100.0% | **100.0%** | PASS |
| **Document Drafting Completeness** | 100.0% | **100.0% (12/12)** | PASS |
| **Simulation Realism Score** | >= 85.0/100 | **100.0 / 100** | PASS |

---

## 2. Multi-Scenario Benchmark Results Matrix

| Scenario ID | Dispute Category | Disputed Amount | Scope Detected | Top Hit Section | Citations Verified | Documents Drafted | Sim Score | Result |
|:---|:---|:---:|:---:|:---|:---:|:---:|:---:|:---:|
| `scenario_1` | ecommerce_defective_goods | INR 89,999 | In-Scope | Section 2(11) | 31 / 31 (100.0%) | 3 / 3 | 100.0 | PASS |
| `scenario_2` | social_commerce_fraud | INR 4,500 | In-Scope | Section 2(11) | 33 / 33 (100.0%) | 3 / 3 | 100.0 | PASS |
| `scenario_3` | edtech_subscription_trap | INR 60,000 | In-Scope | Section 2(11) | 33 / 33 (100.0%) | 3 / 3 | 100.0 | PASS |
| `scenario_4` | quick_commerce_short_delivery | INR 1,800 | In-Scope | Section 2(11) | 30 / 30 (100.0%) | 3 / 3 | 100.0 | PASS |
| `scenario_5` | commercial_b2b_cheque_bounce | INR 25,000,000 | Out-of-Scope | N/A (Escalated) | N/A (Blocked) | 0 / 0 (Blocked) | N/A | PASS |

---

## 3. Mathematical Metric Definitions & Evaluation Formulas

1. **Scope Detection Accuracy**:
   $$\text{Accuracy} = \frac{\sum_{i=1}^{5} \mathbb{I}(\text{detected\_scope}_i == \text{expected\_scope}_i)}{5} \times 100\%$$
   - Evaluates Layer 1 Pre-Retrieval Filter. Successfully admitted all 4 genuine consumer grievances while deterministically intercepting Scenario 5 (Commercial B2B dispute under Section 138 NI Act with criminal threats) and issuing Bar Council of India Advocate escalation advice.

2. **Retrieval Precision**:
   $$\text{Precision} = \frac{|\text{Retrieved Sections} \cap \text{Expected Statutory Sections}|}{|\text{Expected Statutory Sections}|} \times 100\%$$
   - Evaluates whether CPA 2019 and E-Commerce Rules provisions governing the dispute appear within candidate hybrid RRF chunks.

3. **Citation Verification Pass Rate**:
   $$\text{Pass Rate} = \frac{\text{Verified Citations}}{\text{Verified Citations} + \text{Flagged Fabricated Citations}} \times 100\%$$
   - Validates Layer 3 Post-Generation Verifier: ensures zero hallucinated Section numbers or non-existent rules appear in user outputs.

4. **Document Drafting Completeness**:
   $$\text{Completeness} = \frac{\text{Complete Required Documents Generated}}{\text{Expected Documents (4 in-scope} \times 3 = 12\text{)}} \times 100\%$$
   - Assesses automated generation of Grievance Escalation Email, 15-Day Legal Demand Notice, and 7-part e-Daakhil Complaint petition across all in-scope cases.

5. **Simulation Realism Score**:
   $$\text{Average Score} = \frac{1}{N_{\text{in-scope}}} \sum_{i=1}^{N_{\text{in-scope}}} \text{Simulator Evaluation Score}_i$$
   - Quantitative evaluation of consumer rebuttals against realistic corporate merchant defense tactics (Safe Harbor, T&C exclusions, 3PL shifts, and OTP confirmations).
