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

# Create slope graph function
def create_resident_slope_graph(data, title_suffix=""):
    """Create a slope graph comparing Permanent vs Temporary residents"""
    # Group by resident status and calculate totals
    resident_data = data.groupby('resident')['count'].sum().reset_index()
    
    if len(resident_data) < 2:
        st.warning("⚠️ Insufficient data for resident comparison chart.")
        return None
        
    # Create slope graph
    fig_slope = go.Figure()
    
    # Get values for permanent and temporary residents
    perm_resident = resident_data[resident_data['resident'] == 'Permanent Resident']['count'].iloc[0] if 'Permanent Resident' in resident_data['resident'].values else 0
    temp_resident = resident_data[resident_data['resident'] == 'Temporary Resident']['count'].iloc[0] if 'Temporary Resident' in resident_data['resident'].values else 0
    
    # Create slope line
    fig_slope.add_trace(go.Scatter(
        x=[0, 1],
        y=[perm_resident, temp_resident],
        mode='lines+markers+text',
        line=dict(color='blue', width=4),
        marker=dict(size=15, color=['#FF6B6B', '#4ECDC4']),
        text=[f'Permanent<br>{perm_resident:,}', f'Temporary<br>{temp_resident:,}'],
        textposition=['middle left', 'middle right'],
        textfont=dict(size=14, color='black'),
        name='Resident Status Comparison',
        hovertemplate='<b>%{text}</b><br>Count: %{y:,}<extra></extra>'
    ))
    
    # Update layout
    fig_slope.update_layout(
        title=f'Permanent vs Temporary Residents{title_suffix}',
        xaxis=dict(
            tickvals=[0, 1],
            ticktext=['Permanent Resident', 'Temporary Resident'],
            showgrid=False,
            zeroline=False,
            range=[-0.3, 1.3]
        ),
        yaxis=dict(
            title='Number of Refusals',
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        margin=dict(l=80, r=80, t=80, b=80)
    )
    
    return fig_slope

# ----------------------
# Filters on main page
# ----------------------
st.header("🔍 Data Filters")

# Initialize clear filter state
if 'clear_filters' not in st.session_state:
    st.session_state.clear_filters = False

col_f1, col_f2, col_f3, col_f4 = st.columns([1,1,1,1])

with col_f4:
    if st.button("🗑️ Clear All Filters"):
        # Set flag to clear filters
        st.session_state.clear_filters = True
        st.rerun()

# Get unique values for each column
countries = sorted(df['country'].unique())
years = sorted(df['year'].unique())
inadmissibility_grounds = sorted(df['inadmissibility_grounds'].unique())

# Determine default values based on clear filter state
countries_default = None if st.session_state.clear_filters else st.session_state.get('selected_countries', None)
years_default = None if st.session_state.clear_filters else st.session_state.get('selected_years', None)
inadmissibility_default = None if st.session_state.clear_filters else st.session_state.get('selected_inadmissibility', None)

# Reset the clear filter flag after using it
if st.session_state.clear_filters:
    st.session_state.clear_filters = False

with col_f1:
    selected_countries = st.selectbox(
        "Select Country:",
        options=[None] + countries,
        index=0 if countries_default is None else (countries.index(countries_default) + 1 if countries_default in countries else 0),
        key='selected_countries',
        help="Choose a country to analyze (leave empty to show all)",
        format_func=lambda x: "All Countries" if x is None else x
    )
with col_f2:
    selected_years = st.selectbox(
        "Select Year:",
        options=[None] + years,
        index=0 if years_default is None else (years.index(years_default) + 1 if years_default in years else 0),
        key='selected_years',
        help="Choose a year to analyze (leave empty to show all)",
        format_func=lambda x: "All Years" if x is None else str(x)
    )
with col_f3:
    selected_inadmissibility = st.selectbox(
        "Select Inadmissibility Ground:",
        options=[None] + inadmissibility_grounds,
        index=0 if inadmissibility_default is None else (inadmissibility_grounds.index(inadmissibility_default) + 1 if inadmissibility_default in inadmissibility_grounds else 0),
        key='selected_inadmissibility',
        help="Choose an inadmissibility ground (leave empty to show all)",
        format_func=lambda x: "All Inadmissibility Grounds" if x is None else x
    )

st.markdown("---")

# Apply filters
mask = pd.Series([True] * len(df))  # Start with all True

if selected_countries is not None:
    mask &= df['country'] == selected_countries
if selected_years is not None:
    mask &= df['year'] == selected_years
if selected_inadmissibility is not None:
    mask &= df['inadmissibility_grounds'] == selected_inadmissibility

filtered_df = df[mask]

# Show current filter status
if not any([selected_countries is not None, selected_years is not None, selected_inadmissibility is not None]):
    st.info("ℹ️ No filters selected - showing all data. Use the filter section above to select criteria.")
else:
    active_filters = []
    if selected_countries is not None:
        active_filters.append(f"Country: {selected_countries}")
    if selected_years is not None:
        active_filters.append(f"Year: {selected_years}")
    if selected_inadmissibility is not None:
        active_filters.append(f"Inadmissibility Ground: {selected_inadmissibility}")
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

# Visualizations
st.markdown("---")
st.subheader("📈 Data Visualizations")

# Check if no filters are selected to show default charts
no_filters_selected = not any([selected_countries is not None, selected_years is not None, selected_inadmissibility is not None])

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
            color_discrete_sequence=['#1f77b4']
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
            color_discrete_sequence=['#1f77b4']
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
    
    # Slope Graph for Resident Status
    st.subheader("📊 Permanent vs Temporary Residents Comparison")
    
    # Create and display slope graph for all data
    slope_fig = create_resident_slope_graph(df, " - All Data")
    if slope_fig:
        st.plotly_chart(slope_fig, use_container_width=True)

else:
    # Filtered visualizations - dynamic based on selected filters
    st.subheader("🔍 Filtered Data Visualizations")    # Determine which filters are active
    year_selected = selected_years is not None
    country_selected = selected_countries is not None
    inadmissibility_selected = selected_inadmissibility is not None
    
    # Case 1: All three main filters selected (year, country, inadmissibility)
    if year_selected and country_selected and inadmissibility_selected:
        st.subheader("📊 Complete Filter Applied")
        total_refusals = filtered_df['count'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Refusals", f"{total_refusals:,}")
        with col2:
            st.metric("Year", str(selected_years))
        with col3:
            st.metric("Country", selected_countries)
        
        if total_refusals > 0:
            st.success(f"Found {total_refusals} refusal(s) matching your criteria.")
            
            # Add slope graph for this filtered data
            st.subheader("📊 Permanent vs Temporary Residents Comparison")
            slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_countries} in {selected_years}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
        else:
            st.warning("No refusals found matching your criteria.")
      # Case 2: Year and Country selected (show inadmissibility grounds)
    elif year_selected and country_selected and not inadmissibility_selected:
        st.subheader("📊 Analysis for Selected Year and Country")
        
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
                    title=f'Inadmissibility Grounds for {selected_countries} in {selected_years}',
                    color_discrete_sequence=['#FF6B6B']
                )
                fig_inadmiss.update_layout(
                    xaxis_title="Inadmissibility Grounds",
                    yaxis_title="Number of Refusals",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_inadmiss, use_container_width=True)
        
        with col2:
            # Show summary metrics since we only have single selections
            total_cases = filtered_df['count'].sum()
            unique_inadmiss = filtered_df['inadmissibility_grounds'].nunique()
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric(
                    "Total Cases",
                    f"{total_cases:,}",
                    help=f"Total refusals for {selected_countries} in {selected_years}"
                )
            with col2_2:
                st.metric(
                    "Inadmissibility Types", 
                    unique_inadmiss,
                    help="Number of different inadmissibility grounds"                )
        
        # Add slope graph for resident comparison
        st.subheader("📊 Permanent vs Temporary Residents Comparison")
        slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_countries} in {selected_years}")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)
      # Case 3: Year and Inadmissibility selected (show top countries)
    elif year_selected and inadmissibility_selected and not country_selected:
        st.subheader("🌍 Analysis for Selected Year and Inadmissibility Ground")
        
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
                    title=f'Top 10 Countries for {selected_inadmissibility} in {selected_years}',
                    color_discrete_sequence=['#FF6B6B']
                )
                fig_countries.update_layout(
                    xaxis_title="Country",
                    yaxis_title="Number of Refusals",
                    xaxis_tickangle=-45
                )
                st.plotly_chart(fig_countries, use_container_width=True)
        
        with col2:
            # Show summary metrics since we only have single selections
            total_cases = filtered_df['count'].sum()
            unique_countries = filtered_df['country'].nunique()
            
            col2_1, col2_2 = st.columns(2)
            with col2_1:
                st.metric(
                    "Total Cases",
                    f"{total_cases:,}",
                    help=f"Total refusals for {selected_inadmissibility} in {selected_years}"
                )
            with col2_2:                st.metric(
                    "Countries Affected", 
                    unique_countries,
                    help="Number of countries with refusals"
                )
        
        # Add slope graph for resident comparison
        st.subheader("📊 Permanent vs Temporary Residents Comparison")
        slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_inadmissibility} in {selected_years}")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 4: Country and Inadmissibility selected (show yearly trends)
    elif country_selected and inadmissibility_selected and not year_selected:
        st.subheader("📅 Yearly Trends for Selected Country and Inadmissibility Ground")
        
        yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
        
        if not yearly_data.empty:
            fig_yearly = px.line(
                yearly_data,
                x='year',                
                 y='count',
                title=f'Refusals Over Time: {selected_countries} - {selected_inadmissibility}',
                markers=True,
                line_shape='spline'
            )
            fig_yearly.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Refusals"
            )
            st.plotly_chart(fig_yearly, use_container_width=True)
            
            # Add slope graph for resident comparison
            st.subheader("📊 Permanent vs Temporary Residents Comparison")
            slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_countries} - {selected_inadmissibility}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 5: Only Year selected (show treemap for top countries with inadmissibility grounds)
    elif year_selected and not country_selected and not inadmissibility_selected:
        st.subheader(f"🗺️ Top Countries and Inadmissibility Grounds for {selected_years}")
        
        # Get top 5 countries for the selected year
        top_countries_data = filtered_df.groupby('country')['count'].sum().sort_values(ascending=False).head(5)
        treemap_data = filtered_df[filtered_df['country'].isin(top_countries_data.index)]
        
        if not treemap_data.empty and treemap_data['count'].sum() > 0:
            fig_treemap = px.treemap(
                treemap_data,
                path=["country", "inadmissibility_grounds"],
                values="count",
                title=f"Top 5 Countries and Inadmissibility Grounds for {selected_years}",
                color="inadmissibility_grounds",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry")
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
            
            # Add slope graph for resident comparison
            st.subheader("📊 Permanent vs Temporary Residents Comparison")
            slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_years}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
      # Case 6: Only Country selected (show multiple analysis)
    elif country_selected and not year_selected and not inadmissibility_selected:
        st.subheader(f"📊 Analysis for {selected_countries}")
        
        col1, col2 = st.columns(2)
        
        with col1:            # Time series for the selected country
            yearly_data = filtered_df.groupby('year')['count'].sum().reset_index()
            
            if not yearly_data.empty:
                fig_yearly = px.line(
                    yearly_data,
                    x='year',
                    y='count',
                    title=f'Refusals Over Time for {selected_countries}',
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
                    title=f'Inadmissibility Trends for {selected_countries}',
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
                title=f"Inadmissibility Grounds for {selected_countries}",
                color="inadmissibility_grounds",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_treemap.update_traces(textinfo="label+value+percent entry")
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
          # Add slope graph for resident comparison
        st.subheader("📊 Permanent vs Temporary Residents Comparison")
        slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_countries}")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)
      # Case 7: Only Inadmissibility selected (show comprehensive analysis)
    elif inadmissibility_selected and not year_selected and not country_selected:
        st.subheader(f"📈 Analysis for {selected_inadmissibility}")
        
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
                    title=f'Top 10 Countries for {selected_inadmissibility}',
                    color_discrete_sequence=['#4ECDC4']
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
            
            # Add slope graph for resident comparison
            st.subheader("📊 Permanent vs Temporary Residents Comparison")
            slope_fig = create_resident_slope_graph(filtered_df, f" - {selected_inadmissibility}")
            if slope_fig:
                st.plotly_chart(slope_fig, use_container_width=True)
    
    # Case 8: Only Resident selected or other combinations
    else:
        st.subheader("📊 General Analysis")
        
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
                        title='Top 10 Countries',
                        color_discrete_sequence=['#1f77b4']
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
        
        # Add slope graph for resident comparison
        st.subheader("📊 Permanent vs Temporary Residents Comparison")
        slope_fig = create_resident_slope_graph(filtered_df, " - General Analysis")
        if slope_fig:
            st.plotly_chart(slope_fig, use_container_width=True)

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