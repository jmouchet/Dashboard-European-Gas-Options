import streamlit as st
from components.session import setup_sidebar

st.set_page_config(page_title="Gas Intelligence", page_icon="🔥", layout="wide")
setup_sidebar()

page = st.navigation({
    "Market Dashboard": [
        st.Page("views/morning.py", title="Morning", icon=":material/wb_sunny:", default=True),
        st.Page("views/markets.py", title="Markets", icon=":material/show_chart:"),
        st.Page("views/fundamentals.py", title="Fundamentals", icon=":material/storage:"),
        st.Page("views/physical.py", title="Physical System", icon=":material/hub:"),
        st.Page("views/options.py", title="Options & Volatility", icon=":material/ssid_chart:"),
        st.Page("views/events.py", title="Events", icon=":material/event:"),
    ],
    "Build understanding": [
        st.Page("views/knowledge.py", title="Knowledge Wiki", icon=":material/menu_book:"),
        st.Page("views/daily_learning.py", title="Daily Learning", icon=":material/school:"),
        st.Page("views/quiz.py", title="Quiz & Review", icon=":material/quiz:"),
    ],
    "Workspace": [
        st.Page("views/journal.py", title="Journal", icon=":material/edit_note:"),
        st.Page("views/admin.py", title="Data / Admin", icon=":material/database:"),
    ],
})
page.run()
