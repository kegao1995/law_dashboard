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
cor_statuses = sorted(df['cor_status'].unique())
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
    selected_cor_status = st.multiselect(
        "Select COR Status:",
        options=cor_statuses,
        default=[],
        help="Choose COR (Country of Reference) status (leave empty to show all)"
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
if selected_cor_status:
    mask &= df['cor_status'].isin(selected_cor_status)
if selected_residents:
    mask &= df['resident'].isin(selected_residents)

filtered_df = df[mask]

# Show current filter status
if not any([selected_countries, selected_years, selected_cor_status, selected_residents]):
    st.info("ℹ️ No filters selected - showing all data. Use the filter section above to select criteria.")
else:
    active_filters = []
    if selected_countries:
        active_filters.append(f"Countries: {len(selected_countries)} selected")
    if selected_years:
        active_filters.append(f"Years: {len(selected_years)} selected")
    if selected_cor_status:
        active_filters.append(f"COR Status: {len(selected_cor_status)} selected")
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

# Create tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["📅 Trends Over Time", "🌍 By Country", "📊 By Status", "🔄 Comparative Analysis"])

with tab1:
    st.subheader("Cases by Year")
    
    # Time series chart
    yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
    
    fig_line = px.line(
        yearly_data, 
        x='year', 
        y='count',
        title='Total Refused Cases Over Time',
        markers=True,
        line_shape='spline'
    )
    fig_line.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Cases",
        hovermode='x unified'
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # Stacked area chart by COR status
    yearly_cor_data = filtered_df.groupby(['year', 'cor_status'])['count'].sum().reset_index()
    
    fig_area = px.area(
        yearly_cor_data,
        x='year',
        y='count',
        color='cor_status',
        title='Cases Over Time by COR Status'
    )
    fig_area.update_layout(
        xaxis_title="Year",
        yaxis_title="Number of Cases"
    )
    st.plotly_chart(fig_area, use_container_width=True)

with tab2:
    st.subheader("Cases by Country")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart by country
        country_data = filtered_df.groupby('country')['count'].sum().reset_index().sort_values('count', ascending=False)
        
        fig_bar = px.bar(
            country_data.head(15),  # Show top 15 countries
            x='count',
            y='country',
            orientation='h',
            title='Top Countries by Number of Cases',
            color='count',
            color_continuous_scale='Reds'
        )
        fig_bar.update_layout(
            xaxis_title="Number of Cases",
            yaxis_title="Country",
            yaxis={'categoryorder': 'total ascending'}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart for top countries
        top_countries = country_data.head(10)
        
        fig_pie = px.pie(
            top_countries,
            values='count',
            names='country',
            title='Distribution of Cases (Top 10 Countries)'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

with tab3:
    st.subheader("Cases by Status Categories")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # COR Status distribution
        cor_data = filtered_df.groupby('cor_status')['count'].sum().reset_index()
        # Use distinct colors for each COR status
        colors = ["#dc3e3e", "#fc8c8c"] 
        
        fig_cor = px.bar(
            cor_data,
            x='cor_status',
            y='count',
            title='Cases by COR Status',
            color='cor_status',
            color_discrete_sequence=colors
        )
        fig_cor.update_layout(
            xaxis_title="COR Status",
            yaxis_title="Number of Cases",
            showlegend=False,
        )
        st.plotly_chart(fig_cor)
    
    with col2:
        # Resident status distribution
        resident_data = filtered_df.groupby('resident')['count'].sum().reset_index()
        
        # Use distinct colors for each resident status
        colors = ["#dc3e3e", "#fc8c8c"] 
        
        fig_resident = px.bar(
            resident_data,
            x='resident',
            y='count',
            title='Cases by Resident Status',
            color='resident',
            color_discrete_sequence=colors
        )
        fig_resident.update_layout(
            xaxis_title="Resident Status",
            yaxis_title="Number of Cases",
            showlegend=False,
        )
        st.plotly_chart(fig_resident)

with tab4:
    st.subheader("Comparative Analysis")
    
    # Heatmap showing relationship between country and year
    heatmap_data = filtered_df.pivot_table(
        values='count', 
        index='country', 
        columns='year', 
        aggfunc='sum', 
        fill_value=0
    )
    
    # Only show countries with significant data
    country_totals = heatmap_data.sum(axis=1).sort_values(ascending=False)
    top_countries_heatmap = country_totals.head(15).index
    heatmap_subset = heatmap_data.loc[top_countries_heatmap]
    
    fig_heatmap = px.imshow(
        heatmap_subset,
        title='Cases Heatmap: Countries vs Years',
        color_continuous_scale='Reds',
        aspect='auto'
    )
    fig_heatmap.update_layout(
        xaxis_title="Year",
        yaxis_title="Country"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # Sunburst chart for hierarchical view
    sunburst_data = filtered_df[filtered_df['count'] > 0].copy()  # Only show non-zero cases
    
    fig_sunburst = px.sunburst(
        sunburst_data,
        path=['cor_status', 'country', 'year'],
        values='count',
        title='Hierarchical View: COR Status → Country → Year'
    )
    st.plotly_chart(fig_sunburst, use_container_width=True)

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
        'COR Statuses': [filtered_df['cor_status'].nunique()],
        'Resident Types': [filtered_df['resident'].nunique()],
        'Non-Zero Cases': [len(filtered_df[filtered_df['count'] > 0])],
        'Zero Cases': [len(filtered_df[filtered_df['count'] == 0])]
    })
    st.dataframe(summary_stats.T, column_config={"0": "Value"})