const mongoose = require('mongoose')

const diseaseDetectionSchema = new mongoose.Schema({
  user_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
  crop_type: { type: String, required: true },
  image_base64: { type: String },
  detection_result: {
    disease_name: String,
    confidence_score: Number,
    severity_level: String,
    treatment_recommendations: [String],
    preventive_measures: [String],
    is_healthy: Boolean,
  },
  raw_ai_response: { type: String },
}, { timestamps: true })

module.exports = mongoose.model('DiseaseDetection', diseaseDetectionSchema)
