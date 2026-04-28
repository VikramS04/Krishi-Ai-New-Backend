const express = require('express')
const crypto = require('crypto')
const router = express.Router()
const User = require('../models/User')

const hashPassword = (password, salt = crypto.randomBytes(16).toString('hex')) => {
  const hash = crypto.scryptSync(password, salt, 64).toString('hex')
  return `${salt}:${hash}`
}

const verifyPassword = (password, storedHash) => {
  if (!storedHash || !storedHash.includes(':')) return false

  const [salt, savedHash] = storedHash.split(':')
  const derivedHash = crypto.scryptSync(password, salt, 64)
  const savedHashBuffer = Buffer.from(savedHash, 'hex')

  return savedHashBuffer.length === derivedHash.length
    && crypto.timingSafeEqual(savedHashBuffer, derivedHash)
}

const sanitizeUser = (user) => {
  const userData = user.toObject ? user.toObject() : { ...user }
  delete userData.password_hash
  delete userData.__v
  return userData
}

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
    const { username, email, password, full_name, phone, location, farm_size, primary_crops, language_preference } = req.body
    if (!username || !email || !password) return res.status(400).json({ success: false, error: 'Username, email, and password are required' })
    if (password.length < 8) return res.status(400).json({ success: false, error: 'Password must be at least 8 characters long' })

    const existing = await User.findOne({ $or: [{ email }, { username }] })
    if (existing) return res.status(409).json({ success: false, error: 'Username or email already exists' })

    const user = await User.create({
      username,
      email,
      password_hash: hashPassword(password),
      full_name,
      phone,
      location,
      farm_size,
      primary_crops,
      language_preference,
    })
    res.status(201).json({ success: true, data: sanitizeUser(user) })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/users/login
router.post('/users/login', async (req, res) => {
  try {
    const { identifier, password } = req.body
    if (!identifier || !identifier.trim()) {
      return res.status(400).json({ success: false, error: 'Username or email is required' })
    }
    if (!password) {
      return res.status(400).json({ success: false, error: 'Password is required' })
    }

    const normalizedIdentifier = identifier.trim()
    const user = await User.findOne({
      $or: [
        { email: normalizedIdentifier.toLowerCase() },
        { username: normalizedIdentifier },
      ],
    }).select('+password_hash')

    if (!user) {
      return res.status(404).json({ success: false, error: 'No farmer profile found with that username or email' })
    }

    if (!verifyPassword(password, user.password_hash)) {
      return res.status(401).json({ success: false, error: 'Incorrect password' })
    }

    res.json({ success: true, data: sanitizeUser(user) })
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
