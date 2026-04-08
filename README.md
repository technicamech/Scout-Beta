# Scout — V0.11 Beta

AI-assisted diagnostic planning tool for professional automotive technicians.

---

## What Scout Does

Scout helps technicians determine the most logical **next diagnostic step** based on:

- Vehicle information (VIN or manual entry)
- Customer complaint
- Fault codes
- Technician observations

It produces:
- Structured diagnostic reasoning
- Ranked probable causes
- Step-by-step diagnostic path
- Suggested service information references

---

## What Scout Is NOT

- Not a repair manual  
- Not a parts replacement tool  
- Not always correct  

Scout is a **diagnostic aid**, not a decision-maker.

---

## Beta Status

Version: **V0.11 Beta**

This is an early field-test release:
- Core functionality only
- Some rough edges expected
- Focus is **diagnostic logic and usefulness**

---

## Core Features

- VIN decoding via NHTSA vPIC
- Manual vehicle entry (year / make / model / trim / engine / transmission)
- Structured AI diagnostic planning
- Recall and manufacturer communication awareness (NHTSA)
- Local case logging for feedback and repair outcomes
- Service reference guidance (wiring, procedures, specs, etc.)

---

## Data Sources

Scout uses:
- NHTSA vPIC (VIN decoding)
- NHTSA recall data
- Optional local service manual dataset (user-provided)

---

## Files

- `app.py` — main Streamlit app
- `requirements.txt` — Python dependencies

---

## Install

pip install -r requirements.txt

---

## Set your OpenAI API key

PowerShell:

$env:OPENAI_API_KEY="your_key_here"

---

## Run the app

streamlit run app.py

---

## Optional: Local Service Data

You can point Scout to a local service manual dataset:

$env:SCOUT_LOCAL_DATASET_DIR="C:\path\to\your\manuals"

---

## Feedback (Beta Testers)

Feedback is critical to improving Scout.

Focus on:
- Diagnostic logic
- Clarity
- Real-world usefulness

---

## Disclaimer

Scout is a diagnostic aid only.

Always verify findings using proper testing procedures, service information, safety practices, and manufacturer specifications.
