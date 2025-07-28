
import pandas as pd
import streamlit as st
import altair as alt
from sqlalchemy import create_engine

# Connect to SQLite database
engine = create_engine('sqlite:///accidents.db')

# Title
st.title("US Accident Data Analysis (Optimized)")

# Step 1: Get State list (only distinct states)
state_query = "SELECT DISTINCT state FROM accidents WHERE state IS NOT NULL ORDER BY state"
state_list = pd.read_sql(state_query, con=engine)['state'].tolist()
selected_state = st.selectbox("Select a State", state_list)

# Step 2: Get City list for selected state
city_query = f"SELECT DISTINCT city FROM accidents WHERE state = '{selected_state}' AND city IS NOT NULL ORDER BY city"
city_list = pd.read_sql(city_query, con=engine)['city'].tolist()
selected_city = st.selectbox("Select a City", city_list)

# Step 3: Pull city-specific data (only necessary columns)
data_query = f"""
SELECT start_time, end_time, street
FROM accidents
WHERE state = '{selected_state}' AND city = '{selected_city}'
"""
city_data = pd.read_sql(data_query, con=engine, parse_dates=['start_time', 'end_time'])

# Extract datetime components
city_data['Year'] = city_data['start_time'].dt.year
city_data['Month'] = city_data['start_time'].dt.month
city_data['Day'] = city_data['start_time'].dt.day
city_data['Hour'] = city_data['start_time'].dt.hour
city_data['Weekday'] = city_data['start_time'].dt.day_name()

# Add season
def get_season(month):
    return (
        'Winter' if month in [12, 1, 2] else
        'Spring' if month in [3, 4, 5] else
        'Summer' if month in [6, 7, 8] else
        'Autumn'
    )

city_data['Season'] = city_data['Month'].apply(get_season)

# Display Header
st.subheader(f"Analytics for {selected_city}, {selected_state}")

# Weekday analysis
weekday_counts = city_data['Weekday'].value_counts().reset_index()
weekday_counts.columns = ['Weekday', 'count']
st.bar_chart(data=weekday_counts, x='Weekday', y='count', use_container_width=True)

# Hourly analysis
hourly_counts = city_data['Hour'].value_counts().sort_index().reset_index()
hourly_counts.columns = ['Hour', 'count']
st.line_chart(data=hourly_counts, x='Hour', y='count', use_container_width=True)

# Street-level
if 'street' in city_data.columns:
    top_streets = city_data['street'].value_counts().head(10).reset_index()
    top_streets.columns = ['Street', 'count']
    st.write("Top 10 Streets with Most Accidents")
    st.bar_chart(data=top_streets, x='Street', y='count', use_container_width=True)

# Yearly trend
yearly_summary = city_data.groupby('Year').size().reset_index(name='Accident_Count')
chart = alt.Chart(yearly_summary).mark_line(point=True).encode(
    x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0)),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count', format='~s'))
).properties(width=700, height=400)
st.altair_chart(chart, use_container_width=True)

# Monthly trend
monthly_summary = city_data.groupby('Month').size().reset_index(name='Accident_Count')
chart_month = alt.Chart(monthly_summary).mark_line(point=True).encode(
    x=alt.X('Month:O', axis=alt.Axis(title='Month')),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count', format='~s'))
).properties(width=700, height=400)
st.altair_chart(chart_month, use_container_width=True)

# Seasonal trend
seasonal_summary = city_data['Season'].value_counts().reset_index()
seasonal_summary.columns = ['Season', 'count']
st.bar_chart(data=seasonal_summary, x='Season', y='count', use_container_width=True)
