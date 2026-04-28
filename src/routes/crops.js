const express = require('express')
const router = express.Router()
const User = require('../models/User')
const { getCropRecommendationsWithAI } = require('../services/geminiService')

// POST /api/crops/recommend
router.post('/crops/recommend', async (req, res) => {
  try {
    const { user_id } = req.body
    if (!user_id) return res.status(400).json({ success: false, error: 'user_id is required' })

    // Fetch user profile to personalize recommendations
    let userData = {}
    try {
      const user = await User.findById(user_id)
      if (user) userData = { location: user.location, farm_size: user.farm_size, primary_crops: user.primary_crops }
    } catch (_) {
      // Non-critical — continue with empty profile
    }

    let aiResult
    try {
      aiResult = await getCropRecommendationsWithAI(userData)
    } catch (aiErr) {
      console.error('Gemini AI error:', aiErr.message)
      return res.status(503).json({ success: false, error: 'AI service unavailable. Please check your GEMINI_API_KEY.' })
    }

    res.json({ success: true, data: aiResult })
  } catch (err) {
    console.error('Crop recommendation error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
