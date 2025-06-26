import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.colors import qualitative
import os

st.set_page_config(layout="wide")
st.title(" Grounds for Refusal of Immigration Applications")
st.info("""⚠️ *Note: Due to the small refusal counts in general, strong conclusions should be avoided.*
""")
@st.cache_data
def load_data():
    """Load and cache the CSV data"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "a34_1_refused_cleaned.csv")
    try:
        df = pd.read_csv(data_path)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at: {data_path}")
        return pd.DataFrame()

# Load data
ref = load_data()

# Load data
ref = load_data()

# Load data
ref = load_data()

if not ref.empty:
    st.markdown(
        """
        ### Dataset Download
        You can download the A34(1) Refusal Dataset used in this analysis for your own review and further exploration.
        """
    )
    csv_data = ref.to_csv(index=False)
    st.download_button(
        label="Download Refusal Dataset (CSV)",
        data=csv_data,
        file_name="a34_1_refusal.csv",
        mime="text/csv"
    )
else:
    st.warning("Dataset is empty, cannot download.")



# --- Top 10 Countries by Total Refusals ---

st.header("Top 10 Countries by Total Refusals")
st.markdown("""
**Ukraine** (176) and **Syria** (101) lead the list
""")

st.info("""
        **How to Read This Chart**:
        
        - This bar chart displays the total number of immigration refusal cases categorized by country. 
        - The height of each bar represents the cumulative refusals for that country over the entire period analyzed. 
        - This helps identify countries with the highest refusal counts.
""")

country_counts = ref.groupby("country")["count"].sum().nlargest(10).reset_index()
fig1 = px.bar(
    country_counts,
    x="country",
    y="count",
    text_auto=True
)

fig1.update_layout(
    yaxis_title="Number of Refusals",
    xaxis_title="Country",
    xaxis_tickfont=dict(size=12, color='black', weight='bold'),
    yaxis_tickfont=dict(size=12, color='black', weight='bold'),
    xaxis_title_font=dict(size=14, color='black', weight='bold'),
    yaxis_title_font=dict(size=14, color='black', weight='bold')
)

st.plotly_chart(fig1, use_container_width=True)

# --- Heatmap: Yearly Trends for Top 5 Countries ---
st.header("Yearly Refusal Trends (Top 5 Countries)")
st.markdown("""
**Observations**:
- **Ukraine** had a large spike in **2024** with **131** refusals.
- **Syria** led in **2019** and **2022**.
- **Iran** has steady refusals across multiple years.
""")

st.info("""
        **How to Read This Heatmap**:

        - This heatmap shows yearly refusal counts for the top five countries with the most refusals. 
        - Each cell’s color intensity corresponds to the number of refusals in that year for the respective country, allowing you to observe trends and spikes over time.
""")


top_countries = country_counts.head(5)['country'].tolist()
df_top = ref[ref['country'].isin(top_countries)]
heatmap_data = df_top.pivot_table(index='country', columns='year', values='count', aggfunc='sum', fill_value=0)
fig2 = px.imshow(
    heatmap_data,
    text_auto=True,
    color_continuous_scale='Blues',
    labels=dict(x="Year", y="Country", color="Refusals")
)

# Bold the axis tick labels
fig2.update_layout(
    xaxis_tickfont=dict(size=12, color='black', weight='bold'),
    yaxis_tickfont=dict(size=12, color='black', weight='bold'),
    xaxis_title_font=dict(size=14, color='black', weight='bold'),
    yaxis_title_font=dict(size=14, color='black', weight='bold')
)



st.plotly_chart(fig2, use_container_width=True)


# --- Treemap: Grounds for Refusal ---
st.header("Refusal Breakdown by Inadmissibility Grounds")

# Map countries to colors
country_color_map = {
    "Ukraine": "#66c2a5",
    "Bangladesh": "#fc8d62",
    "Iran": "#8da0cb",
    "Syria": "#e78ac3",
    "China": "#a6d854"
}

st.markdown(f"""
**Breakdown of Grounds**:
- <span style="color:{country_color_map['Ukraine']};"><strong>Ukraine</strong></span> and <span style="color:{country_color_map['Bangladesh']};"><strong>Bangladesh</strong></span>: Mostly A34(1)(f) (around 80–90%).
- <span style="color:{country_color_map['Iran']};"><strong>Iran</strong></span> and <span style="color:{country_color_map['Syria']};"><strong>Syria</strong></span>: Refusals spread across multiple clauses (f, d, b, c).
- <span style="color:{country_color_map['China']};"><strong>China</strong></span>: Primarily A34(1)(f) with some under (a) and (c).

These patterns may suggest different risk categorizations per country, but more data would be needed to confirm.
""", unsafe_allow_html=True)

grounds_description = {
    "A34(1)(a)": "Espionage against Canada or contrary to Canada’s interests",
    "A34(1)(b)": "Subversion by force of any government",
    "A34(1)(b.1)": "Subversion against a democratic government, institution, or process (as understood in Canada)",
    "A34(1)(c)": "Engaging in terrorism",
    "A34(1)(d)": "Being a danger to the security of Canada",
    "A34(1)(e)": "Acts of violence endangering lives or safety of persons in Canada",
    "A34(1)(f)": "Membership in an organization engaged in espionage, subversion, or terrorism"
}

st.info("""
        **How to Read This Treemap**:

        - The treemap visualizes the distribution of refusal cases by country for the top 5 countries and specific legal grounds for refusal under section A34(1). 
        - The size of each rectangle reflects the volume of refusals, while color differentiates countries. 
        - Hover over sections for detailed descriptions of refusal grounds.
""")

# Add descriptions for hover tooltips
df_top["grounds_description"] = df_top["inadmissibility_grounds"].map(grounds_description)

fig3 = px.treemap(
    df_top,
    path=["country", "inadmissibility_grounds"],
    values="count",
    hover_data={
        "count": True,
        "grounds_description": True
    },
    color="country",
    color_discrete_map=country_color_map
)

fig3.update_traces(
    textinfo="label+value",
    textfont=dict(size=12, family='Arial', color='black')
)

fig3.update_layout(
    uniformtext=dict(minsize=12),
    width=1400,
    height=800
)

st.plotly_chart(fig3, use_container_width=True)



st.info("""
**⚠️ Disclaimer:** Refusal numbers under A34(1) are quite low overall. While some patterns emerge, these are not sufficient for conclusive inferences. More contextual data, like total applications or approval rates, is essential for robust analysis.
""")