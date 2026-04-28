const mongoose = require('mongoose')

const commentSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  username: { type: String, default: 'Anonymous' },
  content: { type: String, required: true },
}, { timestamps: true })

const communityPostSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  username: { type: String, default: 'Farmer' },
  title: { type: String, required: true, trim: true },
  content: { type: String, required: true, trim: true },
  category: {
    type: String,
    enum: ['Crop Management', 'Soil Health', 'Pest Control', 'Weather Discussion', 'Market Prices', 'Technology', 'Success Stories', 'Questions', 'General Discussion'],
    default: 'General Discussion',
  },
  language: { type: String, enum: ['english', 'hindi'], default: 'english' },
  likes: [{ type: mongoose.Schema.Types.ObjectId, ref: 'User' }],
  comments: [commentSchema],
  views: { type: Number, default: 0 },
}, { timestamps: true })

// Virtual fields for counts
communityPostSchema.virtual('likes_count').get(function () { return this.likes.length })
communityPostSchema.virtual('comments_count').get(function () { return this.comments.length })

communityPostSchema.set('toJSON', { virtuals: true })
communityPostSchema.set('toObject', { virtuals: true })

module.exports = mongoose.model('CommunityPost', communityPostSchema)
