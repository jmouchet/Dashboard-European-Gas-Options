import streamlit as st
from components.session import curriculum, page_header

page_header("Knowledge Wiki", "A sourced foundation for European gas and gas options.")
articles, questions = curriculum()
query = st.text_input("Search articles", placeholder="Storage, TTF, delta…")
category = st.selectbox("Category", ["All"] + sorted({a["category"] for a in articles}))
matches = [a for a in articles if (category == "All" or a["category"] == category)
           and query.casefold() in (a["title"] + " " + a["content_markdown"]).casefold()]
if not matches:
    st.info("No articles match this search.")
else:
    chosen = st.selectbox("Article", matches, format_func=lambda a: a["title"])
    st.subheader(chosen["title"])
    st.caption(f"{chosen['category']} · Difficulty {chosen['difficulty']}/5")
    st.markdown(chosen["content_markdown"])
    st.page_link("views/quiz.py", label="Practice in Quiz & Review →")
