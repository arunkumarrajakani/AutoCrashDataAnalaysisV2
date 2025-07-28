from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sqlite3

app = Flask(__name__)
CORS(app)

def get_data(state, city):
    conn = sqlite3.connect("accidents.db")
    df = pd.read_sql("SELECT * FROM accidents WHERE state=? AND city=?", conn, params=(state, city))
    conn.close()
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])
    return df

def serialize_chart(df, group_col, label_name='Accidents'):
    chart = df[group_col].value_counts().sort_index().reset_index()
    chart.columns = ['label', 'value']
    return {
        "labels": chart['label'].astype(str).tolist(),
        "datasets": [{
            "label": label_name,
            "data": chart['value'].tolist(),
            "backgroundColor": "rgba(75, 192, 192, 0.6)",
            "borderColor": "rgba(75, 192, 192, 1)",
            "borderWidth": 1
        }]
    }

@app.route("/api/states")
def get_states():
    conn = sqlite3.connect("accidents.db")
    df = pd.read_sql("SELECT DISTINCT state FROM accidents WHERE state IS NOT NULL ORDER BY state", conn)
    conn.close()
    return jsonify(df['state'].dropna().unique().tolist())

@app.route("/api/cities")
def get_cities():
    state = request.args.get("state")
    conn = sqlite3.connect("accidents.db")
    df = pd.read_sql("SELECT DISTINCT city FROM accidents WHERE state=? AND city IS NOT NULL ORDER BY city", conn, params=(state,))
    conn.close()
    return jsonify(df['city'].dropna().unique().tolist())

@app.route("/api/analytics")
def get_analytics():
    state = request.args.get("state")
    city = request.args.get("city")
    year = request.args.get("year")
    month = request.args.get("month")
    day = request.args.get("day")
    season = request.args.get("season")

    df = get_data(state, city)

    if season:
        season_months = {
            'Winter': [12, 1, 2],
            'Spring': [3, 4, 5],
            'Summer': [6, 7, 8],
            'Autumn': [9, 10, 11]
        }
        df = df[df['start_time'].dt.month.isin(season_months.get(season, []))]
    if year:
        df = df[df['start_time'].dt.year == int(year)]
    if month:
        df = df[df['start_time'].dt.month == int(month)]
    if day:
        df = df[df['start_time'].dt.day == int(day)]

    df['year'] = df['start_time'].dt.year
    df['month'] = df['start_time'].dt.month
    df['day'] = df['start_time'].dt.day
    df['hour'] = df['start_time'].dt.hour
    df['weekday'] = df['start_time'].dt.day_name()

    def get_season(month):
        if month in [12, 1, 2]: return 'Winter'
        if month in [3, 4, 5]: return 'Spring'
        if month in [6, 7, 8]: return 'Summer'
        return 'Autumn'
    df['season'] = df['month'].apply(get_season)

    response = {
        "years": serialize_chart(df, 'year'),
        "months": serialize_chart(df, 'month'),
        "days": serialize_chart(df, 'day'),
        "hours": serialize_chart(df, 'hour'),
        "weekdays": serialize_chart(df, 'weekday'),
        "seasons": serialize_chart(df, 'season')
    }
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
