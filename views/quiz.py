import time
from uuid import uuid4
import streamlit as st
from components.session import curriculum, page_header, read_rows, save_row
from data.validation import utc_now
from learning.review import summarize_attempts

page_header("Quiz & Review", "Explain your answer first; then compare with the reference and assess it honestly.")
articles, questions = curriculum()
attempts = read_rows("quiz_attempts")
summary = summarize_attempts(attempts)
cols = st.columns(3)
cols[0].metric("Recorded attempts", summary["attempts"])
cols[1].metric("Self-assessed average", "—" if summary["average_score"] is None else f"{summary['average_score']:.0%}")
cols[2].metric("Wrong + very confident", summary["confident_errors"])
st.caption("Scores are self-assessed: wrong = 0, partial = 0.5, correct = 1. These are not certified mastery scores.")
mode = st.selectbox("Question set", ["Starter pack", "All questions", "By topic", "Calculations", "Reasoning"])
title_by_slug = {a["slug"]: a["title"] for a in articles}
if mode == "Starter pack":
    selected = [q for q in questions if q["topic"] in {"units", "storage", "lng"}][:5]
elif mode == "By topic":
    topic = st.selectbox("Topic", list(title_by_slug), format_func=title_by_slug.get)
    selected = [q for q in questions if q["topic"] == topic]
elif mode == "Calculations":
    selected = [q for q in questions if q["question_type"] == "calculation"]
elif mode == "Reasoning":
    selected = [q for q in questions if q["question_type"] not in {"calculation", "recall"}]
else:
    selected = questions
if not selected:
    st.info("No questions in this set.")
    st.stop()
question = st.selectbox("Question", selected, format_func=lambda q: q["question"])
qid = question["id"]
state_key = f"answer_{qid}"
start_key = f"start_{qid}"
st.session_state.setdefault(start_key, time.monotonic())
st.caption(f"{title_by_slug.get(question['topic'], question['topic'])} · {question['question_type']} · Difficulty {question['difficulty']}/5")
if state_key not in st.session_state:
    with st.form(f"question_{qid}"):
        answer = st.text_area("Your answer")
        confidence = st.radio("Confidence before seeing the answer", [1, 2, 3, 4],
                              format_func=lambda c: {1: "1 · Guess", 2: "2 · Unsure", 3: "3 · Reasonably sure", 4: "4 · Very sure"}[c])
        reveal = st.form_submit_button("Reveal reference answer", type="primary")
    if reveal:
        if not answer.strip():
            st.error("Write an answer before revealing the reference.")
        else:
            st.session_state[state_key] = {
                "id": str(uuid4()), "question_id": qid, "user_answer": answer.strip(),
                "confidence": confidence, "attempt_date": utc_now(),
                "response_time": max(0, time.monotonic() - st.session_state[start_key]),
                "grading_method": "self_assessed",
            }
            st.rerun()
else:
    pending = st.session_state[state_key]
    st.markdown("**Your recorded answer**")
    st.write(pending["user_answer"])
    st.caption(f"Original confidence: {pending['confidence']}/4")
    st.info(question["answer"])
    st.write(question["explanation"])
    score = st.radio("Self-assessment", [0.0, 0.5, 1.0], index=None,
                     format_func=lambda s: {0: "Wrong", 0.5: "Partly correct", 1: "Correct"}[s], key=f"score_{qid}")
    if st.button("Save attempt", type="primary", disabled=score is None):
        if save_row("quiz_attempts", {**pending, "score": score}):
            del st.session_state[state_key]
            st.session_state.pop(start_key, None)
            st.session_state.pop(f"score_{qid}", None)
            st.rerun()
st.page_link("views/knowledge.py", label="Review the Wiki →")
