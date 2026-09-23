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
        st.Page("views/events.py", title="Events", icon=":material/event:"),
    ],
    "Workspace": [
        st.Page("views/journal.py", title="Journal", icon=":material/edit_note:"),
        st.Page("views/admin.py", title="Data / Admin", icon=":material/database:"),
    ],
})
page.run()
