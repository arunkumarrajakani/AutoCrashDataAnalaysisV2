import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import './App.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend
);

const App = () => {
  const [states, setStates] = useState([]);
  const [cities, setCities] = useState([]);
  const [selectedState, setSelectedState] = useState('');
  const [selectedCity, setSelectedCity] = useState('');
  const [chartData, setChartData] = useState(null);
  const [selectedYear, setSelectedYear] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(null);
  const [selectedDay, setSelectedDay] = useState(null);
  const [selectedSeason, setSelectedSeason] = useState(null);

  const fetchAnalytics = async (state, city, year, month, day, season) => {
    const params = { state, city };
    if (year) params.year = year;
    if (month) params.month = month;
    if (day) params.day = day;
    if (season) params.season = season;

    const res = await axios.get('http://localhost:5000/api/analytics', { params });
    setChartData(res.data);
  };

  useEffect(() => {
    axios.get('http://localhost:5000/api/states').then(res => setStates(res.data));
  }, []);

  useEffect(() => {
    if (selectedState) {
      axios.get(`http://localhost:5000/api/cities?state=${selectedState}`).then(res => setCities(res.data));
    }
  }, [selectedState]);

  useEffect(() => {
    if (selectedState && selectedCity) {
      fetchAnalytics(selectedState, selectedCity, selectedYear, selectedMonth, selectedDay, selectedSeason);
    }
  }, [selectedState, selectedCity, selectedYear, selectedMonth, selectedDay, selectedSeason]);

  const handleReset = () => {
    setSelectedYear(null);
    setSelectedMonth(null);
    setSelectedDay(null);
    setSelectedSeason(null);
  };

  const handleDrill = (level, value) => {
    if (level === 'year') {
      setSelectedYear(value);
      setSelectedMonth(null);
      setSelectedDay(null);
    } else if (level === 'month') {
      setSelectedMonth(value);
      setSelectedDay(null);
    } else if (level === 'day') {
      setSelectedDay(value);
    } else if (level === 'season') {
      setSelectedSeason(value);
      setSelectedYear(null);
      setSelectedMonth(null);
      setSelectedDay(null);
    }
  };

  const createOptions = (label, drillLevel) => ({
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: false },
    },
    onClick: (e, elements) => {
      if (elements.length > 0) {
        const index = elements[0].index;
        let clickedLabel = chartData[drillLevel]?.labels?.[index];

        if (clickedLabel !== undefined) {
          if (drillLevel === 'years') handleDrill('year', parseInt(clickedLabel));
          if (drillLevel === 'months') handleDrill('month', parseInt(clickedLabel));
          if (drillLevel === 'days') handleDrill('day', parseInt(clickedLabel));
          if (drillLevel === 'seasons') handleDrill('season', clickedLabel);
        }
      }
    }
  });

  return (
    <div className="container">
      <h1>US Accident Dashboard</h1>
      <div className="dropdowns">
        <select value={selectedState} onChange={e => setSelectedState(e.target.value)}>
          <option value="">Select State</option>
          {states.map(state => (
            <option key={state} value={state}>{state}</option>
          ))}
        </select>

        <select value={selectedCity} onChange={e => setSelectedCity(e.target.value)}>
          <option value="">Select City</option>
          {cities.map(city => (
            <option key={city} value={city}>{city}</option>
          ))}
        </select>

        <button onClick={handleReset}>Reset Drilldown</button>
      </div>

      {chartData && (
        <>
          <h2>{selectedCity}, {selectedState}</h2>

          {chartData.years && <><h3>Yearly Accidents</h3><Bar data={chartData.years} options={createOptions('Yearly', 'years')} /></>}
          {selectedYear && chartData.months && <><h3>Monthly Accidents</h3><Bar data={chartData.months} options={createOptions('Monthly', 'months')} /></>}
          {selectedMonth && chartData.days && <><h3>Daily Accidents</h3><Bar data={chartData.days} options={createOptions('Daily', 'days')} /></>}
          {selectedDay && chartData.hours && <><h3>Hourly Accidents</h3><Line data={chartData.hours} options={createOptions('Hourly', 'hours')} /></>}

          <h3>Seasonal Accidents</h3>
          {chartData.seasons && <Bar data={chartData.seasons} options={createOptions('Seasonal', 'seasons')} />}
          {selectedSeason && chartData.months && <><h3>Season Breakdown - Monthly</h3><Bar data={chartData.months} options={createOptions('Monthly', 'months')} /></>}
        </>
      )}
    </div>
  );
};

export default App;
