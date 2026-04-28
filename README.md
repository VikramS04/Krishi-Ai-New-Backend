# 🌱 KrishiAi Backend v2.0

Node.js · Express · MongoDB Atlas · Google Gemini AI · OpenWeatherMap

---

## Stack

| Layer | Technology |
|---|---|
| Runtime | Node.js 18+ |
| Framework | Express.js |
| Database | MongoDB Atlas (free tier) |
| AI | Google Gemini 1.5 Flash |
| Weather | OpenWeatherMap API |
| Hosting | Vercel (serverless) |

---

## Project Structure

```
krishi-backend/
├── config/
│   └── db.js                  # MongoDB Atlas connection
├── src/
│   ├── index.js               # App entry point
│   ├── middleware/
│   │   └── errorHandler.js    # Global error handling
│   ├── models/
│   │   ├── User.js
│   │   ├── SoilAnalysis.js
│   │   ├── DiseaseDetection.js
│   │   └── CommunityPost.js
│   ├── routes/
│   │   ├── users.js
│   │   ├── soil.js
│   │   ├── crops.js
│   │   ├── disease.js
│   │   ├── weather.js
│   │   └── community.js
│   └── services/
│       ├── geminiService.js   # All Gemini AI calls
│       └── weatherService.js  # OpenWeatherMap calls
├── .env.example
├── package.json
└── vercel.json
```

---

## Setup (Local)

### 1. Install dependencies
```bash
npm install
```

### 2. Create your .env file
```bash
cp .env.example .env
```

Then fill in:
```
MONGODB_URI=mongodb+srv://...
GEMINI_API_KEY=...
OPENWEATHER_API_KEY=...
```

### 3. Get your API keys

**MongoDB Atlas** (already have this)
- Go to your cluster → Connect → Drivers → copy the connection string
- Replace `<password>` with your actual password

**Google Gemini API** (free — 1500 requests/day)
- Visit: https://aistudio.google.com/app/apikey
- Create a new API key
- Paste it as GEMINI_API_KEY

**OpenWeatherMap** (free — 1000 calls/day)
- Visit: https://openweathermap.org/api
- Sign up → API Keys tab → copy your key
- Paste it as OPENWEATHER_API_KEY

### 4. Run locally
```bash
npm run dev
```

API runs at: http://localhost:5001

---

## Deploy to Vercel

### 1. Install Vercel CLI
```bash
npm i -g vercel
```

### 2. Deploy
```bash
vercel
```

### 3. Add environment variables in Vercel dashboard
- Go to your project → Settings → Environment Variables
- Add: `MONGODB_URI`, `GEMINI_API_KEY`, `OPENWEATHER_API_KEY`
- Redeploy after adding variables

---

## Update your Frontend

Change the API_BASE_URL in your React app:
```js
const API_BASE_URL = 'https://your-project.vercel.app/api'
```

---

## API Endpoints

### Health
```
GET /api/health
GET /api/docs
```

### Users
```
GET    /api/users
POST   /api/users          { username, email, full_name, phone, location, farm_size, primary_crops }
GET    /api/users/:id
PUT    /api/users/:id
DELETE /api/users/:id
```

### Soil Analysis (Gemini AI)
```
POST /api/soil/analyze     { user_id, location, ph_level, nitrogen, phosphorus, potassium, organic_matter, moisture_content }
GET  /api/soil/history/:user_id
GET  /api/soil/:id
```

### Crop Recommendations (Gemini AI)
```
POST /api/crops/recommend  { user_id }
```

### Disease Detection (Gemini Vision)
```
POST /api/disease/detect   { user_id, crop_type, symptoms? }
POST /api/disease/upload   multipart/form-data: { user_id, crop_type, image }
GET  /api/disease/history/:user_id
```

### Weather (OpenWeatherMap)
```
GET /api/weather/current/:location
GET /api/weather/forecast/:location?days=7
GET /api/weather/alerts/:location
```

### Community
```
GET  /api/community/posts?language=english&category=Soil Health&page=1
POST /api/community/posts          { user_id, title, content, category, language }
GET  /api/community/posts/:id
POST /api/community/posts/:id/like     { user_id }
POST /api/community/posts/:id/comments { user_id, content }
GET  /api/community/trending
GET  /api/community/search?q=wheat
```

---

## Notes

- AI endpoints are rate-limited to 20 requests/minute to protect your Gemini quota
- Image uploads support JPG/PNG up to 10MB, processed in-memory (no disk — Vercel compatible)
- Gemini 1.5 Flash is used for all AI — it's fast, accurate, and free tier is generous
- Disease detection supports both text-based (symptoms) and image-based (Gemini Vision) analysis
