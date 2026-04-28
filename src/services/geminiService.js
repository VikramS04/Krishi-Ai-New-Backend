const { GoogleGenerativeAI } = require('@google/generative-ai')

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY)
const GEMINI_MODEL = process.env.GEMINI_MODEL || 'gemini-2.5-flash'

const getModel = () => genAI.getGenerativeModel({ model: GEMINI_MODEL })

// ─── Soil Analysis ────────────────────────────────────────────────────────────
const analyzeSoilWithAI = async (soilData) => {
  const model = getModel()

  const prompt = `
You are an expert agricultural soil scientist. Analyze the following soil data and respond ONLY with valid JSON — no markdown, no explanation, just the raw JSON object.

Soil Data:
- Location: ${soilData.location || 'Unknown'}
- pH Level: ${soilData.ph_level}
- Nitrogen (N): ${soilData.nitrogen} mg/kg
- Phosphorus (P): ${soilData.phosphorus} mg/kg
- Potassium (K): ${soilData.potassium} mg/kg
- Organic Matter: ${soilData.organic_matter}%
- Moisture Content: ${soilData.moisture_content}%

Respond with exactly this JSON structure:
{
  "health_score": <integer 0-100>,
  "soil_type": "<one of: Sandy, Clay, Loamy, Silt, Peat, Chalky, or Mixed>",
  "recommendations": [
    { "type": "<category e.g. pH Correction, Nitrogen, Fertilizer, Irrigation>", "recommendation": "<specific actionable advice>" },
    { "type": "...", "recommendation": "..." }
  ],
  "suitable_crops": [
    { "crop_name": "<crop>", "suitability_score": <integer 50-100> },
    { "crop_name": "<crop>", "suitability_score": <integer 50-100> }
  ],
  "summary": "<2-3 sentence overall assessment>"
}

Include 3-5 recommendations and 6-8 suitable crops. Be specific to Indian agriculture context.
`

  const result = await model.generateContent(prompt)
  const text = result.response.text().trim()

  // Strip markdown fences if Gemini wraps in ```json
  const clean = text.replace(/^```json\n?/, '').replace(/\n?```$/, '').trim()
  return JSON.parse(clean)
}

// ─── Crop Recommendations ─────────────────────────────────────────────────────
const getCropRecommendationsWithAI = async (userData) => {
  const model = getModel()

  const prompt = `
You are an expert agricultural advisor for Indian farmers. Based on the following farmer profile, provide crop recommendations. Respond ONLY with valid JSON.

Farmer Profile:
- Location: ${userData.location || 'India'}
- Farm Size: ${userData.farm_size || 'Unknown'} acres
- Current Crops: ${userData.primary_crops || 'Unknown'}
- Season: ${getCurrentSeason()}

Respond with exactly this JSON structure:
{
  "recommended_crops": [
    {
      "crop_name": "<crop>",
      "reason": "<why this crop suits their profile>",
      "expected_yield": "<e.g. 25-30 quintals/acre>",
      "growing_period": "<e.g. 90-120 days>",
      "market_demand": "<High/Medium/Low>",
      "estimated_profit": "<e.g. ₹15,000-20,000/acre>"
    }
  ],
  "seasonal_advice": "<general advice for current season>",
  "risk_factors": ["<risk 1>", "<risk 2>"]
}

Include 4-6 crops suitable for Indian agriculture.
`

  const result = await model.generateContent(prompt)
  const text = result.response.text().trim()
  const clean = text.replace(/^```json\n?/, '').replace(/\n?```$/, '').trim()
  return JSON.parse(clean)
}

// ─── Disease Detection (text-based) ──────────────────────────────────────────
const detectDiseaseWithAI = async (cropType, symptoms = null) => {
  const model = getModel()

  const prompt = `
You are a plant pathologist and crop disease expert. Analyze the following crop information and respond ONLY with valid JSON.

Crop Type: ${cropType}
Reported Symptoms: ${symptoms || 'General health check requested — provide common disease risks for this crop'}

Respond with exactly this JSON structure:
{
  "disease_name": "<name of disease or 'Healthy' if no disease>",
  "confidence_score": <float 0.0-1.0>,
  "severity_level": "<None/Mild/Moderate/Severe>",
  "is_healthy": <true or false>,
  "affected_parts": ["<leaf>", "<stem>", etc],
  "treatment_recommendations": [
    "<specific treatment step 1>",
    "<specific treatment step 2>",
    "<specific treatment step 3>"
  ],
  "preventive_measures": [
    "<prevention tip 1>",
    "<prevention tip 2>",
    "<prevention tip 3>"
  ],
  "organic_alternatives": ["<organic treatment 1>", "<organic treatment 2>"],
  "urgency": "<Low/Medium/High — how urgently the farmer should act>"
}

Be specific to Indian farming conditions. Include 3-4 treatment recommendations and 3-4 preventive measures.
`

  const result = await model.generateContent(prompt)
  const text = result.response.text().trim()
  const clean = text.replace(/^```json\n?/, '').replace(/\n?```$/, '').trim()
  return JSON.parse(clean)
}

// ─── Disease Detection with Image ─────────────────────────────────────────────
const detectDiseaseFromImageWithAI = async (cropType, imageBase64, mimeType = 'image/jpeg') => {
  const model = getModel()

  const prompt = `
You are a plant pathologist. Analyze this crop image for disease detection. The crop is: ${cropType}.
Respond ONLY with valid JSON using exactly this structure:
{
  "disease_name": "<name or 'Healthy'>",
  "confidence_score": <float 0.0-1.0>,
  "severity_level": "<None/Mild/Moderate/Severe>",
  "is_healthy": <true/false>,
  "affected_parts": ["<part>"],
  "visual_symptoms": "<what you see in the image>",
  "treatment_recommendations": ["<step 1>", "<step 2>", "<step 3>"],
  "preventive_measures": ["<tip 1>", "<tip 2>", "<tip 3>"],
  "organic_alternatives": ["<option 1>", "<option 2>"],
  "urgency": "<Low/Medium/High>"
}
`

  const result = await model.generateContent([
    prompt,
    { inlineData: { data: imageBase64, mimeType } },
  ])

  const text = result.response.text().trim()
  const clean = text.replace(/^```json\n?/, '').replace(/\n?```$/, '').trim()
  return JSON.parse(clean)
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
const getCurrentSeason = () => {
  const month = new Date().getMonth() + 1
  if (month >= 6 && month <= 9) return 'Kharif (Monsoon)'
  if (month >= 10 && month <= 11) return 'Rabi (Winter sowing)'
  if (month >= 12 || month <= 2) return 'Rabi (Winter crop growing)'
  return 'Zaid (Summer)'
}

module.exports = {
  analyzeSoilWithAI,
  getCropRecommendationsWithAI,
  detectDiseaseWithAI,
  detectDiseaseFromImageWithAI,
}
