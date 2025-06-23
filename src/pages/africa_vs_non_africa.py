import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
from plotly.colors import qualitative
import os

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
      .large-title {
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 0.2rem;
      }
      .subtitle {
        font-size: 1.25rem;
        color: #666666;
        margin-bottom: 2rem;
      }
    </style>
    """,
    unsafe_allow_html=True
)
continent_colors = {
    "Africa":        "#e74c3c",
    "Caribbean":     "#7a5618",
    "North America": "#2980b9",
    "Asia":          "#27ae60",
    "Europe":        "#8e44ad",
    "South America": "#54cac8",
    "Oceania":       "#f39c12",
    "Unspecified":   "#7f8c8d",
}
st.markdown('<div class="large-title">Litigation Cases by Region</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">'
    'This dashboard is aimed at uncovering patterns of dismissed rates across '
    'regions to evaluate potential Anti-African/Black racism in litigation outcomes.'
    '</div>',
    unsafe_allow_html=True
)


@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "litigation_cases.xlsx")
    return pd.read_excel(path, skiprows=5, skipfooter=7)

df = load_data()
df['LIT Leave Decision Desc'] = (
    df['LIT Leave Decision Desc']
      .replace(r'^Discontinued.*', 'Discontinued', regex=True)
      .replace(r'^Dismissed.*',    'Dismissed',    regex=True)
      .replace(r'^Allowed.*',      'Allowed',      regex=True)
)

continent_map = {
    'India': 'Asia', 'Fiji': 'Oceania', 'Russia': 'Asia', 'Republic of Indonesia': 'Asia',
    'Georgia': 'Asia', 'Nigeria': 'Africa', 'United States of America': 'North America',
    'Lebanon': 'Asia', 'Croatia': 'Europe', 'Egypt': 'Africa', "People's Republic of China": 'Asia',
    'Albania': 'Europe', 'Colombia': 'South America', 'Somalia, Democratic Republic of': 'Africa',
    'Iraq': 'Asia', 'Italy': 'Europe', 'Rwanda': 'Africa', 
    'United Kingdom and Overseas Territories': 'Europe', 'Bulgaria': 'Europe', 
    'Ukraine': 'Europe', 'Kenya': 'Africa', 'Stateless': 'Unspecified', 'Greece': 'Europe',
    'Syria': 'Asia', 'Jamaica': 'North America', 'Hungary': 'Europe', 'Turkey': 'Asia',
    'Pakistan': 'Asia', 'Socialist Republic of Vietnam': 'Asia', 'Kazakhstan': 'Asia',
    'Mexico': 'North America', 'Federal Republic of Cameroon': 'Africa',
    'Congo, Democratic Republic of the': 'Africa', 'Namibia': 'Africa', 'Iran': 'Asia',
    'Cambodia': 'Asia', "Korea, People's Democratic Republic of": 'Asia',
    'Trinidad and Tobago, Republic of': 'North America', 'Peru': 'South America',
    'Palestinian Authority (Gaza/West Bank)': 'Asia', 'St. Kitts-Nevis': 'North America',
    'Republic of Ivory Coast': 'Africa', 'Ghana': 'Africa', 'Republic of South Africa': 'Africa',
    'El Salvador': 'North America', 'Bangladesh': 'Asia', 'Kosovo, Republic of': 'Europe',
    'Guinea, Republic of': 'Africa', 'Sri Lanka': 'Asia', 'Latvia': 'Europe',
    'Hong Kong SAR': 'Asia', 'Jordan': 'Asia', 'Slovak Republic': 'Europe', 'Zimbabwe': 'Africa',
    'St. Lucia': 'North America', 'Honduras': 'North America', 'United Republic of Tanzania': 'Africa',
    'Nepal': 'Asia', 'St. Vincent and the Grenadines': 'North America', 'Philippines': 'Asia',
    'Sierra Leone': 'Africa', 'Tunisia': 'Africa', 'Federal Republic of Germany': 'Europe',
    'Togo, Republic of': 'Africa', 'Spain': 'Europe', 'Malawi': 'Africa', 'France': 'Europe',
    'Afghanistan': 'Asia', 'Guyana': 'South America', 'Haiti': 'North America', 'Belgium': 'Europe',
    'Kuwait': 'Asia', 'Eritrea': 'Africa', 'Algeria': 'Africa', 'Uganda': 'Africa',
    'Democratic Republic of Sudan': 'Africa', 'Gabon Republic': 'Africa',
    'Korea, Republic of': 'Asia', 'Chad, Republic of': 'Africa', 'Saudi Arabia': 'Asia',
    'Brazil': 'South America', 'Mauritius': 'Africa', 'Israel': 'Asia', 'Azerbaijan': 'Asia',
    'Argentina': 'South America', 'Portugal': 'Europe', 'Dominican Republic': 'North America',
    'Libya': 'Africa', 'Senegal': 'Africa', 'Romania': 'Europe', 'Venezuela': 'South America',
    'Poland': 'Europe', 'Belarus': 'Europe', 'Panama, Republic of': 'North America',
    'Gambia': 'Africa', 'Norway': 'Europe', 'Ethiopia': 'Africa', 'Swaziland': 'Africa',
    'Costa Rica': 'North America', 'Barbados': 'North America', 'Malaysia': 'Asia',
    'The Netherlands': 'Europe', 'Liberia': 'Africa', 'Taiwan': 'Asia', 'Switzerland': 'Europe',
    'Mozambique': 'Africa', 'Nicaragua': 'North America', 'Republic of Ireland': 'Europe',
    'Burkina-Faso': 'Africa', 'Madagascar': 'Africa', 'Ecuador': 'South America',
    'Morocco': 'Africa', 'Peoples Republic of Benin': 'Africa', 'Burundi': 'Africa',
    'Chile': 'South America', 'Belize': 'North America', 'Republic of Djibouti': 'Africa',
    'Mali, Republic of': 'Africa', 'Uzbekistan': 'Asia', 'Montenegro, Republic of': 'Europe',
    'Mauritania': 'Africa', 'Angola': 'Africa', 'Armenia': 'Asia', 'Moldova': 'Europe',
    'Yemen, Republic of': 'Asia', 'Bahama Islands, The': 'North America', 'Grenada': 'North America',
    "Congo, People's Republic of the": 'Africa', 'Sweden': 'Europe', 'Czech Republic': 'Europe',
    'Guinea-Bissau': 'Africa', 'Kyrgyzstan': 'Asia', 'Antigua and Barbuda': 'North America',
    'Equatorial Guinea': 'Africa', 'Japan': 'Asia', 'Cuba': 'North America', 'Lesotho': 'Africa',
    'Bosnia-Hercegovina': 'Europe', 'Serbia, Republic of': 'Europe', 'Guatemala': 'North America',
    'Austria': 'Europe', 'Vanuatu': 'Oceania', 'Turkmenistan': 'Asia', 
    'Serbia and Montenegro': 'Europe', 'Lithuania': 'Europe',
    "Mongolia, People's Republic of": 'Asia', 'Republic of the Niger': 'Africa', 'Thailand': 'Asia',
    'Botswana, Republic of': 'Africa', 'New Zealand': 'Oceania', 'Myanmar (Burma)': 'Asia',
    'Unspecified': 'Unspecified', 'Bahrain': 'Asia', 'Macedonia': 'Europe', 'Singapore': 'Asia',
    'United Arab Emirates': 'Asia', 'Surinam': 'South America', 'Bolivia': 'South America',
    'Uruguay': 'South America', 'Australia': 'Oceania', 'Comoros': 'Africa', 'Paraguay': 'South America',
    'Zambia': 'Africa', 'Tadjikistan': 'Asia', 'Cyprus': 'Europe', 'Qatar': 'Asia',
    'Dominica': 'North America', 'Central African Republic': 'Africa', 'Denmark': 'Europe',
    'Macao SAR': 'Asia', 'South Sudan, Republic Of': 'Africa', 'Estonia': 'Europe',
    'Bhutan': 'Asia', 'Slovenia': 'Europe', 'Oman': 'Asia', 'Luxembourg': 'Europe',
    'Solomons, The': 'Oceania', 'Laos': 'Asia', 'Finland': 'Europe', 'Iceland': 'Europe'
}

caribbean_countries = {
    'Antigua and Barbuda': 'Caribbean',
    'Bahamas': 'Caribbean',
    'Barbados': 'Caribbean',
    'Cuba': 'Caribbean',
    'Dominica': 'Caribbean',
    'Dominican Republic': 'Caribbean',
    'Grenada': 'Caribbean',
    'Haiti': 'Caribbean',
    'Jamaica': 'Caribbean',
    'Saint Kitts and Nevis': 'Caribbean',
    'Saint Lucia': 'Caribbean',
    'Saint Vincent and the Grenadines': 'Caribbean',
    'Trinidad and Tobago': 'Caribbean',
    'Puerto Rico': 'Caribbean',
    'Saint Martin': 'Caribbean',
    'Montserrat': 'Caribbean',
    'Anguilla': 'Caribbean',
    'British Virgin Islands': 'Caribbean',
    'US Virgin Islands': 'Caribbean',
    'Cayman Islands': 'Caribbean',
    'Aruba': 'Caribbean',
    'Saint Barthelemy': 'Caribbean',
    'Saint Pierre and Miquelon': 'Caribbean',
    'Guadeloupe': 'Caribbean',
    'Martinique': 'Caribbean'
}
continent_map.update(caribbean_countries)
df['continent'] = df["Country of Citizenship"].map(continent_map)

st.header("Total Litigation Cases vs Dismissed Rate by Region")
st.markdown(f"""
- <span style="color:{continent_colors['Asia']}">Asia</span> processes the **highest volume of cases (~22,908)**, yet its **dismissal rate (45.9%)** remains **below the global average**.  
- <span style="color:{continent_colors['Africa']}">Africa</span> handles the **second-highest volume (~13,400 cases)** but its **dismissal rate (56.5%)** is well above the global average.  
- <span style="color:{continent_colors['Caribbean']}">Caribbean</span> tops the list with a **67.7% dismissal rate**, despite handling only about **2,560 cases**.  
- <span style="color:{continent_colors['South America']}">South America</span> and <span style="color:{continent_colors['Europe']}">Europe</span> both have **mid-range volumes** but **lower dismissal rates (~47.5–49.9%)**, highlighting that African and Caribbean cases are treated more punitively.
""", unsafe_allow_html=True)

total = (
    df
    .groupby('continent', as_index=False)['LIT Litigation Count']
    .sum()
    .rename(columns={'LIT Litigation Count':'total_cases'})
)
dismissed = (
    df[df['LIT Leave Decision Desc']=='Dismissed']
    .groupby('continent', as_index=False)['LIT Litigation Count']
    .sum()
    .rename(columns={'LIT Litigation Count':'dismissed_cases'})
)
cont_df = total.merge(dismissed, on='continent', how='left').fillna(0)
cont_df['refusal_rate'] = cont_df['dismissed_cases'] / cont_df['total_cases'] * 100
cont_df = cont_df.sort_values('total_cases', ascending=False).reset_index(drop=True)

bar_colors = cont_df['continent'].map(continent_colors)

fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Bar(
        x=cont_df['continent'],
        y=cont_df['total_cases'],
        name='Litigation Application',
        marker_color=bar_colors,
        text=cont_df['total_cases'],
        textposition='inside',
        showlegend=False
    ),
    secondary_y=False
)

fig.add_trace(
    go.Scatter(
        x=cont_df['continent'],
        y=cont_df['refusal_rate'],
        mode='lines+markers+text',
        name='Dismissal Rate (%)',
        text=cont_df['refusal_rate'].round(1).astype(str) + '%',
        textposition='top center',
        line=dict(color='black'),
        marker=dict(color='black')
    ),
    secondary_y=True
)

fig.update_layout(
    xaxis_title="Continent",
    bargap=0.2,
    legend=dict(y=0.5, traceorder='reversed')
)
fig.update_yaxes(title_text="Litigation Application", secondary_y=False)
fig.update_yaxes(title_text="Dismissal Rate (%)", secondary_y=True, ticksuffix='%')
fig.update_xaxes(categoryorder='array', categoryarray=cont_df['continent'])
fig.update_yaxes(showgrid=False, secondary_y=False)
fig.update_yaxes(showgrid=False, secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

st.markdown("👉We've compared each regions's total cases and dismissed rates, now let's see how they differ from the global average.")
st.header("Overall Dismissal Rate Difference vs Global")
st.markdown(f"""
- <span style="color:{continent_colors['Caribbean']}">Caribbean</span> dismissal rates exceed the world average by **+16.3 pp**, the largest gap of any region.  
- <span style="color:{continent_colors['North America']}">North America</span> is **+8.6 pp** and <span style="color:{continent_colors['Africa']}">Africa</span> **+5.1 pp** above global, confirming a systematic elevation.  
- By contrast, <span style="color:{continent_colors['Asia']}">Asia</span>, <span style="color:{continent_colors['Europe']}">Europe</span> and <span style="color:{continent_colors['South America']}">South America</span> fall below global (–5.6 pp to –1.5 pp), underscoring the specific disadvantage faced by Applicants of African descent.
""", unsafe_allow_html=True)

tot = (
    df
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='cont_total')
)
dis = (
    df[df['LIT Leave Decision Desc'] == 'Dismissed']
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='cont_dismissed')
)
cont_all = tot.merge(dis, on='continent', how='left').fillna(0)
cont_all['cont_rate'] = cont_all['cont_dismissed'] / cont_all['cont_total'] * 100
global_rate = cont_all['cont_dismissed'].sum() / cont_all['cont_total'].sum() * 100
cont_all['delta_pct'] = cont_all['cont_rate'] - global_rate
cont_all_sorted = cont_all.sort_values('delta_pct', ascending=False)

fig = px.bar(
    cont_all_sorted,
    x='continent',
    y='delta_pct',
    text=cont_all_sorted['delta_pct'].round(1).astype(str) + '%',
    labels={'delta_pct':'Δ Refusal Rate (%)','continent':'Continent'},
    category_orders={'continent': cont_all_sorted['continent'].tolist()},
    color='continent',
    color_discrete_map=continent_colors
)
fig.update_traces(textposition='inside')
fig.update_layout(yaxis_ticksuffix='%', yaxis_title='Δ Refusal Rate (%)', xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))

st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
👉Focusing on the three regions whose <strong>dismissal rates</strong> exceed the global average—<span style="color:{continent_colors['Africa']}"><strong>Africa</strong></span>, 
<span style="color:{continent_colors['Caribbean']}"><strong>the Caribbean</strong></span>, and 
<span style="color:{continent_colors['North America']}"><strong>North America</strong></span>—as well as 
<span style="color:{continent_colors['Asia']}"><strong>Asia</strong></span>, which has the 
<strong>highest volume of litigation applications</strong>, we now explore how their other leave decision categories (Allowed, Discontinued) compare.
""", unsafe_allow_html=True)

st.header("Leave Decision % Δ vs Global by Region")
st.markdown(f"""
- Allowed rates are **only slightly above global** in <span style="color:{continent_colors['North America']}">North America</span> (+4.2 pp) and <span style="color:{continent_colors['Africa']}">Africa</span> (+0.9 pp), but **lower** in <span style="color:{continent_colors['Caribbean']}">Caribbean</span> (–2.9 pp) and <span style="color:{continent_colors['Asia']}">Asia</span> (–3.1 pp).  
- Discontinued cases are **substantially below global** in <span style="color:{continent_colors['Caribbean']}">Caribbean</span> (–13.4 pp), <span style="color:{continent_colors['North America']}">North America</span> (–12.8 pp), and <span style="color:{continent_colors['Africa']}">Africa</span> (–6.0 pp), but **above global** in <span style="color:{continent_colors['Asia']}">Asia</span> (+8.6 pp) — indicating Applicants of African descent are **far more likely to be refused outright**.  
- <span style="color:{continent_colors['Caribbean']}">Caribbean</span> dismissed decisions are **+16.3 pp** vs global; <span style="color:{continent_colors['North America']}">North America</span> **+8.6 pp**; <span style="color:{continent_colors['Africa']}">Africa</span> **+5.1 pp**; while <span style="color:{continent_colors['Asia']}">Asia</span> is **–5.6 pp**, indicating fewer rejections via dismissal.
""", unsafe_allow_html=True)



counts = (
    df
    .groupby(['continent','LIT Leave Decision Desc'])['LIT Litigation Count']
    .sum()
    .reset_index(name='count')
)
tot = (
    df
    .groupby('continent')['LIT Litigation Count']
    .sum()
    .reset_index(name='total')
)
cont = counts.merge(tot, on='continent')
cont['pct_cont'] = cont['count'] / cont['total'] * 100
glob = (
    df
    .groupby('LIT Leave Decision Desc')['LIT Litigation Count']
    .sum()
    .reset_index(name='global_count')
)
glob['pct_global'] = glob['global_count'] / glob['global_count'].sum() * 100
cont = cont.merge(glob[['LIT Leave Decision Desc','pct_global']], on='LIT Leave Decision Desc')
cont['diff'] = cont['pct_cont'] - cont['pct_global']
sel = cont[cont['continent'].isin(['Asia','Africa','North America','Caribbean'])]
sel = sel[~sel['LIT Leave Decision Desc'].isin(['Not Started at Leave','No Leave Required','Leave Exception'])]

fig = px.bar(
    sel,
    x='diff',
    y='LIT Leave Decision Desc',
    color='continent',
    barmode='group',
    text=sel['diff'].round(1).astype(str) + '%',
    labels={'diff':'Δ % (continent vs global)','LIT Leave Decision Desc':'Leave Decision','continent':'Continent'},
    category_orders={'LIT Leave Decision Desc': ['Allowed','Discontinued','Dismissed']},
    color_discrete_map=continent_colors
)
fig.update_traces(textposition='inside')
fig.update_layout(xaxis=dict(ticksuffix='%'))

st.plotly_chart(fig, use_container_width=True)

st.markdown("👉To follow the year-over-year trends, let's examine annual litigation application and dismissed rates for our focus regions from 2018 to 2023.")
st.header("Annual Litigation Applications & Dismissed Rates for Selected Regions")
st.markdown(f"""
- Across every year, <span style="color:{continent_colors['Africa']}">Africa</span>, <span style="color:{continent_colors['North America']}">North America</span> and <span style="color:{continent_colors['Caribbean']}">Caribbean</span> exhibit **dismissed rates well above the global average**.  
- The <span style="color:{continent_colors['Caribbean']}">Caribbean's</span> dismissed rate **peaks highest (73.9 % in 2018 → 76.3 % in 2019)**, then declines to **43.2 % by 2022** before rebounding to **48.7 % in 2023**.  
- <span style="color:{continent_colors['Africa']}">Africa's</span> dismissed rate falls from **67.0 % in 2018 to 50.1 % in 2021**, then upticks to **52.4 % in 2023**, even as its share of cases fluctuates around one-third.
""", unsafe_allow_html=True)

year_col  = 'LIT Leave Decision Date - Year'
cont_col  = 'continent'
dec_col   = 'LIT Leave Decision Desc'
count_col = 'LIT Litigation Count'
keep_conts = ['Asia','Africa', 'North America', 'Caribbean']

glob_tot = df.groupby(year_col)[count_col].sum().reset_index(name='global_total')
glob_dis = df[df[dec_col]=='Dismissed'].groupby(year_col)[count_col].sum().reset_index(name='global_dismissed')
glob = glob_tot.merge(glob_dis, on=year_col)
glob['global_rate'] = glob['global_dismissed'] / glob['global_total'] * 100

cont_tot = df.groupby([year_col, cont_col])[count_col].sum().reset_index(name='cont_total')
cont_dis = df[df[dec_col]=='Dismissed'].groupby([year_col, cont_col])[count_col].sum().reset_index(name='cont_dismissed')
cont = cont_tot.merge(cont_dis, on=[year_col, cont_col], how='left').fillna(0)
cont['cont_rate'] = cont['cont_dismissed'] / cont['cont_total'] * 100

cmp = cont.merge(glob[[year_col, 'global_rate', 'global_total']], on=year_col)
cmp = cmp[cmp[cont_col].isin(keep_conts)].sort_values([cont_col, year_col])
cmp['share_pct']     = cmp['cont_total']   / cmp['global_total'] * 100
cmp['remainder_pct'] = 100 - cmp['share_pct']

n    = len(keep_conts)
cols =2
rows = (n + cols - 1) // cols

fig = make_subplots(
    rows=rows,
    cols=cols,
    subplot_titles=keep_conts,
    specs=[[{"secondary_y": True}]*cols for _ in range(rows)],
    vertical_spacing=0.15,
    horizontal_spacing=0.12
)

for i, cont_name in enumerate(keep_conts):
    sub = cmp[cmp[cont_col] == cont_name].sort_values(year_col)
    row, col = i//cols + 1, i%cols + 1

    fig.add_trace(
        go.Bar(
            x=sub[year_col],
            y=sub['share_pct'],
            name=f'{cont_name} share',
            marker_color=continent_colors[cont_name],
            text=sub['cont_total'],
            textposition='inside',
            showlegend=False
        ),
        row=row, col=col, secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=sub[year_col],
            y=sub['cont_rate'],
            name=f'{cont_name} dismissed rate',
            mode='lines+markers+text',
            text=sub['cont_rate'].round(1).astype(str) + '%',
            textposition='top center',
            marker=dict(color=continent_colors[cont_name]),
            showlegend=False
        ),
        row=row, col=col, secondary_y=True
    )
    fig.add_trace(
        go.Scatter(
            x=sub[year_col],
            y=sub['global_rate'],
            name='Global dismissed rate',
            text=sub['global_rate'].round(1).astype(str) + '%',
            textposition='bottom center',
            line=dict(color='black', dash='dash'),
            showlegend=(i==0)
        ),
        row=row, col=col, secondary_y=True
    )

    fig.update_xaxes(title_text='Year', row=row, col=col)
    fig.update_yaxes(ticksuffix='%', range=[0,100], secondary_y=False, row=row, col=col)
    fig.update_yaxes(showticklabels=False, title_text="", ticksuffix='%', range=[0,100], secondary_y=True, row=row, col=col)

fig.update_xaxes(tickangle=-45)
fig.update_layout(
    barmode='stack',
    bargap=0.1,
    height=400*rows,
    width=1600,
    margin=dict(t=100, b=80, l=60, r=200),
    legend=dict(
        orientation='v',
        x=1.02,
        y=1,
        xanchor='left',
        yanchor='top'
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("👉Next, we’ll break down the top five case types over the years to highlight which pathways dominate in each region.")
st.header("Top 5 Case Types Over Years by Region")
color_map = {
    "HC Decisions": "#636EFA",
    "Visa Officer Refusal": "#FF3C9E",
    "PRRA": "#00CC96",
    "RAD Decisions": "#AB63FA",
    "RPD Decisions": "#FFA15A"
}

st.markdown(f"""
- <span style="color:{color_map['RAD Decisions']}; font-weight: bold">RAD decisions</span> dominates <span style="color:{continent_colors['Africa']}">Africa</span>, <span style="color:{continent_colors['North America']}">North America</span> and <span style="color:{continent_colors['Caribbean']}">Caribbean</span> (≈50 – 70 % of cases), showing “refugee appeal” is the principal case type.  
- <span style="color:{continent_colors['Africa']}">Africa</span>, <span style="color:{continent_colors['North America']}">North America</span> and <span style="color:{continent_colors['Asia']}">Asia</span> have more variety (e.g. 
<span style="color:{color_map['HC Decisions']}"><b>HC decisions</b></span>, 
<span style="color:{color_map['Visa Officer Refusal']}"><b>visa-officer refusals</b></span>), whereas the 
<span style="color:{continent_colors['Caribbean']}">Caribbean</span> is almost entirely on 
<span style="color:{color_map['RAD Decisions']}"><b>RAD</b></span>.  
- <span style="color:{color_map['RAD Decisions']}"><b>RAD</b></span> share peaked during 2020–2021 for <span style="color:{continent_colors['Africa']}">Africa</span> and <span style="color:{continent_colors['North America']}">North America</span>, reflecting pandemic-era backlogs and expedited dismissals. For the <span style="color:{continent_colors['Caribbean']}">Caribbean</span>, it peaked in 2019.  
- In <span style="color:{continent_colors['Asia']}">Asia</span>, the majority of cases are 
<span style="color:{color_map['Visa Officer Refusal']}"><b>visa officer refusals</b></span>, which have increased year after year, peaking in 2023.
""", unsafe_allow_html=True)


agg = df.groupby(['continent','LIT Case Type Group Desc','LIT Leave Decision Date - Year'], as_index=False)['LIT Litigation Count'].sum()
top5 = agg.groupby(['continent','LIT Case Type Group Desc'])['LIT Litigation Count'].sum().reset_index().sort_values(['continent','LIT Litigation Count'], ascending=[True,False]).groupby('continent').head(5)
agg_f = agg.merge(top5[['continent','LIT Case Type Group Desc']], on=['continent','LIT Case Type Group Desc'])
selected = ['Africa','North America','Caribbean', 'Asia']
case_types = sorted(agg_f[agg_f['continent'].isin(selected)]['LIT Case Type Group Desc'].unique())
color_map = {ct: qualitative.Plotly[i % len(qualitative.Plotly)] for i, ct in enumerate(case_types)}

fig = make_subplots(rows=1, cols=4, shared_yaxes=True)


for i, cont_name in enumerate(selected):
    sub = agg_f[agg_f['continent'] == cont_name]
    pivot = sub.pivot_table(index='LIT Leave Decision Date - Year',
                            columns='LIT Case Type Group Desc',
                            values='LIT Litigation Count',
                            fill_value=0)
    years = pivot.index.tolist()
    for ct in case_types:
        if ct in pivot.columns:
            fig.add_trace(
                go.Bar(
                    y=years,
                    x=pivot[ct],
                    orientation='h',
                    name=ct,
                    legendgroup=ct,
                    showlegend=(i == 0),
                    marker_color=color_map[ct],
                    text=pivot[ct],
                    textposition='inside'
                ),
                row=1, col=i + 1
            )
    # Remove x-axis labels
    fig.update_xaxes(visible=False, row=1, col=i + 1)
    fig.update_yaxes(title_text='Year' if i == 0 else '', row=1, col=i + 1)

num_subplots = len(selected)
x_positions = [(i + 0.5) / num_subplots for i in range(num_subplots)]

for i, cont_name in enumerate(selected):
    fig.add_annotation(
        text=f"<span style='color:{continent_colors[cont_name]}'>{cont_name}</span>",
        xref="paper",
        yref="paper",
        x=x_positions[i],
        y=1.08,  # Adjust if needed: try 1.07 or 1.1 depending on layout
        showarrow=False,
        font=dict(size=14),
        align="center"
    )


fig.update_layout(barmode='stack', height=600, width=1200)
st.plotly_chart(fig, use_container_width=True)

st.markdown("👉Finally, let's zoom in on individual countries and reveal the top ten by case volume in these region.")
st.header("Top 10 Countries by Case Volume")

highlight_colors = {
    'Nigeria': '#d62728',
    'Congo, Democratic Republic of the': '#ff9896',
    'Mexico': '#1f77b4',
    'United States of America': '#aec7e8',
    'Haiti': '#8c564b',
    'Jamaica': '#c49c94',
    'India': "#165a16",
    'Iran': "#38ad20",
    "People's Republic of China": "#40db4a",
    'Pakistan': "#a2e59e"
}



st.markdown(f"""
- In <span style="color:{continent_colors['Africa']}">Africa</span>, 
  <strong><span style="color:{highlight_colors['Nigeria']}">Nigeria</span></strong> alone accounts for ~73% of the region’s litigation applications. 
  The next largest, <strong><span style="color:{highlight_colors['Congo, Democratic Republic of the']}">DR Congo</span></strong>, is only ~4%.  
- In <span style="color:{continent_colors['North America']}">North America</span>, 
  <strong><span style="color:{highlight_colors['Mexico']}">Mexico (50.2%)</span></strong> and 
  <strong><span style="color:{highlight_colors['United States of America']}">United States (22.6%)</span></strong> together account for over 70% of the litigation applications.  
- In <span style="color:{continent_colors['Caribbean']}">Caribbean</span>, 
  <strong><span style="color:{highlight_colors['Haiti']}">Haiti (64.8%)</span></strong> and 
  <strong><span style="color:{highlight_colors['Jamaica']}">Jamaica (21.3%)</span></strong> dominate the region’s litigation applications.  
- In <span style="color:{continent_colors['Asia']}">Asia</span>, the top contributors are 
  <strong><span style="color:{highlight_colors['India']}">India (34.4%)</span></strong>, 
  <strong><span style="color:{highlight_colors['Iran']}">Iran (22.7%)</span></strong>, 
  <strong><span style="color:{highlight_colors["People's Republic of China"]}">People’s Republic of China (16.2%)</span></strong>, and 
  <strong><span style="color:{highlight_colors['Pakistan']}">Pakistan (10.8%)</span></strong>.
""", unsafe_allow_html=True)


for cont_name in ['Africa', 'North America', 'Caribbean', 'Asia']:
    dfc = df[df['continent'] == cont_name]
    pc = (
        dfc
        .groupby('Country of Citizenship', as_index=False)['LIT Litigation Count']
        .sum()
        .sort_values('LIT Litigation Count', ascending=False)
        .head(10)
    )

    country_colors = [
        highlight_colors.get(country, "#cccccc") for country in pc['Country of Citizenship']
    ]

    fig = px.pie(
        pc,
        names='Country of Citizenship',
        values='LIT Litigation Count',
        title=f'{cont_name}: Top 10 Countries by Case Volume',
        hole=0.4,
        color_discrete_sequence=country_colors
    )

    fig.update_traces(
        textinfo='percent+label',
        textposition='outside',
        automargin=True
    )

    fig.update_layout(
        margin=dict(t=40, b=40, l=40, r=40),
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)