const express = require('express')
const router = express.Router()
const multer = require('multer')
const DiseaseDetection = require('../models/DiseaseDetection')
const { detectDiseaseWithAI, detectDiseaseFromImageWithAI } = require('../services/geminiService')

// Multer — store image in memory (no disk, Vercel serverless compatible)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) cb(null, true)
    else cb(new Error('Only image files are allowed'), false)
  },
})

// POST /api/disease/detect  (text-based, with optional symptoms)
router.post('/disease/detect', async (req, res) => {
  try {
    const { user_id, crop_type, symptoms } = req.body
    if (!user_id || !crop_type) return res.status(400).json({ success: false, error: 'user_id and crop_type are required' })

    let aiResult
    try {
      aiResult = await detectDiseaseWithAI(crop_type, symptoms)
    } catch (aiErr) {
      console.error('Gemini AI error:', aiErr.message)
      return res.status(503).json({ success: false, error: 'AI service unavailable. Please check your GEMINI_API_KEY.' })
    }

    const detection = await DiseaseDetection.create({
      user_id,
      crop_type,
      detection_result: aiResult,
      raw_ai_response: JSON.stringify(aiResult),
    })

    res.status(201).json({
      success: true,
      detection_result: aiResult,
      record_id: detection._id,
    })
  } catch (err) {
    console.error('Disease detection error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/disease/upload  (image upload → Gemini Vision)
router.post('/disease/upload', upload.single('image'), async (req, res) => {
  try {
    const { user_id, crop_type, symptoms } = req.body
    if (!user_id || !crop_type) return res.status(400).json({ success: false, error: 'user_id and crop_type are required' })
    if (!req.file) return res.status(400).json({ success: false, error: 'Image file is required' })

    const imageBase64 = req.file.buffer.toString('base64')
    const mimeType = req.file.mimetype

    let aiResult
    try {
      aiResult = await detectDiseaseFromImageWithAI(crop_type, imageBase64, mimeType)
    } catch (aiErr) {
      console.error('Gemini Vision error:', aiErr.message)
      // Fallback to text-based detection
      aiResult = await detectDiseaseWithAI(crop_type, symptoms)
    }

    const detection = await DiseaseDetection.create({
      user_id,
      crop_type,
      image_base64: imageBase64.substring(0, 100) + '...', // store truncated ref only
      detection_result: aiResult,
      raw_ai_response: JSON.stringify(aiResult),
    })

    res.status(201).json({
      success: true,
      detection_result: aiResult,
      record_id: detection._id,
    })
  } catch (err) {
    console.error('Image upload detection error:', err)
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/disease/history/:user_id
router.get('/disease/history/:user_id', async (req, res) => {
  try {
    const detections = await DiseaseDetection.find({ user_id: req.params.user_id })
      .select('-raw_ai_response -image_base64 -__v')
      .sort({ createdAt: -1 })
      .limit(10)
    res.json({ success: true, count: detections.length, data: detections })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
