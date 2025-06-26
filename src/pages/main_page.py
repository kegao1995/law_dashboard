import streamlit as st

st.set_page_config(layout="wide")

# Dashboard Introduction
st.title("Immigration Litigation and Refusal Insights Dashboard")
st.markdown("""
Welcome to the Immigration Insights Dashboard. This dashboard presents data-driven stories and interactive visualizations based on publicly available datasets from Canadian immigration authorities. It is designed to help users explore patterns in **application refusals** and **litigation outcomes**, and to investigate potential regional disparities or systemic trends.

---

### 📊 What You'll Find in This Dashboard
""")

# Data Story 1 (Coming Soon)
st.subheader("Data Story 1: Grounds for Refusal of Immigration Applications")
st.markdown("""
Based on the dataset:
> *"A34 (1) Refusal Grounds for Temporary and Permanent Resident Applications (2019–2024)"*

This section will explore:
- Countries with the highest number of refusals.
- The **primary grounds for inadmissibility**, such as security concerns or misrepresentation.
- Yearly trends in refusal rates.
""")
st.page_link("a34_story.py", label="👉 Go to Grounds for Refusal of Immigration Applications")

# Data Story 2
st.subheader("Data Story 2: Litigation Outcomes by Region")
st.markdown("""
Based on the dataset:
> *"Litigation Applications by Case Type and Leave Decision (2018–2023)"*

This section analyzes:
- **Regional variation** in allowed, dismissed, and discontinued litigation outcomes.
- Potential **biases** in how litigation decisions are distributed across different regions.
- Key trends by regions (Africa, Asia, North America, Caribbean).
""")
st.page_link("africa_vs_non_africa.py", label="👉 Go to Litigation Outcomes by Region")

# Data Story 3
st.subheader("Data Story 3: Country-Level Case Type & Outcome Analysis")
st.markdown("""
Also using the litigation dataset above, this section dives deeper into:
- The top 4 countries: **Nigeria, India, Iran, and China**.
- A comparative view of case types and outcomes (e.g., RAD, HC, Visa Officer Refusals).
- How litigation pathways differ by country of citizenship.
""")
st.page_link("litigation_dashboard.py", label="👉 Go to Country-Level Case Type & Outcome Analysis")

# Refusals Explorer
st.subheader("Interactive Dashboard: Refusals Explorer")
st.markdown("""
An interactive interface to:
- Explore inadmissibility refusal data from 2019 to 2024.
- Filter by grounds, year, and country of citizenship.
""")
st.page_link("A34_Refused_Data.py", label="👉 Go to A34(1) Inadmissibility Refusal")

# Litigation Explorer
st.subheader("Interactive Dashboard: Litigation Explorer")
st.markdown("""
An interactive tool for:
- Visualizing trends in litigation applications across years.
- Exploring leave decisions, case types and primary decision offices.
""")
st.page_link("litigation_interactive.py", label="👉 Go to Litigation Applications Dashboard")

# Final Note
st.markdown("""
---
###  Navigation
Use the sidebar to move between sections. Each page provides in-depth charts, annotations, and context.
""")