import sqlite3
import random
from io import BytesIO
from datetime import datetime

import pandas as pd
import streamlit as st

DB_PATH = "questions.db"

st.set_page_config(page_title="Question Paper Builder", page_icon="📝", layout="wide")

CATEGORIES = ["Officer", "Sailor/Agniveer", "Both"]
TRADES = ["Electrical", "Mechanical", "Both"]
DIFFICULTIES = [0, 1, 2, 3, 4, 5]


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                option_a TEXT NOT NULL,
                option_b TEXT NOT NULL,
                option_c TEXT NOT NULL,
                option_d TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                strength INTEGER NOT NULL CHECK(strength BETWEEN 0 AND 5),
                candidate_category TEXT NOT NULL,
                trade TEXT NOT NULL,
                topic TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)
        count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        if count == 0:
            seed_questions(conn)


def seed_questions(conn):
    # Fictional, beginner-friendly demonstration questions only.
    rows = [
        ("What is the unit of electric current?", "Volt", "Ampere", "Ohm", "Watt", "B", 1, "Both", "Electrical", "Basic electricity"),
        ("Which instrument measures voltage?", "Ammeter", "Voltmeter", "Wattmeter", "Ohmmeter", "B", 1, "Both", "Electrical", "Instruments"),
        ("What is the SI unit of resistance?", "Ohm", "Ampere", "Volt", "Joule", "A", 2, "Sailor/Agniveer", "Electrical", "Basic electricity"),
        ("Which component stores energy in an electric field?", "Resistor", "Fuse", "Capacitor", "Switch", "C", 2, "Both", "Electrical", "Components"),
        ("What is the main purpose of a fuse?", "Increase voltage", "Protect against excess current", "Store charge", "Measure resistance", "B", 2, "Both", "Electrical", "Safety"),
        ("Which law relates voltage, current and resistance?", "Newton's law", "Ohm's law", "Faraday's law only", "Hooke's law", "B", 3, "Both", "Electrical", "Circuit theory"),
        ("In a series circuit, which quantity is the same through ideal components?", "Voltage", "Power", "Current", "Resistance", "C", 3, "Officer", "Electrical", "Circuit theory"),
        ("What does a transformer primarily change?", "AC voltage level", "DC frequency", "Wire resistance permanently", "Battery chemistry", "A", 3, "Officer", "Electrical", "Machines"),
        ("Which device converts mechanical energy into electrical energy?", "Motor", "Generator", "Rectifier", "Resistor", "B", 3, "Both", "Electrical", "Machines"),
        ("What is the purpose of earthing in an electrical installation?", "Raise normal operating voltage", "Provide a safer path for fault current", "Increase power consumption", "Eliminate all maintenance", "B", 4, "Officer", "Electrical", "Safety"),
        ("For an ideal resistor, if voltage doubles and resistance stays constant, current will:", "Halve", "Double", "Stay unchanged", "Become zero", "B", 4, "Officer", "Electrical", "Circuit theory"),
        ("Which instrument is commonly used to measure insulation resistance?", "Megohmmeter", "Tachometer", "Thermometer", "Hydrometer", "A", 4, "Both", "Electrical", "Testing"),
        ("Which tool is generally used to tighten a hexagonal bolt?", "Spanner", "Hacksaw", "File", "Scriber", "A", 1, "Sailor/Agniveer", "Mechanical", "Tools"),
        ("Which instrument measures rotational speed?", "Barometer", "Tachometer", "Ammeter", "Caliper", "B", 2, "Both", "Mechanical", "Instruments"),
        ("What is the main purpose of lubrication?", "Increase friction", "Reduce friction and wear", "Increase corrosion", "Reduce component size", "B", 2, "Both", "Mechanical", "Maintenance"),
        ("Which device converts rotary motion into reciprocating motion in many engines?", "Crank mechanism", "Fuse", "Transformer", "Capacitor", "A", 3, "Officer", "Mechanical", "Mechanisms"),
        ("What does a vernier caliper measure?", "Only temperature", "Length or diameter", "Electrical current", "Fluid acidity", "B", 3, "Both", "Mechanical", "Measurement"),
        ("Which property describes resistance to indentation or scratching?", "Hardness", "Ductility", "Elasticity only", "Conductivity", "A", 3, "Both", "Mechanical", "Materials"),
        ("What is preventive maintenance intended to do?", "Wait for failure", "Reduce likelihood of unexpected failure", "Remove safety checks", "Increase downtime", "B", 4, "Officer", "Mechanical", "Maintenance"),
        ("Why is alignment important between coupled rotating shafts?", "To increase imbalance", "To reduce vibration and bearing stress", "To stop lubrication", "To increase friction", "B", 4, "Officer", "Mechanical", "Maintenance"),
        ("Which category includes questions tagged for every candidate type?", "Officer only", "Sailor only", "Both", "None", "C", 1, "Both", "Both", "General"),
        ("Which practice is safest before servicing powered equipment?", "Work while energized", "Isolate energy and verify safe state", "Remove warning labels", "Use damaged tools", "B", 3, "Both", "Both", "Safety"),
        ("What should be checked before using a measuring instrument?", "Its color only", "Condition and suitable range", "The operator's shoe size", "Nothing", "B", 2, "Sailor/Agniveer", "Both", "Safety"),
        ("What is the purpose of a maintenance log?", "Hide equipment faults", "Record work, findings and dates", "Replace all inspections", "Increase equipment load", "B", 2, "Both", "Both", "Documentation"),
        ("Why should a question bank record the correct answer?", "For validation and answer-key generation", "To make questions longer", "To avoid categorization", "To remove filtering", "A", 3, "Officer", "Both", "Question bank"),
        ("What should the system do if only 12 questions match a request for 20?", "Silently add unrelated questions", "Report that only 12 match", "Duplicate 8 questions", "Delete the filters", "B", 4, "Both", "Both", "Software logic"),
        ("Why store the IDs of questions used in a generated paper?", "To track usage and prevent repetition", "To change their answers automatically", "To make them public", "To remove the database", "A", 4, "Officer", "Both", "Software logic"),
        ("Which selection method can vary the paper while keeping the filters?", "Random selection from eligible questions", "Always choose the first rows", "Ignore the filters", "Repeat every question", "A", 3, "Both", "Both", "Software logic"),
        ("What is the best response if a saved question has no verified correct answer?", "Use it anyway", "Flag it for review before use", "Guess silently", "Hide the options", "B", 5, "Officer", "Both", "Quality control"),
        ("Why should question-paper exports be access-controlled?", "To reduce unauthorized disclosure", "To make the paper harder to read", "To remove the answer key from storage", "To prevent all printing", "A", 5, "Officer", "Both", "Security"),
    ]
    now = datetime.now().isoformat(timespec="seconds")
    conn.executemany("""
        INSERT INTO questions
        (question_text, option_a, option_b, option_c, option_d, correct_answer,
         strength, candidate_category, trade, topic, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
    """, [tuple(r) + (now,) for r in rows])


def get_questions():
    with connect() as conn:
        return pd.read_sql_query("SELECT * FROM questions ORDER BY id DESC", conn)


def category_matches(row_value, selected):
    return row_value == "Both" or row_value == selected or selected == "Both"


def build_pdf(paper, include_answers=False):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import mm
        from xml.sax.saxutils import escape
    except ImportError:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("PaperTitle", parent=styles["Title"], fontSize=17, leading=21, spaceAfter=10)
    q_style = ParagraphStyle("Question", parent=styles["BodyText"], fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=4)
    opt_style = ParagraphStyle("Option", parent=styles["BodyText"], fontSize=9.5, leading=12, leftIndent=12)
    story = [Paragraph("Question Paper — Demonstration", title_style),
             Paragraph(f"Category: {escape(str(paper['category']))} | Trade: {escape(str(paper['trade']))}", styles["Normal"]),
             Paragraph(f"Questions: {len(paper['rows'])} | Generated: {escape(paper['generated_at'])}", styles["Normal"]),
             Spacer(1, 10)]
    for idx, row in enumerate(paper["rows"], start=1):
        story.append(Paragraph(f"<b>{idx}. {escape(str(row['question_text']))}</b>", q_style))
        for letter, col in [("A", "option_a"), ("B", "option_b"), ("C", "option_c"), ("D", "option_d")]:
            story.append(Paragraph(f"{letter}. {escape(str(row[col]))}", opt_style))
        if include_answers:
            story.append(Paragraph(f"<b>Answer: {escape(str(row['correct_answer']))}</b>", opt_style))
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


init_db()

st.title("📝 Question Paper Builder")
st.caption("A small prototype using a dummy question bank. No AI model is used; questions are filtered from the database.")

tab_add, tab_bank, tab_generate = st.tabs(["➕ Add Question", "📚 Question Bank", "🧾 Generate Paper"])

with tab_add:
    st.subheader("Add a question")
    with st.form("add_question_form", clear_on_submit=True):
        qtext = st.text_area("Question text", placeholder="Enter the question...")
        c1, c2 = st.columns(2)
        with c1:
            opt_a = st.text_input("Option A")
            opt_b = st.text_input("Option B")
        with c2:
            opt_c = st.text_input("Option C")
            opt_d = st.text_input("Option D")
        c3, c4, c5 = st.columns(3)
        with c3:
            answer = st.selectbox("Correct answer", ["A", "B", "C", "D"])
        with c4:
            strength = st.select_slider("Strength / difficulty", options=DIFFICULTIES, value=3)
        with c5:
            category = st.selectbox("Candidate category", CATEGORIES)
        c6, c7 = st.columns(2)
        with c6:
            trade = st.selectbox("Trade", TRADES)
        with c7:
            topic = st.text_input("Topic", value="General")
        submitted = st.form_submit_button("Save question", type="primary")
        if submitted:
            if not all([qtext.strip(), opt_a.strip(), opt_b.strip(), opt_c.strip(), opt_d.strip(), topic.strip()]):
                st.error("Please complete the question, all four options and the topic.")
            else:
                with connect() as conn:
                    conn.execute("""
                        INSERT INTO questions
                        (question_text, option_a, option_b, option_c, option_d, correct_answer,
                         strength, candidate_category, trade, topic, active, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """, (qtext.strip(), opt_a.strip(), opt_b.strip(), opt_c.strip(), opt_d.strip(),
                          answer, int(strength), category, trade, topic.strip(), datetime.now().isoformat(timespec="seconds")))
                st.success("Question saved to the database.")

with tab_bank:
    st.subheader("Question bank")
    df = get_questions()
    a, b, c = st.columns(3)
    with a:
        cat_filter = st.selectbox("Filter by category", ["All"] + CATEGORIES, key="bank_cat")
    with b:
        trade_filter = st.selectbox("Filter by trade", ["All"] + TRADES, key="bank_trade")
    with c:
        diff_filter = st.multiselect("Filter by strength", DIFFICULTIES, default=[], key="bank_diff")
    search = st.text_input("Search question or topic", key="bank_search")
    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered["candidate_category"].apply(lambda x: category_matches(x, cat_filter))]
    if trade_filter != "All":
        filtered = filtered[filtered["trade"].apply(lambda x: category_matches(x, trade_filter))]
    if diff_filter:
        filtered = filtered[filtered["strength"].isin(diff_filter)]
    if search:
        mask = filtered["question_text"].str.contains(search, case=False, na=False) | filtered["topic"].str.contains(search, case=False, na=False)
        filtered = filtered[mask]
    st.metric("Questions shown", len(filtered))
    display_cols = ["id", "question_text", "correct_answer", "strength", "candidate_category", "trade", "topic"]
    st.dataframe(filtered[display_cols], use_container_width=True, hide_index=True)
    st.download_button("Download question bank as CSV", data=filtered.to_csv(index=False).encode("utf-8"),
                       file_name="question_bank.csv", mime="text/csv")

with tab_generate:
    st.subheader("Generate a question paper")
    st.info("A question tagged 'Both' is eligible for either category or trade. Strength is treated as difficulty in this prototype.")
    g1, g2, g3 = st.columns(3)
    with g1:
        gen_category = st.selectbox("Candidate category", ["Officer", "Sailor/Agniveer", "Both"], key="gen_cat")
    with g2:
        gen_trade = st.selectbox("Trade", ["Electrical", "Mechanical", "Both"], key="gen_trade")
    with g3:
        count = st.number_input("Number of questions", min_value=1, max_value=500, value=10, step=1)
    chosen_strengths = st.multiselect("Allowed strength levels", DIFFICULTIES, default=[3, 4, 5])
    avoid_used = st.checkbox("Exclude questions used in this session's previous generated papers", value=False)
    if "used_question_ids" not in st.session_state:
        st.session_state.used_question_ids = set()

    if st.button("Generate paper", type="primary"):
        all_df = get_questions()
        eligible = all_df[all_df["active"] == 1].copy()
        eligible = eligible[
            eligible["candidate_category"].apply(lambda x: category_matches(x, gen_category)) &
            eligible["trade"].apply(lambda x: category_matches(x, gen_trade))
        ]
        if chosen_strengths:
            eligible = eligible[eligible["strength"].isin(chosen_strengths)]
        if avoid_used and st.session_state.used_question_ids:
            eligible = eligible[~eligible["id"].isin(st.session_state.used_question_ids)]
        if len(eligible) < count:
            st.error(f"Only {len(eligible)} matching questions are available, but you requested {count}. Change the filters or add more questions.")
            st.session_state.pop("current_paper", None)
        else:
            selected = eligible.sample(n=int(count), replace=False, random_state=random.randint(0, 2**31 - 1))
            rows = selected.to_dict(orient="records")
            paper = {
                "category": gen_category,
                "trade": gen_trade,
                "rows": rows,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state.current_paper = paper
            st.session_state.used_question_ids.update(int(r["id"]) for r in rows)

    if "current_paper" in st.session_state:
        paper = st.session_state.current_paper
        st.divider()
        st.markdown(f"### Generated paper — {len(paper['rows'])} questions")
        st.caption(f"Category: {paper['category']} · Trade: {paper['trade']} · Generated: {paper['generated_at']}")
        for idx, row in enumerate(paper["rows"], start=1):
            with st.container(border=True):
                st.markdown(f"**{idx}. {row['question_text']}**")
                st.write(f"A. {row['option_a']}")
                st.write(f"B. {row['option_b']}")
                st.write(f"C. {row['option_c']}")
                st.write(f"D. {row['option_d']}")
                with st.expander("Show answer (trainer only)"):
                    st.success(f"Correct answer: {row['correct_answer']}")
        paper_df = pd.DataFrame(paper["rows"])
        export_cols = ["question_text", "option_a", "option_b", "option_c", "option_d"]
        st.download_button("Download paper as CSV", data=paper_df[export_cols].to_csv(index=False).encode("utf-8"),
                           file_name="question_paper.csv", mime="text/csv")
        pdf_bytes = build_pdf(paper, include_answers=False)
        if pdf_bytes:
            st.download_button("Download paper as PDF", data=pdf_bytes, file_name="question_paper.pdf", mime="application/pdf")
        else:
            st.warning("PDF export requires ReportLab. Install it with: pip install reportlab")
        answer_bytes = build_pdf(paper, include_answers=True)
        if answer_bytes:
            st.download_button("Download answer-key PDF (trainer)", data=answer_bytes,
                               file_name="answer_key_trainer_only.pdf", mime="application/pdf")

st.divider()
st.caption("Prototype only: the included questions are fictional demo data. Add authentication and deployment security before using confidential or operational question banks.")
