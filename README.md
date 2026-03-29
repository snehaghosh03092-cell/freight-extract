# 📦 Email Extraction System

This project demonstrates an end-to-end pipeline for extracting structured data from emails using LLMs, along with evaluation, prompt iteration, and system design considerations.

---

# 🚀 Setup Instructions

## 1. Install Dependencies
pip install -r requirements.txt

## 2. Run Extraction Pipeline
python extract.py

### Output
- output.json

---

## 3. Run Evaluation
python evaluate.py

### Outputs
- Field-wise accuracy metrics
- Overall extraction accuracy

---

# 🧠 Prompt Iteration & Improvements

This section shows how the prompt was iteratively improved based on observed LLM failures.

---

## v1: Basic Extraction Prompt

### Approach
- Simple instruction to extract structured fields from email
- Enforced strict JSON output

### Results
- Accuracy: 60%

### Issues Observed
- Incorrect or hallucinated port codes
- Missing or inconsistent incoterms
- No standardization of weight/CBM units

### Example Failure
EMAIL_038  
→ Extracted "China" instead of "Tianjin/Xingang"

EMAIL_014
→ Extracted "China" instead of "Xingang"

EMAIL_031 
→ Incorrect origin inference for “Japanese goods”  
---

## v2: Added Port Reference + UN/LOCODE Constraints

### Improvements
- Introduced full port reference list in prompt
- Forced port selection from valid dataset only
- Explicit routing rules (ICD > POD priority)
- Added rule to extract places name from terms like "japanese goods"

### Results
- Accuracy: 84%

### Issues
- RT was classified as cargo_cbm but cargo_weight was calculated from it
- Some places that are present in same code are identified as different port assignments.

### Example Failure
EMAIL_034
- cargo_weight_kg assigned as NULL

EMAIL_007
- cargo_weight_kg assigned as NULL

---

## v2: Business Rules + Normalization Layer Added

### Improvements
- Unit conversion rules (kg/lbs/tons/CBM/RT)
- Incoterm normalization, explicit mentioning of terms
- Dangerous goods detection rules
- Added rule for identifying places grouped under same code as single consignment

### Results
- Accuracy: 96%

### Remaining Issues
EMAIL_026
→ RT given, cargo_weight_kg assigned is NULL

EMAIL_042
→ CBM extraction missed due to malformed dimensions

EMAIL_006
→ Incoterm extracted as "FCA"
---

# 🧪 Edge Cases Handled

## Edge Case 1: Implicit Origin Detection
Emails: EMAIL_011, EMAIL_031  
Issue: Origin not explicitly mentioned

### Fix
- Added adjective → country mapping
- Japanese → Japan
- Chinese → China

---

## Edge Case 2: Multiple Shipments in One Email
Emails: EMAIL_025  
Issue: Model incorrectly split shipments

### Fix
- Split only if origin_port_code differs
- Otherwise treat as a single RFQ

---

## Edge Case 3: Mixed Units in Single Email
Emails: EMAIL_018  
Issue: lbs and CBM mixed

### Fix
- Do not convert between weight and CBM
- Extract independently

---

# 🏗️ System Design

## 1. Scaling to 10,000 Emails/Day (5 min SLA, $500 Budget)

### Architecture
- Message queue (SQS / RabbitMQ) for ingestion so that spikes in email can be handled
- Worker pool (FastAPI + async workers / Kubernetes jobs) can be introduced to process/consume from queue
- Batch processing with chunked LLM calls
- We can itroduce redis cache for repeated lookups

### LLM Cost Control
- Batch multiple emails per prompt
- Use smaller models for simple cases
- Fallback to larger LLM when needed

### Optimization
- Parallel async processing
- Retry only failed extractions

---

## 2. Monitoring Accuracy Drop (90% → 70%)

### Detection
We can track following parameters:
- Field-level accuracy
- Confidence score distribution
- Validation failure rate

### Alerting
- We need to make Grafana / Prometheus dashboards to visualise the drop over time series
- Need to set up alerts when:
   - Accuracy drops >5%
   - Validation failures spike

### Investigation
- Sample failed emails
- Compare:
   - Prompt changes
   - New formats
   - Dataset updates

### Root Causes
- New unseen formats
- Model drift
- Prompt regression

---

## 3. Multilingual Emails (Mandarin + Hindi)

### Changes Required

### Translation Layer
- LLM-based translation
- Or external API (e.g., Google Translate)

### Prompt Enhancements
- Add multilingual examples
- Normalize country names

---

### Evaluation Strategy
- Maintain multilingual test dataset
- Measure per-language accuracy
- Compare pipelines

---

### Risk Mitigation
- High ambiguity in Mandarin ports
- Use bilingual port dictionary

---

# ✅ Summary

This system demonstrates:

- Real-world LLM prompt engineering
- Structured output validation
- Domain-specific constraint design
- Iterative improvement loop
- Scalable system design for production use

---
