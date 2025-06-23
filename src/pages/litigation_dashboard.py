import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import os
# Load data

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")
    lit = pd.read_excel(path, sheet_name="Final", skiprows=5)
    lit["Year"] = lit["LIT Leave Decision Date - Year"]

    # Standardizing Leave decision
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Discontinued.*', value='Discontinued', regex=True
    )
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Dismissed.*', value='Dismissed', regex=True
    )
    lit['LIT Leave Decision Desc'] = lit['LIT Leave Decision Desc'].replace(
        to_replace=r'^Allowed.*', value='Allowed', regex=True
    )

    # Filter out irrelevant decision types
    lit = lit[~lit["LIT Leave Decision Desc"].isin(["Not Started at Leave", "No Leave Required", "Leave Exception"])]

    return lit

lit = load_data()

st.set_page_config(layout="wide")
st.title("Litigation Case Dashboard")

# ===== Section 1 =====
st.header("Overview of Top Countries and Litigation Trends")

# Litigation Top Countries
top_lit = lit.groupby("Country of Citizenship")["LIT Litigation Count"].sum().reset_index()
top_lit = top_lit.sort_values("LIT Litigation Count", ascending=False).head(10)
fig_lit = px.bar(top_lit, x="Country of Citizenship", y="LIT Litigation Count", title="Top 10 Countries by Litigation Count")
st.plotly_chart(fig_lit, use_container_width=True)

# Total Litigation Count by Year
top_year = lit.groupby("Year")["LIT Litigation Count"].sum()
top_year = top_year[top_year.index.astype(str).str.isnumeric()]
top_year.index = top_year.index.astype(int)

fig_total = go.Figure()
fig_total.add_trace(go.Scatter(x=top_year.index, y=top_year.values, mode='lines+markers', name='Total'))

for i, value in enumerate(top_year.values):
    fig_total.add_annotation(
        x=top_year.index[i],
        y=value,
        text=f"{int(value)}",
        showarrow=False,
        yshift=10
    )

fig_total.update_layout(
    title="Total Litigation Count by Year",
    xaxis_title="Year",
    yaxis_title="Total Litigation Count",
    plot_bgcolor='white',
    font=dict(size=16)
)
st.plotly_chart(fig_total, use_container_width=True)

# Litigation Trends Over Time for Top 4 Countries
top4 = ["Nigeria", "India", "Iran", "People's Republic of China"]
trend_df = lit[lit["Country of Citizenship"].isin(top4)]
trend_df = trend_df.groupby(["Country of Citizenship", "Year"])["LIT Litigation Count"].sum().reset_index()
fig_trend = px.line(trend_df, x="Year", y="LIT Litigation Count", color="Country of Citizenship", title="Litigation Trends (2018–2023)")
st.plotly_chart(fig_trend, use_container_width=True)

# ===== Section 2 =====
# ===== Litigation Case Types Over Time by Country =====
st.header("Case Type Breakdown Over Time for Top 4 Countries")

countries = {
    "People's Republic of China": "China",
    "India": "India",
    "Iran": "Iran",
    "Nigeria": "Nigeria"
}
valid_case_types = ["RAD Decisions", "Visa Officer Refusal", "Mandamus"]

color_palette = px.colors.qualitative.Pastel
color_map = dict(zip(valid_case_types, color_palette[:len(valid_case_types)]))

fig = make_subplots(
    rows=2, cols=4,
    shared_xaxes=False,
    shared_yaxes=True,
    vertical_spacing=0.1,
    horizontal_spacing=0.03,
    subplot_titles=list(countries.values()),
    row_heights=[0.2, 0.8]
)

for col_idx, (country_key, country_name) in enumerate(countries.items(), start=1):
    df_country = lit[lit["Country of Citizenship"] == country_key]
    df_country = df_country[df_country["LIT Case Type Group Desc"].isin(valid_case_types)]

    grouped = df_country.groupby(
        ["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"]
    )["LIT Litigation Count"].sum().reset_index()

    pivot_df = grouped.pivot(
        index="LIT Leave Decision Date - Year",
        columns="LIT Case Type Group Desc",
        values="LIT Litigation Count"
    ).fillna(0).sort_index()

    total_counts = pivot_df.sum()
    total_percent = (total_counts / total_counts.sum() * 100).round(2)


    for case_type in valid_case_types:
        fig.add_trace(
            go.Bar(
                x=pivot_df[case_type].astype(str),
                y=pivot_df.index,
                orientation="h",
                name=case_type,
                text=pivot_df[case_type],
                textposition="outside",
                marker_color=color_map[case_type],
                showlegend=False
            ), row=2, col=col_idx
        )


fig.update_layout(
    height=800,
    width=1200,
    barmode="stack",
    plot_bgcolor="white",
    title_text="Case Type Breakdown Over Time (2018–2023)",
    font=dict(size=14),
    legend_title_text="Case Types"
)

st.plotly_chart(fig, use_container_width=True)

# ===== Section 3 =====
st.header("Decision Type by Country Dumbbell Chart")

# Country-level percentages
country_grouped = lit[lit["Country of Citizenship"].isin(top4)].groupby(
    ["Country of Citizenship", "LIT Leave Decision Desc"]
)["LIT Litigation Count"].sum().reset_index()
total_by_country = country_grouped.groupby("Country of Citizenship")["LIT Litigation Count"].transform("sum")
country_grouped["Percentage"] = country_grouped["LIT Litigation Count"] / total_by_country * 100

# Global percentages based on ALL data
global_grouped = lit.groupby("LIT Leave Decision Desc")["LIT Litigation Count"].sum().reset_index()
global_grouped["Total_Percentage"] = global_grouped["LIT Litigation Count"] / global_grouped["LIT Litigation Count"].sum() * 100

# Merge and compute difference
merged = pd.merge(
    country_grouped[["Country of Citizenship", "LIT Leave Decision Desc", "Percentage"]],
    global_grouped[["LIT Leave Decision Desc", "Total_Percentage"]],
    on="LIT Leave Decision Desc"
)
merged["Difference"] = merged["Percentage"] - merged["Total_Percentage"]

fig = go.Figure()

# Show legend only for countries that appear in 'Dismissed'
dismissed_countries = set(merged[merged['LIT Leave Decision Desc'] == 'Dismissed']['Country of Citizenship'])

# Color map
unique_countries = merged['Country of Citizenship'].unique()
color_map = {country: f"hsl({i * 60 % 360}, 70%, 50%)" for i, country in enumerate(unique_countries)}

for decision in merged['LIT Leave Decision Desc'].unique():
    subset = merged[merged['LIT Leave Decision Desc'] == decision]

    for i, (_, row) in enumerate(subset.iterrows()):
        fig.add_trace(go.Scatter(
            x=[0, row['Difference']],
            y=[decision, decision],
            mode='lines',
            line=dict(color='gray', width=2),
            showlegend=False
        ))

        show_legend_label = (row['Country of Citizenship'] in dismissed_countries) and (decision == 'Dismissed')

        fig.add_trace(go.Scatter(
            x=[row['Difference']],
            y=[decision],
            mode='markers',
            marker=dict(size=16, color=color_map[row['Country of Citizenship']], symbol='circle'),
            showlegend=show_legend_label,
            name=row['Country of Citizenship'],
            hovertemplate=(
                f"{row['Country of Citizenship']}<br>"
                f"Decision: {decision}<br>"
                f"Difference: {row['Difference']:.2f}%<extra></extra>"
            )
        ))

        fig.add_annotation(
            x=row['Difference'],
            y=decision,
            text=f"{row['Difference']:.2f}%",
            showarrow=False,
            font=dict(size=14, color='white'),
            align='center',
            bgcolor=color_map[row['Country of Citizenship']],
            borderpad=4,
            yshift=12 if i % 2 == 0 else -12
        )

fig.update_layout(
    xaxis=dict(title="Difference in Percentage (country % - total %)", zeroline=True),
    yaxis=dict(title="Leave Decision", autorange='reversed', gridcolor='white'),
    height=800,
    width=1500,
    plot_bgcolor='white',
    font=dict(family='Arial, sans-serif', size=20),
    hovermode="closest",
    legend=dict(
        orientation="h",
        y=-0.3,
        x=0.5,
        xanchor="center",
        bordercolor="white",
        borderwidth=1,
        itemclick="toggle",
        itemdoubleclick="toggleothers"
    )
)
st.plotly_chart(fig, use_container_width=True)

# ===== Section 4 =====
st.header("Decision Group Trends")

nonk_df = lit.copy()
df_filtered = nonk_df[
    nonk_df['LIT Leave Decision Desc'].isin(['Discontinued', 'Dismissed', 'Allowed']) &
    nonk_df['Country of Citizenship'].isin(top4)
]

# Group by year, country, and decision group
grouped = (
    df_filtered
    .groupby(['LIT Leave Decision Date - Year', 'Country of Citizenship', 'LIT Leave Decision Desc'])['LIT Litigation Count']
    .sum()
    .reset_index()
)

fig = make_subplots(rows=1, cols=3, shared_yaxes=True, subplot_titles=['Allowed', 'Discontinued', 'Dismissed'])

# Define consistent color map for countries
color_map = {
    "India": "#1f77b4",
    "Iran": "#aec7e8",
    "Nigeria": "#d62728",
    "People's Republic of China": "#ff9896"
}

for i, case in enumerate(['Allowed', 'Discontinued', 'Dismissed']):
    for country in top4:
        df_subset = grouped[(grouped['LIT Leave Decision Desc'] == case) & (grouped['Country of Citizenship'] == country)]
        fig.add_trace(
            go.Scatter(
                x=df_subset['LIT Leave Decision Date - Year'],
                y=df_subset['LIT Litigation Count'],
                mode='lines+markers',
                name=country if i == 0 else None,
                legendgroup=country,
                showlegend=(i == 0),
                line=dict(color=color_map[country])
            ), row=1, col=i+1
        )

    fig.update_xaxes(title_text="Year", row=1, col=i+1)
    if i == 0:
        fig.update_yaxes(title_text="Total Litigation Count", row=1, col=i+1)

fig.update_layout(height=500, width=1200, title_text="Decision Group Trends", showlegend=True)
st.plotly_chart(fig, use_container_width=True)
