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
