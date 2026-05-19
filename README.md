# VeritasAI — Fake News Detection System

An end-to-end AI-powered fake news detection system using Claude (NLP), Flask (backend), and React (frontend).

## Architecture

```
veritasai/
├── backend/           ← Flask REST API
│   ├── app.py         ← Main API server
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/          ← React + Vite UI
│   ├── src/
│   │   ├── App.jsx    ← Main UI component
│   │   ├── api.js     ← API service layer
│   │   ├── index.css  ← Global styles
│   │   └── main.jsx   ← Entry point
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
└── docker-compose.yml ← Full stack deployment
```

## Quick Start

### 1. Get your Anthropic API key
Sign up at https://console.anthropic.com and create an API key.

### 2. Option A — Docker (recommended)

```bash
# Clone and navigate
cd veritasai

# Set your API key
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Start everything
docker-compose up --build

# Open http://localhost:3000
```

### 3. Option B — Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set ANTHROPIC_API_KEY=your_key
python app.py
# API running at http://localhost:5000
```

**Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
# Edit .env: VITE_API_URL=http://localhost:5000/api
npm run dev
# UI running at http://localhost:3000
```

## API Endpoints

| Method | Endpoint        | Description                        |
|--------|-----------------|------------------------------------|
| GET    | /api/health     | Health check + version info        |
| POST   | /api/analyze    | Analyze a single article/headline  |
| POST   | /api/batch      | Analyze up to 5 items at once      |
| GET    | /api/history    | Get recent analysis history        |
| GET    | /api/stats      | Aggregate statistics               |

### POST /api/analyze

**Request:**
```json
{
  "text": "News article text here...",
  "url": "https://optional-url.com"
}
```

**Response:**
```json
{
  "verdict": "FAKE",
  "confidence": 92,
  "summary": "This article displays multiple hallmarks of misinformation...",
  "scores": {
    "factual_accuracy": 12,
    "source_credibility": 8,
    "emotional_manipulation": 94,
    "clickbait_score": 88,
    "scientific_accuracy": 5,
    "linguistic_quality": 45
  },
  "signals": [...],
  "nlp_tags": [...],
  "recommendations": [...],
  "red_flags": [...],
  "positive_indicators": [],
  "cached": false,
  "analyzed_at": "2026-05-18T10:30:00Z"
}
```

## Features

- **Real-time AI analysis** powered by Claude Sonnet
- **6 credibility scores** — factual accuracy, source credibility, emotional manipulation, clickbait, scientific accuracy, linguistic quality
- **Detection signals** — color-coded red/amber/green flags
- **NLP markers** — linguistic pattern tags
- **Red flags & positive indicators** — specific evidence found
- **Recommendations** — actionable steps for the reader
- **Response caching** — identical requests return instantly
- **Rate limiting** — 20 requests/minute, 200/day per IP
- **Batch analysis** — analyze up to 5 articles at once
- **Analysis history** — last 100 analyses stored in memory
- **Live stats** — verdict distribution, avg confidence
- **Docker ready** — one command deployment

## Tech Stack

| Layer     | Technology              |
|-----------|-------------------------|
| AI / NLP  | Anthropic Claude Sonnet |
| Backend   | Python 3.12 + Flask 3   |
| Frontend  | React 18 + Vite 5       |
| Styling   | Pure CSS (no framework) |
| HTTP      | Axios                   |
| Deploy    | Docker + Nginx          |

## Production Notes

- Replace in-memory cache with Redis for multi-worker deployments
- Add a database (PostgreSQL) for persistent history
- Set `ALLOWED_ORIGINS` to your domain in production
- Use a reverse proxy (Nginx/Caddy) with HTTPS in production
- Monitor API usage in the Anthropic console

## License

MIT
