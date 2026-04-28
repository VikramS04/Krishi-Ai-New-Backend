const express = require('express')
const router = express.Router()
const SoilAnalysis = require('../models/SoilAnalysis')
const { analyzeSoilWithAI } = require('../services/geminiService')

// POST /api/soil/analyze
router.post('/soil/analyze', async (req, res) => {
  try {
    const { user_id, location, ph_level, nitrogen, phosphorus, potassium, organic_matter, moisture_content } = req.body

    if (!user_id) return res.status(400).json({ success: false, error: 'user_id is required' })

    // Validate at least some soil parameters exist
    if (!ph_level && !nitrogen && !phosphorus) {
      return res.status(400).json({ success: false, error: 'Please provide at least pH level, nitrogen, and phosphorus values' })
    }

    const soilInput = { location, ph_level, nitrogen, phosphorus, potassium, organic_matter, moisture_content }

    // Call Gemini AI for analysis
    let aiResult
    try {
      aiResult = await analyzeSoilWithAI(soilInput)
    } catch (aiErr) {
      console.error('Gemini AI error:', aiErr.message)
      return res.status(503).json({ success: false, error: 'AI analysis service unavailable. Please check your GEMINI_API_KEY.' })
    }

    // Save to MongoDB
    const analysis = await SoilAnalysis.create({
      user_id,
      ...soilInput,
      health_score: aiResult.health_score,
      soil_type: aiResult.soil_type,
      recommendations: aiResult.recommendations,
      suitable_crops: aiResult.suitable_crops,
      raw_ai_response: JSON.stringify(aiResult),
    })

    res.status(201).json({
      success: true,
      data: {
        _id: analysis._id,
        health_score: aiResult.health_score,
        soil_type: aiResult.soil_type,
        summary: aiResult.summary,
      },
      recommendations: aiResult.recommendations,
      suitable_crops: aiResult.suitable_crops,
    })
  } catch (err) {
    console.error('Soil analysis error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/soil/history/:user_id
router.get('/soil/history/:user_id', async (req, res) => {
  try {
    const analyses = await SoilAnalysis.find({ user_id: req.params.user_id })
      .select('-raw_ai_response -__v')
      .sort({ createdAt: -1 })
      .limit(10)
    res.json({ success: true, count: analyses.length, data: analyses })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/soil/:id
router.get('/soil/:id', async (req, res) => {
  try {
    const analysis = await SoilAnalysis.findById(req.params.id).select('-raw_ai_response -__v')
    if (!analysis) return res.status(404).json({ success: false, error: 'Analysis not found' })
    res.json({ success: true, data: analysis })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
