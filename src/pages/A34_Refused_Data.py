import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# Title
st.title("🍁 A34 Inadmissibility Refused Data Dashboard")
st.markdown("---")

# Load data
@st.cache_data
def load_data():
    """Load and cache the CSV data"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "a34_1_refused_cleaned.csv")
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

# ----------------------
# Filters on main page
# ----------------------
st.header("🔍 Data Filters")

col_f1, col_f2, col_f3, col_f4, col_f5 = st.columns([1,1,1,1,1])

with col_f5:
    if st.button("🗑️ Clear All Filters"):
        st.rerun()

# Get unique values for each column
countries = sorted(df['country'].unique())
years = sorted(df['year'].unique())
inadmissibility_grounds = sorted(df['inadmissibility_grounds'].unique())
residents = sorted(df['resident'].unique())

with col_f1:
    selected_countries = st.multiselect(
        "Select Countries:",
        options=countries,
        default=[],
        help="Choose one or more countries to analyze (leave empty to show all)"
    )
with col_f2:
    selected_years = st.multiselect(
        "Select Years:",
        options=years,
        default=[],
        help="Choose one or more years to analyze (leave empty to show all)"
    )
with col_f3:
    selected_inadmissibility = st.multiselect(
        "Select Inadmissibility Grounds:",
        options=inadmissibility_grounds,
        default=[],
        help="Choose inadmissibility grounds (leave empty to show all)"
    )
with col_f4:
    selected_residents = st.multiselect(
        "Select Resident Status:",
        options=residents,
        default=[],
        help="Choose resident status (leave empty to show all)"
    )

st.markdown("---")

# Apply filters
mask = pd.Series([True] * len(df))  # Start with all True

if selected_countries:
    mask &= df['country'].isin(selected_countries)
if selected_years:
    mask &= df['year'].isin(selected_years)
if selected_inadmissibility:
    mask &= df['inadmissibility_grounds'].isin(selected_inadmissibility)
if selected_residents:
    mask &= df['resident'].isin(selected_residents)

filtered_df = df[mask]

# Show current filter status
if not any([selected_countries, selected_years, selected_inadmissibility, selected_residents]):
    st.info("ℹ️ No filters selected - showing all data. Use the filter section above to select criteria.")
else:
    active_filters = []
    if selected_countries:
        active_filters.append(f"Countries: {len(selected_countries)} selected")
    if selected_years:
        active_filters.append(f"Years: {len(selected_years)} selected")
    if selected_inadmissibility:
        active_filters.append(f"Inadmissibility Grounds: {len(selected_inadmissibility)} selected")
    if selected_residents:
        active_filters.append(f"Resident Status: {len(selected_residents)} selected")
    st.info(f"🔍 Active filters: {' | '.join(active_filters)}")

# Main dashboard
if filtered_df.empty:
    st.warning("⚠️ No data matches the selected filters. Please adjust your filter criteria.")
    st.stop()

# Key metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_cases = filtered_df['count'].sum()
    st.metric("Total Cases", f"{total_cases:,}")

with col2:
    unique_countries = filtered_df['country'].nunique()
    st.metric("Countries", unique_countries)

with col3:
    year_range = f"{filtered_df['year'].min()}-{filtered_df['year'].max()}"
    st.metric("Year Range", year_range)

with col4:
    avg_cases_per_country = filtered_df.groupby('country')['count'].sum().mean()
    st.metric("Avg Cases/Country", f"{avg_cases_per_country:.1f}")

st.markdown("---")

# Data table
st.subheader("📊 Filtered Data")
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "count": st.column_config.NumberColumn(
            "Count",
            help="Number of refused cases",
            format="%d",
        ),
        "year": st.column_config.NumberColumn(
            "Year",
            format="%d",
        ),
    }
)

# Visualizations
st.markdown("---")
st.subheader("📈 Data Visualizations")

# Check if no filters are selected to show default charts
no_filters_selected = not any([selected_countries, selected_years, selected_inadmissibility, selected_residents])

if no_filters_selected:
    # Default visualizations when no filters are selected
    st.subheader("🏠 Default Overview Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Total Refusals by Inadmissibility Grounds
        inadmiss_data = df.groupby('inadmissibility_grounds')['count'].sum().reset_index()
        inadmiss_data = inadmiss_data.sort_values('count', ascending=False)
        
        fig_inadmiss = px.bar(
            inadmiss_data,
            x='inadmissibility_grounds',
            y='count',
            title='Total Refusals by Inadmissibility Grounds',
            color='count',
            color_continuous_scale='Blues'
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
            title='Top 10 Countries by Total Refusals',
            color='count',
            color_continuous_scale='Blues'
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
    fig_trends.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Refusals",
        legend_title="Inadmissibility Type"
    )
    st.plotly_chart(fig_trends, use_container_width=True)
    
    # Slope Graph for Resident Status
    st.subheader("📊 Resident Status Trends")
    
    # Prepare data for slope graph
    resident_yearly = df.groupby(['year', 'resident'])['count'].sum().reset_index()
    
    # Create slope graph
    fig_slope = go.Figure()
    
    residents_list = resident_yearly['resident'].unique()
    colors = px.colors.qualitative.Set2
    
    for i, resident_type in enumerate(residents_list):
        data = resident_yearly[resident_yearly['resident'] == resident_type]
        
        fig_slope.add_trace(go.Scatter(
            x=data['year'],
            y=data['count'],
            mode='lines+markers',
            name=resident_type,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8)
        ))
    
    fig_slope.update_layout(
        title='Refusals by Resident Status Over Time (Slope Graph)',
        xaxis_title='Year',
        yaxis_title='Number of Refusals',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_slope, use_container_width=True)

else:
    # Filtered visualizations - dynamic based on selected filters
    st.subheader("🔍 Filtered Data Visualizations")
    
    # Determine which filters are active
    year_selected = len(selected_years) > 0
    country_selected = len(selected_countries) > 0
    inadmissibility_selected = len(selected_inadmissibility) > 0
    resident_selected = len(selected_residents) > 0
    
    # Case 1: All three main filters selected (year, country, inadmissibility)
    if year_selected and country_selected and inadmissibility_selected:
        st.subheader("📊 Complete Filter Applied")
        total_refusals = filtered_df['count'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Refusals", f"{total_refusals:,}")
        with col2:
            st.metric("Years", f"{', '.join(map(str, selected_years))}")
        with col3:
            st.metric("Countries", f"{', '.join(selected_countries[:3])}{'...' if len(selected_countries) > 3 else ''}")
        
        if total_refusals > 0:
            st.success(f"Found {total_refusals} refusal(s) matching your criteria.")
        else:
            st.warning("No refusals found matching your criteria.")
    
    # Case 2: Year and Country selected (show inadmissibility grounds)
    elif year_selected and country_selected and not inadmissibility_selected:
        st.subheader("📊 Inadmissibility Grounds for Selected Year(s) and Country(ies)")
        
        inadmiss_data = filtered_df.groupby('inadmissibility_grounds')['count'].sum().reset_index()
        inadmiss_data = inadmiss_data.sort_values('count', ascending=False)
        
        if not inadmiss_data.empty:
            fig_inadmiss = px.bar(
                inadmiss_data,
                x='inadmissibility_grounds',
                y='count',
                title=f'Inadmissibility Grounds for {", ".join(selected_countries[:3])} in {", ".join(map(str, selected_years))}',
                color='count',
                color_continuous_scale='Oranges'
            )
            fig_inadmiss.update_layout(
                xaxis_title="Inadmissibility Grounds",
                yaxis_title="Number of Refusals",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_inadmiss, use_container_width=True)
    
    # Case 3: Year and Inadmissibility selected (show top countries)
    elif year_selected and inadmissibility_selected and not country_selected:
        st.subheader("🌍 Top Countries for Selected Year(s) and Inadmissibility Ground(s)")
        
        country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False)
        top_countries = country_data.head(10)
        
        if not top_countries.empty:
            fig_countries = px.bar(
                top_countries,
                x='country',
                y='count',
                title=f'Top 10 Countries for {", ".join(selected_inadmissibility)} in {", ".join(map(str, selected_years))}',
                color='count',
                color_continuous_scale='Reds'
            )
            fig_countries.update_layout(
                xaxis_title="Country",
                yaxis_title="Number of Refusals",
                xaxis_tickangle=-45
            )
            st.plotly_chart(fig_countries, use_container_width=True)
    
    # Case 4: Country and Inadmissibility selected (show yearly trends)
    elif country_selected and inadmissibility_selected and not year_selected:
        st.subheader("📅 Yearly Trends for Selected Country(ies) and Inadmissibility Ground(s)")
        
        yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
        
        if not yearly_data.empty:
            fig_yearly = px.line(
                yearly_data,
                x='year',
                y='count',
                title=f'Refusals Over Time: {", ".join(selected_countries[:3])} - {", ".join(selected_inadmissibility)}',
                markers=True,
                line_shape='spline'
            )
            fig_yearly.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Refusals"
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
    
    # Case 5: Only Year selected (show treemap for top countries with inadmissibility grounds)
    elif year_selected and not country_selected and not inadmissibility_selected:
        st.subheader(f"🗺️ Top Countries and Inadmissibility Grounds for {', '.join(map(str, selected_years))}")
        
        # Get top 5 countries for the selected year(s)
        top_countries_data = filtered_df.groupby('country')['count'].sum().sort_values(ascending=False).head(5)
        treemap_data = filtered_df[filtered_df['country'].isin(top_countries_data.index)]
        
        if not treemap_data.empty and treemap_data['count'].sum() > 0:
            fig_treemap = px.treemap(
                treemap_data,
                path=["country", "inadmissibility_grounds"],
                values="count",
                title=f"Top 5 Countries and Inadmissibility Grounds for {', '.join(map(str, selected_years))}"
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry")
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Case 6: Only Country selected (show treemap with inadmissibility grounds)
    elif country_selected and not year_selected and not inadmissibility_selected:
        st.subheader(f"🗺️ Inadmissibility Grounds for {', '.join(selected_countries[:3])}")
        
        if not filtered_df.empty and filtered_df['count'].sum() > 0:
            fig_treemap = px.treemap(
                filtered_df,
                path=["country", "inadmissibility_grounds"],
                values="count",
                title=f"Inadmissibility Grounds for {', '.join(selected_countries[:3])}"
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry")
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
    
    # Case 7: Only Inadmissibility selected (show trends by country instead of inadmissibility)
    elif inadmissibility_selected and not year_selected and not country_selected:
        st.subheader(f"📈 Refusal Trends Over Time by Country for {', '.join(selected_inadmissibility)}")
        
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
                title=f'Refusal Trends Over Time by Country for {", ".join(selected_inadmissibility)}',
                markers=True
            )
            fig_trends.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Refusals",
                legend_title="Country"
            )
            st.plotly_chart(fig_trends, use_container_width=True)
    
    # Case 8: Only Resident selected or other combinations
    else:
        st.subheader("📊 General Analysis")
        
        # Show a few key charts based on available data
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart by most relevant dimension
            if not country_selected:
                country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False).head(10)
                if not country_data.empty:
                    fig_bar = px.bar(
                        country_data,
                        x='country',
                        y='count',
                        title='Top 10 Countries',
                        color='count',
                        color_continuous_scale='Blues'
                    )
                    fig_bar.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig_bar, use_container_width=True)
        
        with col2:
            # Yearly trend if not year selected
            if not year_selected:
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

# Download section
st.markdown("---")
st.subheader("💾 Download Filtered Data")

# Convert to CSV for download
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=csv,
    file_name=f"a34_refused_filtered_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# Summary statistics
with st.expander("📈 Summary Statistics"):
    st.write("**Descriptive Statistics for Count Column:**")
    st.write(filtered_df['count'].describe())
    
    st.write("**Cases by Category:**")
    summary_stats = pd.DataFrame({
        'Total Cases': [filtered_df['count'].sum()],
        'Countries': [filtered_df['country'].nunique()],
        'Years Covered': [filtered_df['year'].nunique()],
        'Inadmissibility Grounds': [filtered_df['inadmissibility_grounds'].nunique()],
        'Resident Types': [filtered_df['resident'].nunique()],
        'Non-Zero Cases': [len(filtered_df[filtered_df['count'] > 0])],
        'Zero Cases': [len(filtered_df[filtered_df['count'] == 0])]
    })
    st.dataframe(summary_stats.T, column_config={"0": "Value"})