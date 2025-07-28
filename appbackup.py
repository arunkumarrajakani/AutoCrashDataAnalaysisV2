from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pandas as pd

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


def get_db_connection():
    conn = sqlite3.connect('accidents.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/states')
def get_states():
    conn = get_db_connection()
    query = "SELECT DISTINCT state FROM accidents WHERE state IS NOT NULL ORDER BY state"
    states = [row['state'] for row in conn.execute(query).fetchall()]
    conn.close()
    return jsonify(states)


@app.route('/api/cities')
def get_cities():
    state = request.args.get('state')
    conn = get_db_connection()
    query = "SELECT DISTINCT city FROM accidents WHERE state = ? AND city IS NOT NULL ORDER BY city"
    cities = [row['city'] for row in conn.execute(query, (state,)).fetchall()]
    conn.close()
    return jsonify(cities)


@app.route('/api/analytics')
def get_analytics():
    state = request.args.get('state')
    city = request.args.get('city')
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM accidents WHERE state = ? AND city = ?", conn, params=(state, city)
    )
    conn.close()

    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce')
    df = df.dropna(subset=['start_time'])
    df['Year'] = df['start_time'].dt.year
    df['Month'] = df['start_time'].dt.month
    df['Hour'] = df['start_time'].dt.hour
    df['Weekday'] = df['start_time'].dt.day_name()

    def get_season(month):
        return ('Winter' if month in [12, 1, 2] else
                'Spring' if month in [3, 4, 5] else
                'Summer' if month in [6, 7, 8] else
                'Autumn')
    df['Season'] = df['Month'].apply(get_season)

    def chart_format(series, label='Accidents'):
        return {
        "labels": [str(k) for k in series.index.tolist()],
        "datasets": [{
            "label": label,
            "data": [int(v) for v in series.values.tolist()],
            "backgroundColor": "rgba(75, 192, 192, 0.6)",
            "borderColor": "rgba(75, 192, 192, 1)",
            "borderWidth": 1
        }]
    }

    response = {
        "hours": chart_format(df['Hour'].value_counts().sort_index()),
        "months": chart_format(df['Month'].value_counts().sort_index()),
        "years": chart_format(df['Year'].value_counts().sort_index()),
        "weekdays": chart_format(df['Weekday'].value_counts()),
        "seasons": chart_format(df['Season'].value_counts())
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
