// src/App.js
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

  useEffect(() => {
    axios.get('http://localhost:5000/api/states').then(res => setStates(res.data));
  }, []);

  useEffect(() => {
    if (selectedState) {
      axios.get(http://localhost:5000/api/cities?state=${selectedState}).then(res => setCities(res.data));
    }
  }, [selectedState]);

  useEffect(() => {
    if (selectedCity) {
      axios.get(http://localhost:5000/api/analytics?state=${selectedState}&city=${selectedCity})
        .then(res => setChartData(res.data));
    }
  }, [selectedCity]);

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
      </div>

      {chartData && (
        <>
          <h2>{selectedCity}, {selectedState} - Weekly Accidents</h2>
          <Bar data={chartData.weekdays} options={{ responsive: true }} />

          <h2>Hourly Distribution</h2>
          <Line data={chartData.hours} options={{ responsive: true }} />

          <h2>Monthly Accidents</h2>
          <Bar data={chartData.months} options={{ responsive: true }} />

          <h2>Seasonal Distribution</h2>
          <Bar data={chartData.seasons} options={{ responsive: true }} />

          <h2>Yearly Accidents</h2>
          <Bar data={chartData.years} options={{ responsive: true }} />
        </>
      )}
    </div>
  );
};

export default App;

