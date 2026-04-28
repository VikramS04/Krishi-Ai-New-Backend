const mongoose = require('mongoose')

const userSchema = new mongoose.Schema({
  username: {
    type: String,
    required: [true, 'Username is required'],
    unique: true,
    trim: true,
    minlength: 3,
    maxlength: 50,
  },
  email: {
    type: String,
    required: [true, 'Email is required'],
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\S+@\S+\.\S+$/, 'Please enter a valid email'],
  },
  full_name: { type: String, trim: true, default: '' },
  phone: { type: String, trim: true, default: '' },
  location: { type: String, trim: true, default: '' },
  farm_size: { type: Number, default: 0 },
  primary_crops: { type: String, trim: true, default: '' },
  language_preference: { type: String, enum: ['english', 'hindi'], default: 'english' },
}, { timestamps: true })

module.exports = mongoose.model('User', userSchema)
