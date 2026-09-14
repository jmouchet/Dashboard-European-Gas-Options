import streamlit as st
from components.session import curriculum, page_header
from learning.content import HISTORY, HISTORY_URL

page_header("Daily Learning", "Starter pack · Units, storage and LNG · About 15–20 minutes")
articles, questions = curriculum()
by_slug = {a["slug"]: a for a in articles}
st.caption("This fixed pack follows the first-build roadmap. Adaptive selection comes in a later version.")
st.subheader("Three facts to keep")
for slug in ["units", "storage", "lng"]:
    if slug in by_slug:
        st.markdown(f"**{by_slug[slug]['title']}** — {by_slug[slug]['summary']}")
        st.markdown(f"[Primary reference]({by_slug[slug]['source_urls'][0]})")
st.subheader("One mechanism to explain")
st.write("Explain why gas in storage and gas deliverable tomorrow are different quantities. Describe one constraint at each stage of the LNG supply chain.")
st.subheader("One calculation")
st.write("Illustrative exercise: convert 50 mcm into GWh at an explicitly assumed 11 kWh/m³.")
with st.expander("Show calculation and assumptions"):
    st.write("50 × 11 = 550 GWh. The assumed calorific value must be replaced with a documented value for real data, including reference conditions and HHV/LHV basis.")
st.subheader("One chart to investigate")
st.write("Open your Morning observation history. Identify a change and check its source, date and unit before explaining it.")
st.page_link("views/morning.py", label="Open observation history →")
st.subheader("One historical episode")
st.write(HISTORY)
st.markdown(f"[IEA: Gas Market Report, Q1-2023]({HISTORY_URL})")
st.subheader("Five-question review")
st.write("Open Quiz & Review and select Starter pack to answer five questions, reveal explanations and record confidence.")
st.page_link("views/quiz.py", label="Start the review →")
