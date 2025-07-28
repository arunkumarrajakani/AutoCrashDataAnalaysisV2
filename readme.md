# Accident Analytics System (v2)

An interactive data analytics system that ingests, stores, and visualizes real-time accident data from multiple US cities using an automated ETL process, a Flask API backend, and a React.js dashboard with drill-down capabilities.

---

## 1. 📁 Database Creation (`accidents.db`)

### Schema

**Table: **``

| Column                                     | Type        |
| ------------------------------------------ | ----------- |
| id                                         | TEXT (PK)   |
| start\_time, end\_time                     | DATETIME    |
| start\_lat, start\_lng, end\_lat, end\_lng | FLOAT       |
| distance(mi), severity                     | FLOAT / INT |
| city, state, country, timezone             | TEXT        |
| street, description                        | TEXT        |

**Table: **``

| Column         | Type |
| -------------- | ---- |
| run\_time      | TEXT |
| city           | TEXT |
| state          | TEXT |
| source         | TEXT |
| inserted\_rows | INT  |

You can create this with SQLite manually or using `pandas.to_sql()` from the ETL script.

---

## 2. 🚜 Load Data to Database (ETL Script)

### Key File: `etl_loader.py`

### Cities Integrated:

- **Austin**: `https://data.austintexas.gov/resource/y2wy-tgr5.json`
- **New York**: `https://data.cityofnewyork.us/resource/h9gi-nx95.json`
- **Montgomery**: `https://data.montgomerycountymd.gov/resource/mmzv-x632.json`
- **Chicago**: `https://data.cityofchicago.org/resource/85ca-t3if.json`

### ETL Highlights:

- Paginated API call using `$limit` & `$offset`
- Date filter using `$where` for recent data (e.g. 2024+, 2025)
- Source field mapping to unified schema
- Deduplication using `id`
- Auto logging into `etl_logs`

### To Run:

```bash
pip install pandas sqlalchemy requests
python etl_loader.py
```

---

## 3. 🚧 API Integration (Flask + SQLite)

### Flask Setup

```bash
pip install flask flask-cors flask_sqlalchemy
```

### Flask Endpoints

| Endpoint                                                      | Description                 |
| ------------------------------------------------------------- | --------------------------- |
| `/api/states`                                                 | List of distinct states     |
| `/api/cities?state=XX`                                        | List of cities in the state |
| `/api/analytics?state=XX&city=YY[&year=&month=&day=&season=]` | Drillable analytics         |

### JSON Response Structure

- `years`: { labels, datasets }
- `months`, `days`, `hours`, `seasons`: same format
- All responses are JSON serializable and datetime-safe

---

## 4. 🚀 Accident Backend (Flask)

### Key File: `app.py`

- CORS enabled
- Uses pandas and SQLAlchemy
- Automatically converts and groups data
- Supports drilldowns:
  - Year → Month → Day → Hour
  - Season → Month → Day → Hour

### To Start:

```bash
python app.py
```

Default port is `http://localhost:5000`

---

## 5. 📈 Accident Dashboard (React.js)

### Dependencies

```bash
npm install axios chart.js react-chartjs-2
```

### Features

- State → City dropdown
- Bar and Line charts for:
  - Yearly, Monthly, Daily, Hourly, Seasonal
- Click any bar to drill down
- Reset button to clear selection
- Live updates from backend

### To Start:

```bash
npm start
```

Runs at: `http://localhost:3000`

---

## 🚜 Project Outcome

- ✅ Live dashboard for accident trends across US cities
- ✅ Multiple drill-down visualizations
- ✅ Dynamic ETL integration from public APIs
- ✅ Modular architecture for future city integrations

Let me know if you'd like a packaged ZIP, Docker container, or cloud deployment steps!

