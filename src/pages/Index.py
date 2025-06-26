import streamlit as st

st.set_page_config(layout="wide")

pages = {
    "": [  # Empty section title so it doesn't repeat "Home"
        st.Page("main_page.py", title="Home")
    ],
    "Data Stories": [
        st.Page("a34_story.py", title="Grounds for Refusal of Immigration Applications"),
        st.Page("africa_vs_non_africa.py", title="Litigation Outcomes by Region"),
        st.Page("litigation_dashboard.py", title="Country-Level Case Type & Outcome Analysis"),
    ],
    "Interactive Dashboards": [
        st.Page("A34_Refused_Data.py", title="A34(1) Inadmissibility Refusal"),
        st.Page("litigation_interactive.py", title="Litigation Applications Dashboard"),
    ],
}

pg = st.navigation(pages)
pg.run()
