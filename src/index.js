require('dotenv').config()
const express = require('express')
const cors = require('cors')
const rateLimit = require('express-rate-limit')
const connectDB = require('../config/db')
const errorHandler = require('./middleware/errorHandler')

// Route imports
const userRoutes = require('./routes/users')
const soilRoutes = require('./routes/soil')
const cropRoutes = require('./routes/crops')
const diseaseRoutes = require('./routes/disease')
const weatherRoutes = require('./routes/weather')
const communityRoutes = require('./routes/community')

const app = express()

// ─── Connect Database ─────────────────────────────────────────────────────────
connectDB()

// ─── Middleware ───────────────────────────────────────────────────────────────
app.use(cors({ origin: '*', methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'], allowedHeaders: ['Content-Type', 'Authorization'] }))

app.use(express.json({ limit: '15mb' })) // Allow larger payloads for base64 images
app.use(express.urlencoded({ extended: true, limit: '15mb' }))

// Rate limiting — prevent abuse on AI endpoints
const aiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 20,
  message: { success: false, error: 'Too many requests. Please wait a moment and try again.' },
  standardHeaders: true,
  legacyHeaders: false,
})

app.use('/api/soil/analyze', aiLimiter)
app.use('/api/disease/detect', aiLimiter)
app.use('/api/disease/upload', aiLimiter)
app.use('/api/crops/recommend', aiLimiter)

// ─── Routes ───────────────────────────────────────────────────────────────────
app.use('/api', userRoutes)
app.use('/api', soilRoutes)
app.use('/api', cropRoutes)
app.use('/api', diseaseRoutes)
app.use('/api', weatherRoutes)
app.use('/api', communityRoutes)

// ─── Health & Docs ────────────────────────────────────────────────────────────
app.get('/', (req, res) => res.json({ message: '🌱 KrishiAi API v2.0 is running', status: 'healthy' }))

app.get('/api/health', (req, res) => {
  res.json({
    success: true,
    status: 'healthy',
    version: '2.0.0',
    database: 'MongoDB Atlas',
    ai: 'Google Gemini 1.5 Flash',
    weather: 'OpenWeatherMap',
    timestamp: new Date().toISOString(),
  })
})

app.get('/api/docs', (req, res) => {
  res.json({
    title: 'KrishiAi Agriculture Platform API v2',
    version: '2.0.0',
    stack: 'Node.js + Express + MongoDB + Gemini AI',
    endpoints: {
      Users: {
        'GET    /api/users': 'List all users',
        'POST   /api/users': 'Create user { username, email, full_name, phone, location, farm_size, primary_crops }',
        'GET    /api/users/:id': 'Get user by ID',
        'PUT    /api/users/:id': 'Update user',
        'DELETE /api/users/:id': 'Delete user',
      },
      Soil: {
        'POST /api/soil/analyze': 'AI soil analysis { user_id, location, ph_level, nitrogen, phosphorus, potassium, organic_matter, moisture_content }',
        'GET  /api/soil/history/:user_id': 'Soil analysis history',
        'GET  /api/soil/:id': 'Single analysis',
      },
      Crops: {
        'POST /api/crops/recommend': 'AI crop recommendations { user_id }',
      },
      Disease: {
        'POST /api/disease/detect': 'Text-based disease detection { user_id, crop_type, symptoms? }',
        'POST /api/disease/upload': 'Image-based detection (multipart/form-data: user_id, crop_type, image)',
        'GET  /api/disease/history/:user_id': 'Detection history',
      },
      Weather: {
        'GET /api/weather/current/:location': 'Current weather + farming advice',
        'GET /api/weather/forecast/:location?days=7': '7-day forecast',
        'GET /api/weather/alerts/:location': 'Agricultural weather alerts',
      },
      Community: {
        'GET  /api/community/posts?language=english&category=Soil Health': 'List posts',
        'POST /api/community/posts': 'Create post { user_id, title, content, category, language }',
        'GET  /api/community/posts/:id': 'Get post',
        'POST /api/community/posts/:id/like': 'Like/unlike { user_id }',
        'POST /api/community/posts/:id/comments': 'Add comment { user_id, content }',
        'GET  /api/community/trending': 'Trending posts',
        'GET  /api/community/search?q=wheat': 'Search posts',
      },
    },
  })
})

// ─── 404 Handler ─────────────────────────────────────────────────────────────
app.use('*', (req, res) => {
  res.status(404).json({ success: false, error: `Route ${req.method} ${req.originalUrl} not found` })
})

// ─── Error Handler ────────────────────────────────────────────────────────────
app.use(errorHandler)

// ─── Start Server ─────────────────────────────────────────────────────────────
const PORT = process.env.PORT || 5001
app.listen(PORT, () => {
  console.log(`🚀 KrishiAi API v2 running on http://localhost:${PORT}`)
  console.log(`📋 Docs: http://localhost:${PORT}/api/docs`)
})

module.exports = app
