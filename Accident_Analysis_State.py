import pandas as pd
import streamlit as st
import altair as alt

# Load the CSV file
file_path = 'cleaned_crash_data.csv'
df = pd.read_csv(file_path)

# Convert date columns to datetime for analysis
df['start_time'] = pd.to_datetime(df['start_time'])
df['end_time'] = pd.to_datetime(df['end_time'])

# Extract time components
df['Year'] = df['start_time'].dt.year
df['Month'] = df['start_time'].dt.month
df['Day'] = df['start_time'].dt.day
df['Hour'] = df['start_time'].dt.hour
df['Weekday'] = df['start_time'].dt.day_name()

# Define a function to classify season based on month
def get_season(month):
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Spring'
    elif month in [6, 7, 8]:
        return 'Summer'
    else:
        return 'Autumn'

df['Season'] = df['Month'].apply(get_season)

# Streamlit App
st.title("US Accident Data Analysis")

# Overall US accident trend
st.header("📈 Overall US Accident Trends")

us_yearly_summary = df.groupby('Year').size().reset_index(name='Accident_Count')
us_chart = alt.Chart(us_yearly_summary).mark_line(point=True).encode(
    x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0)),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count (K)', format='~s'))
).properties(width=700, height=400)
st.altair_chart(us_chart, use_container_width=True)

# State-wise accident comparison
st.header("📊 State-wise Accident Distribution")

state_summary = df['state'].value_counts().reset_index()
state_summary.columns = ['State', 'Accident_Count']
state_chart = alt.Chart(state_summary).mark_bar().encode(
    x=alt.X('State:N', sort='-y'),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count', format='~s')),
    tooltip=['State', 'Accident_Count']
).properties(width=800, height=400)
st.altair_chart(state_chart, use_container_width=True)

# State selection
st.header("📍 Drill-down by State and City")
state_list = sorted(df['state'].dropna().unique())
selected_state = st.selectbox("Select a State", state_list)

# City selection based on state
filtered_df = df[df['state'] == selected_state]
city_list = sorted(filtered_df['city'].dropna().unique())
selected_city = st.selectbox("Select a City", city_list)

# Filtered data for selected city
city_data = filtered_df[filtered_df['city'] == selected_city]

st.subheader(f"Analytics for {selected_city}, {selected_state}")

# Day of the week analysis
weekday_counts = city_data['Weekday'].value_counts().reset_index()
weekday_counts.columns = ['Weekday', 'count']
st.bar_chart(data=weekday_counts, x='Weekday', y='count', use_container_width=True)

# Hour of the day analysis
hourly_counts = city_data['Hour'].value_counts().sort_index().reset_index()
hourly_counts.columns = ['Hour', 'count']
st.line_chart(data=hourly_counts, x='Hour', y='count', use_container_width=True)

# Street-level analysis
if 'street' in city_data.columns:
    top_streets = city_data['street'].value_counts().head(10).reset_index()
    top_streets.columns = ['Street', 'count']
    st.write("Top 10 Streets with Most Accidents")
    st.bar_chart(data=top_streets, x='Street', y='count', use_container_width=True)

# Yearly trend
yearly_summary = city_data.groupby('Year').size().reset_index(name='Accident_Count')
chart = alt.Chart(yearly_summary).mark_line(point=True).encode(
    x=alt.X('Year:O', axis=alt.Axis(title='Year', labelAngle=0)),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count (K)', format='~s'))
).properties(width=700, height=400)
st.altair_chart(chart, use_container_width=True)

# Monthly trend
monthly_summary = city_data.groupby('Month').size().reset_index(name='Accident_Count')
chart_month = alt.Chart(monthly_summary).mark_line(point=True).encode(
    x=alt.X('Month:O', axis=alt.Axis(title='Month')),
    y=alt.Y('Accident_Count', axis=alt.Axis(title='Accident Count (K)', format='~s'))
).properties(width=700, height=400)
st.altair_chart(chart_month, use_container_width=True)

# Seasonal trend
seasonal_summary = city_data['Season'].value_counts().reset_index()
seasonal_summary.columns = ['Season', 'count']
st.bar_chart(data=seasonal_summary, x='Season', y='count', use_container_width=True)
