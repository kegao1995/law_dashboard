import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Title
st.title("A34 (1) Inadmissibility Refusal Dashboard")

# Load data
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
df = load_data()

if df.empty:
    st.stop()

# Create donut chart function

def create_resident_donut_chart(data, title_suffix=""):
    """Create a donut chart comparing Permanent vs Temporary residents with counts"""
    # Group by resident status and calculate totals
    resident_data = data.groupby('resident')['count'].sum().reset_index()

    if len(resident_data) < 2:
        st.warning("⚠️ Insufficient data for resident comparison chart.")
        return None

    # Extract labels and values
    labels = resident_data['resident']
    values = resident_data['count']

    # Combine label and count for display
    custom_labels = [f"{label}: {value:,}" for label, value in zip(labels, values)]

    # Create donut chart
    fig_donut = go.Figure(data=[go.Pie(
        labels=custom_labels,
        values=values,
        hole=0.5,
        textinfo='label+percent',
        hovertemplate='%{label}<br>Refusals: %{value:,}<extra></extra>'
    )])

    # Layout customization
    fig_donut.update_layout(
        title_text=f'Permanent vs Temporary Residents{title_suffix}',
        showlegend=True,
        height=400,
        margin=dict(l=50, r=50, t=80, b=50)
    )

    return fig_donut

# ----------------------
# Filters on main page
# ----------------------
st.sidebar.header("🔎 Filter Options")


# Get unique values for each column
countries = sorted(df['country'].unique())
years = sorted(df['year'].unique())
inadmissibility_grounds = sorted(df['inadmissibility_grounds'].unique())

# --- Set filter defaults if not cleared ---
if "clear_filters" not in st.session_state:
    st.session_state.clear_filters = False

# Reset values only once when "Clear All Filters" is pressed
if st.session_state.clear_filters:
    st.session_state.selected_country = None
    st.session_state.selected_years = (years[0], years[-1])
    st.session_state.selected_inadmissibility = None
    st.session_state.clear_filters = False
    st.rerun()  # Immediately rerun after reset

# Validate current session state values
if "selected_country" not in st.session_state or st.session_state.selected_country not in countries:
    st.session_state.selected_country = None

if "selected_years" not in st.session_state:
    st.session_state.selected_years = (years[0], years[-1])

if "selected_inadmissibility" not in st.session_state or st.session_state.selected_inadmissibility not in inadmissibility_grounds:
    st.session_state.selected_inadmissibility = None

# --- Sidebar Filters (rely only on session_state) ---
selected_country = st.sidebar.selectbox(
    "Select Country:",
    options=countries,
    index=0 if st.session_state.selected_country is None else (countries.index(st.session_state.selected_country)),
    key="selected_country"
)

selected_years = st.sidebar.slider(
    "Select Year Range:",
    min_value=min(years),
    max_value=max(years),
    value=st.session_state.selected_years,
    step=1,
    key="selected_years"
)

selected_inadmissibility = st.sidebar.selectbox(
    "Select Inadmissibility Ground:",
    options=inadmissibility_grounds,
    index=0 if st.session_state.selected_inadmissibility is None else (inadmissibility_grounds.index(st.session_state.selected_inadmissibility)),
    key="selected_inadmissibility"
)


# --- Clear Filters Button ---
if st.sidebar.button("🗑️ Clear All Filters"):
    st.session_state.clear_filters = True
    st.rerun()

# --- Filtering Logic ---
mask = pd.Series([True] * len(df))

if selected_country is not None:
    mask &= df["country"] == selected_country

if selected_inadmissibility is not None:
    mask &= df["inadmissibility_grounds"] == selected_inadmissibility

if selected_years is not None:
    mask &= df["year"].between(selected_years[0], selected_years[1])

filtered_df = df[mask]

# Main dashboard
if filtered_df['count'].sum() == 0:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()

# --- Summary Metrics ---
total_cases = filtered_df['count'].sum()
year_range = f"{selected_years[0]} - {selected_years[1]}"
selected_country_names = "".join(selected_country) if selected_country else "All Countries"

st.markdown("""
    <style>
    .summary-container {
        display: flex;
        justify-content: space-around;
        gap: 20px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }
    .summary-box {
        background-color: #f9f9fc;
        border-radius: 12px;
        padding: 30px 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
        flex: 1;
        min-width: 250px;
    }
    .summary-box h2 {
        font-size: 1.3em;
        margin: 0;
        color: #333;
    }
    .summary-box .count {
        font-size: 2.2em;
        font-weight: bold;
        color: #2b8cd6;
        margin-top: 10px;
    }
    .summary-box .label {
        font-size: 1em;
        color: #555;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Display the Summary Metrics ---
st.markdown(f"""
<div class="summary-container">
    <div class="summary-box">
        <h2>Total Cases</h2>
        <div class="count">{total_cases:,}</div>
    </div>
    <div class="summary-box">
        <h2>Selected Year Range</h2>
        <div class="count">{year_range}</div>
    </div>
    <div class="summary-box">
        <h2>Countries Selected</h2>
        <div class="count">{selected_country_names}</div>
    </div>
</div>
""", unsafe_allow_html=True)


# Check if no filters are selected to show default charts
no_filters_selected = no_filters_selected = (
    selected_country is None and
    selected_inadmissibility is None and
    selected_years == (years[0], years[-1])
)

if no_filters_selected:

    col1, col2 = st.columns(2)
    
    with col1:
        # Total Refusals by Inadmissibility Grounds
        inadmiss_data = df.groupby('inadmissibility_grounds')['count'].sum().reset_index()
        inadmiss_data = inadmiss_data.sort_values('count', ascending=False)
        
        fig_inadmiss = px.bar(
            inadmiss_data,
            x='inadmissibility_grounds',
            y='count',
            title='Total Refusals by Inadmissibility Grounds'
        )
        fig_inadmiss.update_layout(
            xaxis_title="Inadmissibility Grounds",
            yaxis_title="Count",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_inadmiss, use_container_width=True)
    
    with col2:
        # Top 10 Countries by Total Refusals
        country_counts = df.groupby('country')['count'].sum().sort_values(ascending=False).head(10).reset_index()
        
        fig_countries = px.bar(
            country_counts,
            x='country',
            y='count',
            title='Top 10 Countries by Total Refusals'
        )
        fig_countries.update_layout(
            xaxis_title="Country",
            yaxis_title="Count",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_countries, use_container_width=True)
    
    # Total Refusals Per Year
    yearly_totals = df.groupby('year')['count'].sum().reset_index()
    
    fig_yearly = px.line(
        yearly_totals,
        x='year',
        y='count',
        title='Total Refusals Per Year',
        markers=True,
        line_shape='spline'
    )
    fig_yearly.update_layout(
        xaxis_title="Year",
        yaxis_title="Count"
    )
    st.plotly_chart(fig_yearly, use_container_width=True)
    
    # Refusal Trends Over Time by Inadmissibility Types
    yearly_inadmiss = df.groupby(['year', 'inadmissibility_grounds'])['count'].sum().reset_index()
    
    fig_trends = px.line(
        yearly_inadmiss,
        x='year',
        y='count',
        color='inadmissibility_grounds',
        title='Refusal Trends Over Time by Inadmissibility Types',
        markers=True
    )
    fig_trends.update_layout(        xaxis_title="Year",
        yaxis_title="Number of Refusals",
        legend_title="Inadmissibility Type"
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Donut Chart for Resident Status
    
    # Create and display Donut Chart for all data
    slope_fig = create_resident_donut_chart(df, " - All Data")
    if slope_fig:
        st.plotly_chart(slope_fig, use_container_width=True)

else:
    # Filtered visualizations - dynamic based on selected filters
    start_year, end_year = selected_years
    single_year_selected = start_year == end_year
    year_range_selected = start_year != years[0] or end_year != years[-1] and start_year != end_year
    country_selected = selected_country is not None
    inadmissibility_selected = selected_inadmissibility is not None
    
    # Case 1: All three main filters selected (year, country, inadmissibility)
    if single_year_selected and country_selected and inadmissibility_selected:
        total_refusals = filtered_df['count'].sum()
        
        if total_refusals > 0:
            
            # Add donut chart for this filtered data
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_country} in {selected_years[0]}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
        else:
            st.warning("No refusals found matching your criteria.")

      # Case 2: Year and Country selected (show inadmissibility grounds)
    elif single_year_selected and country_selected and not inadmissibility_selected:
        st.subheader("Analysis for Selected Year and Country")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Inadmissibility grounds bar chart
            inadmiss_data = filtered_df.groupby('inadmissibility_grounds')['count'].sum().reset_index()
            inadmiss_data = inadmiss_data.sort_values('count', ascending=False)
            
            if not inadmiss_data.empty:
                fig_inadmiss = px.bar(
                    inadmiss_data,
                    x='inadmissibility_grounds',
                    y='count',
                    title=f'Inadmissibility Grounds for {selected_country} in {selected_years[0]}'
                )
                fig_inadmiss.update_layout(
                    xaxis_title="Inadmissibility Grounds",
                    yaxis_title="Number of Refusals",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_inadmiss, use_container_width=True)
        
        with col2: 
            # Add donut chart for resident comparison
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_country} in {selected_years[0]}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)

      # Case 3: Year and Inadmissibility selected (show top countries)
    elif single_year_selected and inadmissibility_selected and not country_selected:
        st.subheader("Analysis for Selected Year and Inadmissibility Ground")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top countries bar chart
            country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False)
            top_countries = country_data.head(10)
            
            if not top_countries.empty:
                fig_countries = px.bar(
                    top_countries,
                    x='country',
                    y='count',
                    title=f'Top 10 Countries for {selected_inadmissibility} in {selected_years[0]}',
                )
                fig_countries.update_layout(
                    xaxis_title="Country",
                    yaxis_title="Number of Refusals",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_countries, use_container_width=True)
        
        with col2:
            # Add donut chart for resident comparison
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_inadmissibility} in {selected_years[0]}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 4: Country and Inadmissibility selected (show yearly trends)
    elif country_selected and inadmissibility_selected and not single_year_selected:
        st.subheader("Analysis for Selected Country and Inadmissibility Ground")
        
        yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
        
        if not yearly_data.empty:
            fig_yearly = px.line(
                yearly_data,
                x='year',                
                 y='count',
                title=f'Refusals Over Time: {selected_country} - {selected_inadmissibility}',
                markers=True,
                line_shape='spline'
            )
            fig_yearly.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Refusals"
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
            
            # Add donut chart for resident comparison
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_country} - {selected_inadmissibility}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 5: Only Year selected (show treemap for top countries with inadmissibility grounds)
    elif single_year_selected and not country_selected and not inadmissibility_selected:
        st.subheader(f"Analysis for {selected_years[0]}")
        
        # Get top 5 countries for the selected year
        top_countries_data = filtered_df.groupby('country')['count'].sum().sort_values(ascending=False).head(5)
        treemap_data = filtered_df[filtered_df['country'].isin(top_countries_data.index)]
        
        if not treemap_data.empty and treemap_data['count'].sum() > 0:
            fig_treemap = px.treemap(
                treemap_data,
                path=["country", "inadmissibility_grounds"],
                values="count",
                title=f"Top 5 Countries and Inadmissibility Grounds for {selected_years[0]}",
                color="inadmissibility_grounds",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry",
                                      textfont=dict(color="black"))
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
            
            # Add donut chart for resident comparison
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_years[0]}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)

      # Case 6: Only Country selected (show multiple analysis)
    elif country_selected and not single_year_selected and not inadmissibility_selected:
        st.subheader(f"Analysis for {selected_country}")
        
        col1, col2 = st.columns(2)
        
        with col1:            # Time series for the selected country
            yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
            
            if not yearly_data.empty:
                fig_yearly = px.line(
                    yearly_data,
                    x='year',
                    y='count',
                    title=f'Refusals Over Time for {selected_country}',
                    markers=True,
                    line_shape='spline'
                )
                fig_yearly.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Refusals"
                )
                st.plotly_chart(fig_yearly, use_container_width=True)
        
        with col2:
            # Time series by inadmissibility grounds
            yearly_inadmiss = filtered_df.groupby(['year', 'inadmissibility_grounds'])['count'].sum().reset_index()
            
            if not yearly_inadmiss.empty:
                fig_trends = px.line(
                    yearly_inadmiss,
                    x='year',
                    y='count',
                    color='inadmissibility_grounds',
                    title=f'Inadmissibility Trends for {selected_country}',
                    markers=True
                )
                fig_trends.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Refusals",
                    legend_title="Inadmissibility Type"
                )
                st.plotly_chart(fig_trends, use_container_width=True)
        
        # Treemap with different colors for inadmissibility grounds
        if not filtered_df.empty and filtered_df['count'].sum() > 0:
            fig_treemap = px.treemap(
                filtered_df,
                path=["country", "inadmissibility_grounds"],
                values="count",
                title=f"Inadmissibility Grounds for {selected_country}",
                color="inadmissibility_grounds",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry",
                                      textfont=dict(color="black"))
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
          # Add donut chart for resident comparison
        slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_country}")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)

      # Case 7: Only Inadmissibility selected (show comprehensive analysis)
    elif inadmissibility_selected and not single_year_selected and not country_selected:
        st.subheader(f"Analysis for {selected_inadmissibility}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Time series for the selected inadmissibility ground
            yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
            
            if not yearly_data.empty:
                fig_yearly = px.line(
                    yearly_data,
                    x='year',
                    y='count',
                    title=f'{selected_inadmissibility} Over Time',
                    markers=True,
                    line_shape='spline'
                )
                fig_yearly.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Refusals"
                )
                st.plotly_chart(fig_yearly, use_container_width=True)
        
        with col2:
            # Top countries bar chart
            country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False)
            top_countries = country_data.head(10)
            
            if not top_countries.empty:
                fig_countries = px.bar(
                    top_countries,
                    x='country',
                    y='count',
                    title=f'Top 10 Countries for {selected_inadmissibility}'
                )
                fig_countries.update_layout(
                    xaxis_title="Country",
                    yaxis_title="Number of Refusals",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_countries, use_container_width=True)
        
        # Refusal trends over time by country
        yearly_country_data = filtered_df.groupby(['year', 'country'])['count'].sum().reset_index()
        # Get top 10 countries for this inadmissibility ground
        top_countries_for_ground = filtered_df.groupby('country')['count'].sum().sort_values(ascending=False).head(10).index
        yearly_country_filtered = yearly_country_data[yearly_country_data['country'].isin(top_countries_for_ground)]
        
        if not yearly_country_filtered.empty:            
            fig_trends = px.line(
                yearly_country_filtered,
                x='year',
                y='count',
                color='country',
                title=f'Refusal Trends Over Time by Country for {selected_inadmissibility}',
                markers=True
            )
            fig_trends.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Refusals",
                legend_title="Country"
            )
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # Add donut chart for resident comparison
            slope_fig = create_resident_donut_chart(filtered_df, f" - {selected_inadmissibility}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 8: Only Resident selected or other combinations
    else:
        st.subheader("General Analysis")
        
        # Show a few key charts based on available data
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart by most relevant dimension            if not country_selected:
                country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False).head(10)
                if not country_data.empty:
                    fig_bar = px.bar(
                        country_data,
                        x='country',
                        y='count',
                        title='Top 10 Countries'
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Yearly trend if not year selected
            if not single_year_selected:
                yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
                if not yearly_data.empty:                    
                    fig_yearly = px.line(
                        yearly_data,
                        x='year',
                        y='count',
                        title='Yearly Trends',
                        markers=True
                    )
                    st.plotly_chart(fig_yearly, use_container_width=True)
        
        # Add donut chart for resident comparison
        slope_fig = create_resident_donut_chart(filtered_df, " - General Analysis")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)