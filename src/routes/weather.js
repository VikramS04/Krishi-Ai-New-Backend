const express = require('express')
const router = express.Router()
const { getCurrentWeather, getWeatherForecast, getAgriculturalAdvice } = require('../services/weatherService')

// GET /api/weather/current/:location
router.get('/weather/current/:location', async (req, res) => {
  try {
    const location = decodeURIComponent(req.params.location)
    const data = await getCurrentWeather(location)
    const agricultural_advice = getAgriculturalAdvice(data)
    res.json({ success: true, data: { ...data, agricultural_advice } })
  } catch (err) {
    if (err.response?.status === 404) return res.status(404).json({ success: false, error: `Location "${req.params.location}" not found. Try a major city name.` })
    if (err.response?.status === 401) return res.status(401).json({ success: false, error: 'Invalid OpenWeatherMap API key. Please check your OPENWEATHER_API_KEY.' })
    console.error('Weather error:', err.message)
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/weather/forecast/:location?days=7
router.get('/weather/forecast/:location', async (req, res) => {
  try {
    const location = decodeURIComponent(req.params.location)
    const days = Math.min(parseInt(req.query.days) || 7, 7) // max 7 days on free tier
    const data = await getWeatherForecast(location, days)
    res.json({ success: true, data })
  } catch (err) {
    if (err.response?.status === 404) return res.status(404).json({ success: false, error: `Location "${req.params.location}" not found.` })
    if (err.response?.status === 401) return res.status(401).json({ success: false, error: 'Invalid OpenWeatherMap API key.' })
    console.error('Forecast error:', err.message)
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/weather/alerts/:location  (agricultural alerts based on current weather)
router.get('/weather/alerts/:location', async (req, res) => {
  try {
    const location = decodeURIComponent(req.params.location)
    const weather = await getCurrentWeather(location)
    const alerts = getAgriculturalAdvice(weather)

    const severity = weather.temperature > 40 || weather.rainfall > 50 ? 'High'
      : weather.temperature > 35 || weather.humidity > 85 ? 'Medium' : 'Low'

    res.json({
      success: true,
      location: weather.location,
      alerts,
      severity,
      current_conditions: { temperature: weather.temperature, humidity: weather.humidity, rainfall: weather.rainfall },
    })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
