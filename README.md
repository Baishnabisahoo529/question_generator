# Question Paper Builder — Prototype

A small Streamlit + SQLite prototype using fictional demonstration questions.

## Features
- Add multiple-choice questions with four options and a correct answer
- Tag questions by Officer / Sailor-Agniveer / Both
- Tag questions by Electrical / Mechanical / Both
- Set strength/difficulty from 0 to 5
- Browse/search/filter the question bank
- Generate a random question paper using filters
- Prevent duplicate questions within one paper
- Optionally exclude questions already used in this browser session
- Download the question bank as CSV
- Download generated paper and answer key as PDF

## Run locally
1. Install Python 3.10 or newer.
2. Extract this ZIP.
3. Open a terminal in the extracted folder.
4. Install dependencies:

   `python -m pip install -r requirements.txt`

5. Start the app:

   `streamlit run app.py`

6. Your browser should open the local app.

The SQLite database (`questions.db`) is created automatically the first time the app runs and seeded with 30 fictional sample questions.

## Notes
- This is a prototype, not production-ready.
- There is no login/authentication yet.
- Do not use real confidential question banks until access controls, backups, and deployment security are added.
- Strength is treated as difficulty in this demo. Confirm the trainer's intended meaning before production.
