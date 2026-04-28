const express = require('express')
const router = express.Router()
const CommunityPost = require('../models/CommunityPost')
const User = require('../models/User')

// GET /api/community/posts?language=english&category=Soil Health&page=1&limit=10
router.get('/community/posts', async (req, res) => {
  try {
    const { language, category, page = 1, limit = 20 } = req.query
    const filter = {}
    if (language) filter.language = language
    if (category) filter.category = category

    const posts = await CommunityPost.find(filter)
      .select('-__v')
      .sort({ createdAt: -1 })
      .skip((page - 1) * limit)
      .limit(parseInt(limit))

    const total = await CommunityPost.countDocuments(filter)

    res.json({ success: true, count: posts.length, total, page: parseInt(page), data: posts })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/community/posts
router.post('/community/posts', async (req, res) => {
  try {
    const { user_id, title, content, category, language } = req.body
    if (!user_id || !title || !content) return res.status(400).json({ success: false, error: 'user_id, title and content are required' })

    // Get username for display
    let username = 'Farmer'
    try {
      const user = await User.findById(user_id)
      if (user) username = user.full_name || user.username
    } catch (_) {}

    const post = await CommunityPost.create({ user_id, username, title, content, category, language })
    res.status(201).json({ success: true, data: post })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/community/posts/:id
router.get('/community/posts/:id', async (req, res) => {
  try {
    const post = await CommunityPost.findByIdAndUpdate(
      req.params.id,
      { $inc: { views: 1 } },
      { new: true }
    ).select('-__v')
    if (!post) return res.status(404).json({ success: false, error: 'Post not found' })
    res.json({ success: true, data: post })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/community/posts/:id/like
router.post('/community/posts/:id/like', async (req, res) => {
  try {
    const { user_id } = req.body
    if (!user_id) return res.status(400).json({ success: false, error: 'user_id is required' })

    const post = await CommunityPost.findById(req.params.id)
    if (!post) return res.status(404).json({ success: false, error: 'Post not found' })

    const alreadyLiked = post.likes.includes(user_id)
    if (alreadyLiked) {
      post.likes.pull(user_id) // unlike
    } else {
      post.likes.push(user_id) // like
    }
    await post.save()

    res.json({ success: true, liked: !alreadyLiked, likes_count: post.likes.length })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// POST /api/community/posts/:id/comments
router.post('/community/posts/:id/comments', async (req, res) => {
  try {
    const { user_id, content } = req.body
    if (!user_id || !content) return res.status(400).json({ success: false, error: 'user_id and content are required' })

    let username = 'Farmer'
    try {
      const user = await User.findById(user_id)
      if (user) username = user.full_name || user.username
    } catch (_) {}

    const post = await CommunityPost.findByIdAndUpdate(
      req.params.id,
      { $push: { comments: { user_id, username, content } } },
      { new: true }
    ).select('-__v')

    if (!post) return res.status(404).json({ success: false, error: 'Post not found' })
    res.status(201).json({ success: true, data: post.comments[post.comments.length - 1], comments_count: post.comments.length })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/community/trending
router.get('/community/trending', async (req, res) => {
  try {
    // Score = likes * 3 + comments * 2 + views — last 30 days
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
    const posts = await CommunityPost.find({ createdAt: { $gte: thirtyDaysAgo } }).select('-__v')
    const scored = posts
      .map(p => ({ ...p.toJSON(), score: p.likes.length * 3 + p.comments.length * 2 + p.views }))
      .sort((a, b) => b.score - a.score)
      .slice(0, 10)
    res.json({ success: true, data: scored })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

// GET /api/community/search?q=wheat
router.get('/community/search', async (req, res) => {
  try {
    const { q } = req.query
    if (!q) return res.status(400).json({ success: false, error: 'Search query q is required' })
    const posts = await CommunityPost.find({
      $or: [
        { title: { $regex: q, $options: 'i' } },
        { content: { $regex: q, $options: 'i' } },
        { category: { $regex: q, $options: 'i' } },
      ],
    }).select('-__v').sort({ createdAt: -1 }).limit(20)
    res.json({ success: true, count: posts.length, data: posts })
  } catch (err) {
    res.status(500).json({ success: false, error: err.message })
  }
})

module.exports = router
