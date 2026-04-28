const axios = require('axios')

const BASE_URL = 'https://api.openweathermap.org/data/2.5'
const API_KEY = process.env.OPENWEATHER_API_KEY

// ─── Current Weather ──────────────────────────────────────────────────────────
const getCurrentWeather = async (location) => {
  const res = await axios.get(`${BASE_URL}/weather`, {
    params: { q: location, appid: API_KEY, units: 'metric' },
    timeout: 8000,
  })
  const d = res.data
  return {
    location: d.name,
    country: d.sys.country,
    temperature: Math.round(d.main.temp),
    feels_like: Math.round(d.main.feels_like),
    condition: d.weather[0].description,
    condition_main: d.weather[0].main,
    icon: d.weather[0].icon,
    humidity: d.main.humidity,
    wind_speed: Math.round(d.wind.speed * 3.6), // m/s to km/h
    wind_direction: d.wind.deg,
    pressure: d.main.pressure,
    visibility: d.visibility ? Math.round(d.visibility / 1000) : null,
    rainfall: d.rain ? (d.rain['1h'] || 0) : 0,
    uv_index: null, // requires separate call on free tier
    clouds: d.clouds.all,
    sunrise: new Date(d.sys.sunrise * 1000).toISOString(),
    sunset: new Date(d.sys.sunset * 1000).toISOString(),
  }
}

// ─── 7-Day Forecast ───────────────────────────────────────────────────────────
const getWeatherForecast = async (location, days = 7) => {
  const res = await axios.get(`${BASE_URL}/forecast`, {
    params: { q: location, appid: API_KEY, units: 'metric', cnt: days * 8 },
    timeout: 8000,
  })

  // Aggregate 3h intervals into daily summaries
  const dailyMap = {}
  res.data.list.forEach((item) => {
    const date = item.dt_txt.split(' ')[0]
    if (!dailyMap[date]) {
      dailyMap[date] = { temps: [], humidity: [], rainfall: 0, condition: item.weather[0].description, icon: item.weather[0].icon }
    }
    dailyMap[date].temps.push(item.main.temp)
    dailyMap[date].humidity.push(item.main.humidity)
    dailyMap[date].rainfall += item.rain ? (item.rain['3h'] || 0) : 0
  })

  return Object.entries(dailyMap).slice(0, days).map(([date, data]) => ({
    date,
    temperature: Math.round(data.temps.reduce((a, b) => a + b, 0) / data.temps.length),
    temp_max: Math.round(Math.max(...data.temps)),
    temp_min: Math.round(Math.min(...data.temps)),
    humidity: Math.round(data.humidity.reduce((a, b) => a + b, 0) / data.humidity.length),
    rainfall: Math.round(data.rainfall * 10) / 10,
    condition: data.condition,
    icon: data.icon,
  }))
}

// ─── Agricultural Advice based on weather ────────────────────────────────────
const getAgriculturalAdvice = (weatherData) => {
  const advice = []
  const { temperature, humidity, rainfall, condition_main } = weatherData

  if (temperature > 35) advice.push('High temperature alert — irrigate crops early morning or evening to reduce heat stress.')
  if (temperature < 10) advice.push('Cold weather alert — protect frost-sensitive crops with covers or mulching.')
  if (humidity > 80) advice.push('High humidity increases fungal disease risk — consider preventive fungicide application.')
  if (humidity < 30) advice.push('Low humidity — increase irrigation frequency to prevent crop wilting.')
  if (rainfall > 20) advice.push('Heavy rainfall expected — ensure proper drainage to avoid waterlogging.')
  if (condition_main === 'Clear' && temperature > 25) advice.push('Clear sunny day — ideal for spraying pesticides or fertilizers.')

  return advice.length > 0 ? advice : ['Weather conditions are favorable for most farming activities.']
}

module.exports = { getCurrentWeather, getWeatherForecast, getAgriculturalAdvice }
