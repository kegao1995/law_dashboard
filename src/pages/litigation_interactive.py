import pandas as pd
import streamlit as st
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import os


path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")

# Load data
df = pd.read_excel(
    path,
    skiprows=5, skipfooter=7
)

st.title("📊 Litigation Cases Dashboard")

# --- Filters in Sidebar (Always visible) ---
st.sidebar.header("🔎 Filter Options")

countries = st.sidebar.multiselect("Select Country", sorted(df["Country of Citizenship"].dropna().unique()))
years = st.sidebar.slider("Select Year Range",
    min_value=int(df["LIT Leave Decision Date - Year"].min()),
    max_value=int(df["LIT Leave Decision Date - Year"].max()),
    value=(2018, 2023)
)
case_types = st.sidebar.multiselect("Select Case Type Group", sorted(df["LIT Case Type Group Desc"].dropna().unique()))

# --- Filter Data ---
filtered_df = df.copy()
if countries:
    filtered_df = filtered_df[filtered_df["Country of Citizenship"].isin(countries)]
if case_types:
    filtered_df = filtered_df[filtered_df["LIT Case Type Group Desc"].isin(case_types)]
filtered_df = filtered_df[
    (filtered_df["LIT Leave Decision Date - Year"] >= years[0]) &
    (filtered_df["LIT Leave Decision Date - Year"] <= years[1])
]

# --- Summary Card (Litigation Count Only, Styled) ---
litigation_total = filtered_df["LIT Litigation Count"].sum()

# Custom CSS to beautify the metric
st.markdown("""
    <style>
    .summary-box {
        background-color: #f9f9fc;
        border-radius: 12px;
        padding: 30px 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .summary-box h2 {
        font-size: 1.5em;
        margin: 0;
        color: #333;
    }
    .summary-box .count {
        font-size: 2.5em;
        font-weight: bold;
        color: #2b8cd6;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="summary-box">
    <h2>Total Litigation Count</h2>
    <div class="count">{litigation_total:,}</div>
</div>
""", unsafe_allow_html=True)


# --- Choropleth Map ---
top_countries = filtered_df.groupby("Country of Citizenship")["LIT Litigation Count"].sum().reset_index()
fig = px.choropleth(top_countries, locations="Country of Citizenship", locationmode="country names",
                    color="LIT Litigation Count", hover_name="Country of Citizenship",
                    color_continuous_scale="Reds", title="🌍 Litigation Count by Country of Citizenship")
fig.update_layout(geo=dict(showframe=False, projection_type='natural earth'))
st.plotly_chart(fig, use_container_width=True)

# --- Custom Composite Visualization for Multiple Countries and Multiple Case Types ---
if len(countries) > 1 and len(case_types) > 1:
    color_palette = px.colors.qualitative.Pastel
    selected_case_types = case_types
    color_map = dict(zip(selected_case_types, color_palette[:len(selected_case_types)]))
    selected_countries = countries

    fig = make_subplots(
        rows=2, cols=len(selected_countries),
        shared_xaxes=False,
        shared_yaxes=True,
        vertical_spacing=0.1,
        horizontal_spacing=0.03,
        subplot_titles=selected_countries,
        row_heights=[0.2, 0.8]
    )

    for col_idx, country in enumerate(selected_countries, start=1):
        df_country = filtered_df[filtered_df["Country of Citizenship"] == country]
        df_country = df_country[df_country["LIT Case Type Group Desc"].isin(selected_case_types)]

        grouped = df_country.groupby(
            ["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"]
        )["LIT Litigation Count"].sum().reset_index()

        pivot_df = grouped.pivot(
            index="LIT Leave Decision Date - Year",
            columns="LIT Case Type Group Desc",
            values="LIT Litigation Count"
        ).fillna(0).sort_index()

        # Row 1: Summary bar (Raw counts instead of percentages)
        total_counts = pivot_df.sum()

        for case_type in selected_case_types:
            fig.add_trace(go.Bar(
                y=["Total"],
                x=[total_counts.get(case_type, 0)],
                name=case_type,
                orientation='h',
                text=[str(int(total_counts.get(case_type, 0)))],
                textposition='outside',
                textfont=dict(color='black'),
                marker=dict(color=color_map[case_type]),
                showlegend=(col_idx == 1)
            ), row=1, col=col_idx)

        # Row 2: Yearly stacked bars
        for case_type in selected_case_types:
            fig.add_trace(go.Bar(
                y=pivot_df.index.astype(str),
                x=pivot_df[case_type],
                name=case_type,
                orientation='h',
                text=pivot_df[case_type],
                textposition='outside',
                textfont=dict(color='black'),
                marker=dict(color=color_map[case_type]),
                showlegend=False
            ), row=2, col=col_idx)

    fig.update_layout(
        height=700,
        title_text="📊 Litigation Trends per Country and Case Type",
        barmode="stack"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.stop()

# --- Yearly Trend (Hide if only 1 year) ---
if years[0] != years[1]:
    if len(countries) > 1:
        yearly = filtered_df.groupby(["LIT Leave Decision Date - Year", "Country of Citizenship"])["LIT Litigation Count"].sum().reset_index()
        fig = px.line(yearly, x="LIT Leave Decision Date - Year", y="LIT Litigation Count",
                      color="Country of Citizenship", markers=True,
                      title="Litigation Trend Over the Years by Country")
    elif len(case_types) > 1:
        yearly = filtered_df.groupby(["LIT Leave Decision Date - Year", "LIT Case Type Group Desc"])["LIT Litigation Count"].sum().reset_index()
        fig = px.line(
            yearly,
            x="LIT Leave Decision Date - Year",
            y="LIT Litigation Count",
            color="LIT Case Type Group Desc",
            markers=True,
            title="Litigation Trend Over the Years by Case Type"
        )
    else:
        yearly = filtered_df.groupby("LIT Leave Decision Date - Year")["LIT Litigation Count"].sum().reset_index()
        fig = px.line(yearly, x="LIT Leave Decision Date - Year", y="LIT Litigation Count",
                      title="Litigation Trend Over the Years", markers=True)

    st.plotly_chart(fig, use_container_width=True)

# --- Treemap: Top 5 Countries per Case Type (If Multiple Case Types & Multiple Countries/None) ---
if len(case_types) > 1 and (len(countries) != 1):
    grouped = (
        filtered_df.groupby(["LIT Case Type Group Desc", "Country of Citizenship"])["LIT Litigation Count"]
        .sum().reset_index()
    )

    # Get top 5 countries per case type
    top5_per_case = grouped.groupby("LIT Case Type Group Desc").apply(
        lambda x: x.nlargest(5, "LIT Litigation Count")
    ).reset_index(drop=True)

    fig = px.treemap(
        top5_per_case,
        path=["LIT Case Type Group Desc", "Country of Citizenship"],
        values="LIT Litigation Count",
        color="Country of Citizenship",
        title="Treemap: Top 5 Countries by Litigation Count within Each Case Type"
    )
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

# --- Fallback to Bar Chart (If case above is not true and len(countries) != 1) ---
elif len(countries) != 1:
    top10 = (
        filtered_df.groupby("Country of Citizenship")["LIT Litigation Count"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    fig = px.bar(top10, y="Country of Citizenship", x="LIT Litigation Count", orientation="h",
                 title="Top 10 Countries by Litigation Count", text_auto=True)
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

# --- Case Type Group (Hide if 1 case type) ---
# --- Case Type Treemap if Multiple Countries Selected ---
if len(countries) > 1 and (len(case_types) != 1):
    case_group = (
        filtered_df.groupby(["Country of Citizenship", "LIT Case Type Group Desc"])["LIT Litigation Count"]
        .sum().reset_index()
    )

    # Keep only top 5 case types by total count
    top_case_types = (
        case_group.groupby("LIT Case Type Group Desc")["LIT Litigation Count"]
        .sum().nlargest(5).index
    )
    case_group = case_group[case_group["LIT Case Type Group Desc"].isin(top_case_types)]

    fig = px.treemap(case_group,
                     path=["Country of Citizenship", "LIT Case Type Group Desc"],
                     values="LIT Litigation Count",
                     color="LIT Case Type Group Desc",
                     title="Treemap of Litigation by Country and Top 5 Case Types")
    fig.update_traces(textinfo="label+value")
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

elif len(case_types) != 1:
    # fallback to original bar chart
    case_group = (
        filtered_df.groupby("LIT Case Type Group Desc")["LIT Litigation Count"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    fig = px.bar(case_group, y="LIT Case Type Group Desc", x="LIT Litigation Count", orientation="h",
                 title="Litigation Count by Case Type Group", text_auto=True)
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)


# --- Regional Group Treemap if Multiple Countries Selected ---
if len(countries) > 1 and (len(case_types) == 1  or not case_types):
    regional_group = (
        filtered_df.groupby(["Country of Citizenship", "LIT Primary Office Regional Group Desc"])["LIT Litigation Count"]
        .sum().reset_index()
    )

    # Keep only top 5 regional groups by total count
    top_regions = (
        regional_group.groupby("LIT Primary Office Regional Group Desc")["LIT Litigation Count"]
        .sum().nlargest(5).index
    )
    regional_group = regional_group[regional_group["LIT Primary Office Regional Group Desc"].isin(top_regions)]

    fig = px.treemap(
        regional_group,
        path=["Country of Citizenship", "LIT Primary Office Regional Group Desc"],
        values="LIT Litigation Count",
        color="LIT Primary Office Regional Group Desc",
        title="Treemap of Litigation by Country and Top 5 Regional Groups"
    )
    fig.update_traces(textinfo="label+value")
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

elif len(case_types) > 1 and (len(countries) == 1  or not countries):
    # Treemap: Top 5 Regional Groups per Case Type
    reg_case_group = (
        filtered_df.groupby(["LIT Case Type Group Desc", "LIT Primary Office Regional Group Desc"])["LIT Litigation Count"]
        .sum().reset_index()
    )

    # Get top 5 regional groups per case type
    top5_regions_per_case = reg_case_group.groupby("LIT Case Type Group Desc").apply(
        lambda x: x.nlargest(5, "LIT Litigation Count")
    ).reset_index(drop=True)

    fig = px.treemap(
        top5_regions_per_case,
        path=["LIT Case Type Group Desc", "LIT Primary Office Regional Group Desc"],
        values="LIT Litigation Count",
        color="LIT Primary Office Regional Group Desc",  # Color per region
        title="Treemap: Top 5 Regional Groups by Litigation Count within Each Case Type"
    )
    fig.update_traces(textinfo="label+value")
    fig.update_layout(height=700)
    st.plotly_chart(fig, use_container_width=True)

else:
    # fallback to original bar chart
    regional_group = (
        filtered_df.groupby("LIT Primary Office Regional Group Desc")["LIT Litigation Count"]
        .sum().sort_values(ascending=False).head(10).reset_index()
    )
    fig = px.bar(regional_group, y="LIT Primary Office Regional Group Desc", x="LIT Litigation Count", orientation="h",
                 title="Litigation Count by Regional Group", text_auto=True)
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)


# --- Leave Decision Visualization (Dynamic Based on Country Selection) ---
if len(countries) > 1 and (len(case_types) == 1  or not case_types):
    # Prepare data for scatter plot (percentage per decision type per country)
    decision_df = (
        filtered_df.groupby(["Country of Citizenship", "LIT Leave Decision Desc"])["LIT Litigation Count"]
        .sum().reset_index()
    )
    # Calculate total per country
    totals = decision_df.groupby("Country of Citizenship")["LIT Litigation Count"].transform("sum")
    decision_df["Percentage"] = (decision_df["LIT Litigation Count"] / totals) * 100

    # Keep only top 5 most frequent decision types overall
    top_decisions = (
        filtered_df.groupby("LIT Leave Decision Desc")["LIT Litigation Count"]
        .sum().nlargest(5).index
    )
    decision_df = decision_df[decision_df["LIT Leave Decision Desc"].isin(top_decisions)]

    # Calculate overall percentage per decision type across all countries
    overall_decision = (
        df.groupby("LIT Leave Decision Desc")["LIT Litigation Count"]
        .sum().reset_index()
    )
    overall_total = overall_decision["LIT Litigation Count"].sum()
    overall_decision["Percentage"] = (overall_decision["LIT Litigation Count"] / overall_total) * 100
    overall_decision = overall_decision[overall_decision["LIT Leave Decision Desc"].isin(top_decisions)]

    # Scatter plot for country-specific points
    fig = px.scatter(
        decision_df,
        x="Percentage",
        y="LIT Leave Decision Desc",
        color="Country of Citizenship",
        title="Decision Type Distribution by Country (as % of Total)",
        hover_data=["LIT Litigation Count"]
    )

    # Add black points for overall percentages per decision type
    fig.add_scatter(
        x=overall_decision["Percentage"],
        y=overall_decision["LIT Leave Decision Desc"],
        mode='markers',
        marker=dict(color='black', size=15, symbol='x'),
        name='Overall Percentage',
        hovertemplate='<b>%{y}</b><br>Overall Percentage: %{x:.2f}%<extra></extra>'
    )

    fig.update_layout(
        yaxis=dict(title="Leave Decision Description"),
        xaxis=dict(title="Percentage (%)"),
        legend_title_text='Country'
    )
    fig.update_traces(marker=dict(size=15))

    st.plotly_chart(fig, use_container_width=True)

elif len(case_types) > 1 and (len(countries) == 1  or not countries):
    # Prepare data for scatter plot (percentage per decision type per case type)
    decision_df = (
        filtered_df.groupby(["LIT Case Type Group Desc", "LIT Leave Decision Desc"])["LIT Litigation Count"]
        .sum().reset_index()
    )
    # Calculate total per case_type
    totals = decision_df.groupby("LIT Case Type Group Desc")["LIT Litigation Count"].transform("sum")
    decision_df["Percentage"] = (decision_df["LIT Litigation Count"] / totals) * 100

    # Keep only top 5 most frequent decision types overall
    top_decisions = (
        filtered_df.groupby("LIT Leave Decision Desc")["LIT Litigation Count"]
        .sum().nlargest(5).index
    )
    decision_df = decision_df[decision_df["LIT Leave Decision Desc"].isin(top_decisions)]

    # Calculate overall percentage per decision type across all countries
    overall_decision = (
        df.groupby("LIT Leave Decision Desc")["LIT Litigation Count"]
        .sum().reset_index()
    )
    overall_total = overall_decision["LIT Litigation Count"].sum()
    overall_decision["Percentage"] = (overall_decision["LIT Litigation Count"] / overall_total) * 100
    overall_decision = overall_decision[overall_decision["LIT Leave Decision Desc"].isin(top_decisions)]

    # Scatter plot for country-specific points
    fig = px.scatter(
        decision_df,
        x="Percentage",
        y="LIT Leave Decision Desc",
        color="LIT Case Type Group Desc",
        title="Decision Type Distribution by Country (as % of Total)",
        hover_data=["LIT Litigation Count"]
    )

    # Add black points for overall percentages per decision type
    fig.add_scatter(
        x=overall_decision["Percentage"],
        y=overall_decision["LIT Leave Decision Desc"],
        mode='markers',
        marker=dict(color='black', size=15, symbol='x'),
        name='Overall Percentage',
        hovertemplate='<b>%{y}</b><br>Overall Percentage: %{x:.2f}%<extra></extra>'
    )

    fig.update_layout(
        yaxis=dict(title="Leave Decision Description"),
        xaxis=dict(title="Percentage (%)"),
        legend_title_text='Case Type'
    )
    fig.update_traces(marker=dict(size=15))

    st.plotly_chart(fig, use_container_width=True)

else:
    # Original donut chart for single country or no selection
    decision_desc = filtered_df.groupby("LIT Leave Decision Desc")["LIT Litigation Count"].sum().nlargest(5).reset_index()
    total = decision_desc["LIT Litigation Count"].sum()
    fig = px.pie(
        decision_desc,
        names="LIT Leave Decision Desc",
        values="LIT Litigation Count",
        title=f"Leave Decision Description Distribution (Total = {total})",
        hole=0.5 
    )
    fig.update_traces(
        textinfo="label+percent+value",
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>"
    )
    st.plotly_chart(fig, use_container_width=True)
