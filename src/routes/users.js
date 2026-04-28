const express = require('express')
const router = express.Router()
const User = require('../models/User')

// GET /api/users
router.get('/users', async (req, res) => {
  try {
    const users = await User.find().select('-__v').sort({ createdAt: -1 })
    res.json({ success: true, count: users.length, data: users })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/users
router.post('/users', async (req, res) => {
  try {
    const { username, email, full_name, phone, location, farm_size, primary_crops, language_preference } = req.body
    if (!username || !email) return res.status(400).json({ success: false, error: 'Username and email are required' })

    const existing = await User.findOne({ $or: [{ email }, { username }] })
    if (existing) return res.status(409).json({ success: false, error: 'Username or email already exists' })

    const user = await User.create({ username, email, full_name, phone, location, farm_size, primary_crops, language_preference })
    res.status(201).json({ success: true, data: user })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/users/:id
router.get('/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id).select('-__v')
    if (!user) return res.status(404).json({ success: false, error: 'User not found' })
    res.json({ success: true, data: user })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// PUT /api/users/:id
router.put('/users/:id', async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true }).select('-__v')
    if (!user) return res.status(404).json({ success: false, error: 'User not found' })
    res.json({ success: true, data: user })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// DELETE /api/users/:id
router.delete('/users/:id', async (req, res) => {
  try {
    const user = await User.findByIdAndDelete(req.params.id)
    if (!user) return res.status(404).json({ success: false, error: 'User not found' })
    res.json({ success: true, message: 'User deleted' })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
