import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Set page layout
st.set_page_config(layout="wide")

# Global color maps
COUNTRY_COLOR_MAP = {
    "India": "#66c2a5",
    "Iran": "#fc8d62",
    "Nigeria": "#8da0cb",
    "People's Republic of China": "#e78ac3"
}

CASE_TYPE_COLOR_MAP = {
    "RAD Decisions": "#66c2a5",
    "Visa Officer Refusal": "#fc8d62",
    "Mandamus": "#8da0cb"
}

# Load data
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")
    lit = pd.read_excel(path, skiprows=5, skipfooter=7)
    lit["Year"] = lit["LIT Leave Decision Date - Year"]

    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Discontinued.*', value='Discontinued', regex=True)
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Dismissed.*', value='Dismissed', regex=True)
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Allowed.*', value='Allowed', regex=True)

    lit = lit[~lit["LIT Leave Decision Desc"].isin(["Not Started at Leave", "No Leave Required", "Leave Exception"])]
    return lit

lit = load_data()


st.set_page_config(layout="wide")

st.markdown('# Country-Level Case Type & Outcome Analysis', unsafe_allow_html=True)

if not lit.empty:
    st.markdown(
        """
        ### Dataset Download
        You can download the Litigation Application Dataset used in this analysis for your own review and further exploration.
        """
    )
    csv_data = lit.to_csv(index=False)
    st.download_button(
        label="Download Litigation Application Dataset (CSV)",
        data=csv_data,
        file_name="litigation_application.csv",
        mime="text/csv"
    )
else:
    st.warning("Dataset is empty, cannot download.")

# ===== Section 1 =====
st.markdown("### Nigeria consistently leads in litigation cases, while India and Iran surged post-2021.")
st.info("""
**How to Read This Graph**  
This vertical bar chart ranks the top 10 countries of citizenship by total number of litigation cases filed in Canadian federal court.  

- The x-axis lists the countries.  
- The y-axis shows the total number of litigation cases over the full dataset time range.  
- Taller bars represent countries with higher overall litigation volumes.
""")

# Top countries by count
top_lit = lit.groupby("Country of Citizenship")[["LIT Litigation Count"]].sum().reset_index()
top_lit = top_lit.sort_values("LIT Litigation Count", ascending=False).head(10)
fig_lit = px.bar(top_lit, x="Country of Citizenship", y="LIT Litigation Count")

fig_lit.update_layout(
    xaxis=dict(
        title=dict(text="Country of Citizenship", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    yaxis=dict(
        title=dict(text="LIT Litigation Count", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    font=dict(color="black")
)

st.plotly_chart(fig_lit, use_container_width=True)

# Total litigation count by year
st.markdown("### **Litigation volume** has stayed high since **2021**, showing persistent legal contestation.")
st.info("""
**How to Read This Graph**  
This line chart shows the total annual number of immigration-related litigation cases in federal court over time.  

- The x-axis represents the year (from 2002 to 2024).  
- The y-axis shows the total number of litigation cases filed that year.  
- Each point on the line corresponds to the total for one year, with numeric labels for precise counts.  
- A rising line indicates an increase in litigation volume; a flat or falling line indicates a decrease.
""")


top_year = lit.groupby("Year")["LIT Litigation Count"].sum()
top_year = top_year[top_year.index.astype(str).str.isnumeric()]
top_year.index = top_year.index.astype(int)

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(x=top_year.index, y=top_year.values, mode='lines+markers', name='Total'))

fig_total.update_layout(
    xaxis=dict(
        title=dict(text="Year", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    yaxis=dict(
        title=dict(text="Total Litigation Count", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    plot_bgcolor='white',
    font=dict(size=16)
)

st.plotly_chart(fig_total, use_container_width=True)

# Litigation trends for top 4 countries
st.markdown("""
### <b><span style='color:#66c2a5'>India</span></b> and <b><span style='color:#fc8d62'>Iran</span></b> show sharp increases after 2020, while <b><span style='color:#8da0cb'>Nigeria</span></b> litigations increase up to 2021 and then decrease
""", unsafe_allow_html=True)
st.markdown("""
- <i><span style='color:#fc8d62'>Iran</span></i> & <i><span style='color:#66c2a5'>India</span></i>: a sharp rise in volume since 2020. 
- <i><span style='color:#8da0cb'>Nigeria</span></i>: consistently high in volume, dropped sharply since 2021. 
- <i><span style='color:#e78ac3'>China</span></i>: relatively stable over the years.
""", unsafe_allow_html=True)

st.info("""
**How to Read This Graph**  
This line chart tracks changes in annual litigation volume for four key countries of citizenship: **Nigeria**, **India**, **Iran**, and **China**, over time.  

- The x-axis shows the year. 
- The y-axis shows the total number of litigation cases filed that year for each country.  
- Each colored line represents one country (color-coded to match legend and text highlights above).  
- Rising slopes indicate years where litigation from that country increased.  
- Falling slopes indicate decline in litigation volume from that country.  
""")


top4 = ["Nigeria", "India", "Iran", "People's Republic of China"]
trend_df = lit[lit["Country of Citizenship"].isin(top4)]
trend_df = trend_df.groupby(["Country of Citizenship", "Year"])["LIT Litigation Count"].sum().reset_index()
fig_trend = px.line(trend_df, x="Year", y="LIT Litigation Count", color="Country of Citizenship", 
                    color_discrete_map=COUNTRY_COLOR_MAP)
fig_trend.update_layout(
    xaxis=dict(
        title=dict(text="Year", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    yaxis=dict(
        title=dict(text="LIT Litigation Count", font=dict(size=16, color="black", weight="bold")),
        tickfont=dict(size=14, color="black", weight="bold")
    ),
    font=dict(size=16)
)

st.plotly_chart(fig_trend, use_container_width=True)


# ===== Section 2 =====
st.markdown("""
### <b><span style='color:{mandamus}'>Mandamus surges</span></b> in China, <b><span style='color:{visa}'>Visa Refusals</span></b> dominate Iran, <b><span style='color:{rad}'>RAD peaks</span></b> in Nigeria.
""".format(
    mandamus=CASE_TYPE_COLOR_MAP["Mandamus"],
    visa=CASE_TYPE_COLOR_MAP["Visa Officer Refusal"],
    rad=CASE_TYPE_COLOR_MAP["RAD Decisions"]
), unsafe_allow_html=True)

st.markdown("""
- **Nigeria** and **India**: Dominated by <span style='color:#66c2a5'><b>RAD Decisions</b></span>. **Nigeria** peaked in 2021, then declined. 
- **Iran**: Driven almost entirely by <span style='color:#fc8d62'><b>Visa Officer Refusal</b></span> cases, peaking near 1,900 in 2023. 
- **China**: Shows a sharp rise in <span style='color:#8da0cb'><b>Mandamus</b></span> applications in 2023 with over 300 cases.
""", unsafe_allow_html=True)

st.info("""
**How to Read This Graph**  
This figure displays annual litigation counts by case type for four countries: China, India, Iran, and Nigeria.

- Each subplot corresponds to one country, labeled above each panel.  
- The y-axis represents years, arranged vertically.  
- The horizontal stacked bars show the total cases in each year, broken down by litigation case type (e.g., Mandamus, Visa Officer Refusal, RAD Decisions).  
- Different colors represent distinct case types, consistent with the legend and text highlights.  
- Hovering over any bar segment reveals the exact number of cases for that case type in that year, along with a brief explanation of the case type.  
""")


valid_case_types = list(CASE_TYPE_COLOR_MAP.keys())
countries = {"People's Republic of China": "China", "India": "India", "Iran": "Iran", "Nigeria": "Nigeria"}

CASE_TYPE_EXPLANATIONS = {
    "Mandamus": "Mandamus: A court order compelling the government to act on delayed immigration applications.",
    "Visa Officer Refusal": "Visa Officer Refusal: Cases challenging visa denials made by immigration officers.",
    "PRRA": "PRRA: Pre-Removal Risk Assessment, assessing risk of harm if removed from Canada.",
    "RAD Decisions": "RAD Decisions: Refugee Appeal Division decisions on refugee status appeals.",
    "RPD Decisions": "RPD Decisions: Refugee Protection Division decisions on refugee claims.",
    "HC Decisions": "HC Decisions: Humanitarian and Compassionate grounds applications for immigration relief."
}


# Create a 1-row, 4-column subplot layout
fig = make_subplots(
    rows=1,
    cols=4,
    shared_yaxes=True,
    subplot_titles=list(countries.values()),
    horizontal_spacing=0.03
)

for col_idx, (country_key, country_name) in enumerate(countries.items(), start=1):
    df_country = lit[(lit["Country of Citizenship"] == country_key) & 
                     (lit["LIT Case Type Group Desc"].isin(valid_case_types))]
    
    grouped = df_country.groupby(["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"])["LIT Litigation Count"].sum().reset_index()
    
    pivot_df = grouped.pivot(index="LIT Leave Decision Date - Year", columns="LIT Case Type Group Desc", 
                              values="LIT Litigation Count").fillna(0).sort_index()

    for case_type in valid_case_types:
        if case_type in pivot_df.columns:
            fig.add_trace(
                go.Bar(
                    x=pivot_df[case_type],
                    y=pivot_df.index,
                    orientation='h',
                    name=case_type,
                    marker_color=CASE_TYPE_COLOR_MAP[case_type],
                    showlegend=False,
                    text=pivot_df[case_type],
                    textposition='auto',
                    hovertemplate=(
                        f"<b>{case_type}</b><br>"
                        f"Year: %{{y}}<br>"
                        f"Cases: %{{x}}<br>"
                        f"{CASE_TYPE_EXPLANATIONS.get(case_type, '')}<extra></extra>"
                    )
                ),
                row=1,
                col=col_idx
            )
            fig.update_yaxes(
            title_font=dict(size=14, color='black', weight='bold'),
            tickfont=dict(size=12, color='black', weight='bold')
        )


# Layout styling
fig.update_layout(
    height=700,
    width=1400,
    barmode='stack',
    plot_bgcolor='white',
    font=dict(size=15),
)

# Remove x-axes
for i in range(1, 5):
    fig.update_xaxes(visible=False, row=1, col=i)

fig.for_each_annotation(lambda a: a.update(text=f"<b>{a.text}</b>", font_size=14))
st.plotly_chart(fig, use_container_width=True)

# ===== Section 3 =====
st.markdown("""
### Majority of <span style='color:#8da0cb'><b>Mandamus</b></span> and <span style='color:#fc8d62'><b>Visa Officer Refusal</b></span> litigation are discontinued, while <span style='color:#66c2a5'><b>RAD Decisions</b></span> are more often <b>dismissed</b>.
""", unsafe_allow_html=True)

st.info("""
**How to Read This Graph**  
This chart illustrates the distribution of litigation leave decisions by case type:

- The vertical axis lists leave decision outcomes (Allowed, Dismissed, Discontinued).  
- The horizontal axis shows the percentage of cases within each case type that received that decision.  
- Each colored marker corresponds to a specific litigation case type, with colors consistent with the legend.  
- Lines connect the minimum and maximum percentages for each decision category across case types, visualizing the range.  
- Hover over a marker to see detailed information including case type, decision, exact percentage, and explanatory notes for both the case type and the decision outcome.
""")


# Step 1: Group by case type and decision
grouped_df = lit.groupby(["LIT Case Type Group Desc", "LIT Leave Decision Desc"])["LIT Litigation Count"].sum().reset_index()

# Step 2: Filter for relevant case types
specific_case_types = list(CASE_TYPE_COLOR_MAP.keys())
filtered_df = grouped_df[grouped_df["LIT Case Type Group Desc"].isin(specific_case_types)]

# Step 3: Calculate percentage of each decision within each case type
filtered_df["Percentage"] = (
    filtered_df.groupby("LIT Case Type Group Desc")["LIT Litigation Count"]
    .transform(lambda x: (x / x.sum()) * 100)
).round(2)

LEAVE_DECISION_EXPLANATIONS = {
    "Allowed": "Leave granted by the court to proceed with judicial review.",
    "Dismissed": "Leave application was heard and dismissed.",
    "Discontinued": "Litigation was withdrawn or discontinued before hearing."
}

# Step 4: Plot dumbbell-style chart with actual percentages and connection lines
fig = go.Figure()

# Iterate by decision type
for decision in filtered_df["LIT Leave Decision Desc"].unique():
    subset = filtered_df[filtered_df["LIT Leave Decision Desc"] == decision]

    # Determine min/max percent to draw a connecting line
    min_percent = subset["Percentage"].min()
    max_percent = subset["Percentage"].max()

    # Draw gray line connecting min and max points
    fig.add_trace(go.Scatter(
        x=[min_percent, max_percent],
        y=[decision, decision],
        mode="lines",
        line=dict(color="lightgray", width=3),
        showlegend=False
    ))

    # Add markers + annotations for each case type's percentage
    for _, row in subset.iterrows():
        case_type = row["LIT Case Type Group Desc"]
        decision_type = row["LIT Leave Decision Desc"]

        fig.add_trace(go.Scatter(
            x=[row["Percentage"]],
            y=[decision_type],
            mode="markers",
            marker=dict(size=18, color=CASE_TYPE_COLOR_MAP[case_type]),
            name=case_type,
            showlegend=False,
            hovertemplate=(
                f"<b>{case_type}</b><br>"
                f"Decision: {decision_type}<br>"
                f"Percentage: {row['Percentage']}%<br>"
                f"{CASE_TYPE_EXPLANATIONS.get(case_type, '')}<br>"
                f"{LEAVE_DECISION_EXPLANATIONS.get(decision_type, '')}<extra></extra>"
            )
        ))

        # Optional: Keep annotation as it is (non-hover)
        fig.add_annotation(
            x=row["Percentage"],
            y=decision_type,
            text=f"{row['Percentage']}%",
            showarrow=False,
            font=dict(size=14, color='white'),
            align='center',
            bgcolor=CASE_TYPE_COLOR_MAP[case_type],
            borderpad=4,
            yshift=12
        )

# Update layout
fig.update_layout(
    xaxis=dict(
        title=dict(text="Percentage within Case Type", font=dict(size=18, color='black', weight='bold')),
        zeroline=False,
        tickfont=dict(size=14, color="black", weight="bold") # Bold tick labels on x-axis
    ),
    yaxis=dict(
        title=dict(text="Leave Decision", font=dict(size=18, color='black', weight='bold')),
        autorange="reversed",
        gridcolor="white",
        tickfont=dict(size=14, color="black", weight="bold") # Bold tick labels on y-axis
    ),
    height=700,
    width=1500,
    plot_bgcolor="white",
    hovermode="closest",
    font=dict(size=18),
    legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center")
)


st.plotly_chart(fig, use_container_width=True)

# ===== Section 4 =====
st.markdown("""
### <b><span style='color:#66c2a5'>India</span></b> and <b><span style='color:#fc8d62'>Iran</span></b> have seen the sharpest rise in <b>dismissed</b> and <b>discontinued</b> cases since 2021.
""", unsafe_allow_html=True)

st.markdown("""
- <b>Allowed</b>: Remain consistently low across all countries. 
- <b>Discontinued</b>: <span style='color:#fc8d62'>Iran</span> shows a steep increase from 2020, peaking in 2023 with nearly 1,000 cases. 
- <b>Dismissed</b>: <span style='color:#66c2a5'>India</span> and <span style='color:#fc8d62'>Iran</span> show sharp increases. 
- <span style='color:#8da0cb'>Nigeria</span> shows a decline since 2021 across all outcome types.
""", unsafe_allow_html=True)

st.info("""
**How to Read This Graph**  
This figure presents trends in litigation leave decision outcomes across four key countries: India, Iran, Nigeria, and China.

- The graph is divided into three panels, each representing a different leave decision outcome: **Allowed**, **Discontinued**, and **Dismissed**.  
- The x-axis in each panel shows the year, allowing observation of trends over time from earliest to latest data.  
- The y-axis shows the total number of litigation cases for the given decision type in that year.  
- Lines represent each country’s annual case counts, with distinct colors corresponding to each country (see legend).  
- Markers highlight yearly data points for clarity.
- Hover over any line or marker to see exact values by year and country.
""")


df_filtered = lit[(lit['LIT Leave Decision Desc'].isin(['Discontinued', 'Dismissed', 'Allowed'])) &
                 (lit['Country of Citizenship'].isin(top4))]
grouped = df_filtered.groupby(['LIT Leave Decision Date - Year', 'Country of Citizenship', 'LIT Leave Decision Desc'])["LIT Litigation Count"].sum().reset_index()

fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=['Allowed', 'Discontinued', 'Dismissed'])

for i, case in enumerate(['Allowed', 'Discontinued', 'Dismissed']):
    for country in top4:
        df_subset = grouped[(grouped['LIT Leave Decision Desc'] == case) &
                            (grouped['Country of Citizenship'] == country)]
        fig.add_trace(go.Scatter(x=df_subset['LIT Leave Decision Date - Year'], y=df_subset['LIT Litigation Count'],
                                 mode='lines+markers', name=country if i == 0 else None, legendgroup=country,
                                 showlegend=(i == 0), line=dict(color=COUNTRY_COLOR_MAP[country])),
                      row=1, col=i+1)
    
    # Bold x-axis title and ticks
    fig.update_xaxes(
        title=dict(text="Year", font=dict(size=16, color="black", weight="bold")),
        title_font=dict(size=16),
        tickfont=dict(size=14, color="black", weight="bold"),
        row=1,
        col=i+1
    )
    
    # Bold y-axis title and ticks (only for the first subplot)
    if i == 0:
        fig.update_yaxes(
            title=dict(text="Total Litigation Count", font=dict(size=16, color="black", weight="bold")),
            title_font=dict(size=16),
            tickfont=dict(size=14, color="black", weight="bold"),
            row=1,
            col=i+1
        )

fig.update_layout(
    height=500,
    width=1200,
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)