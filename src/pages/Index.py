import streamlit as st

st.set_page_config(layout="wide")
pages = {
    "Dashboard": [
        st.Page("A34_Refused_Data.py", title="A34 Refused Data"),
        st.Page("litigation_dashboard.py", title="Litigation Dashboard"),
        st.Page("litigation_interactive.py", title="Litigation Interactive"),
    ],

}
pg = st.navigation(pages)
pg.run()
