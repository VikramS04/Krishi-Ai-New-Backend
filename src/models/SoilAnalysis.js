const mongoose = require('mongoose')

const soilAnalysisSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  location: { type: String, trim: true, default: '' },
  ph_level: { type: Number },
  nitrogen: { type: Number },
  phosphorus: { type: Number },
  potassium: { type: Number },
  organic_matter: { type: Number },
  moisture_content: { type: Number },
  // AI-generated results
  health_score: { type: Number },
  soil_type: { type: String },
  recommendations: [{ type: { type: String }, recommendation: String }],
  suitable_crops: [{ crop_name: String, suitability_score: Number }],
  raw_ai_response: { type: String },
}, { timestamps: true })

module.exports = mongoose.model('SoilAnalysis', soilAnalysisSchema)
