# AI Voice Interview System 🎤

AI-powered resume-based voice interview system integrated with SATA (Student Academic Tracker and Analyzer).

## ✨ Features

- **Resume Intelligence**: Upload PDF/DOCX resumes, automatic skill extraction with SpaCy NLP
- **AI Questions**: Personalized interview questions using HuggingFace FLAN-T5
- **Voice Interview**: Real-time voice conversations with Whisper STT + Coqui TTS
- **Voice Analytics**: Speech pattern analysis, filler word detection, confidence scoring
- **Performance Evaluation**: Detailed scorecards, improvement suggestions, career recommendations
- **SATA Integration**: Connects with academic data for comprehensive evaluation

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python 3.11) |
| Frontend | React 18 + TypeScript + TailwindCSS |
| Database | PostgreSQL |
| Resume Parsing | PyResparser + SpaCy |
| Speech-to-Text | OpenAI Whisper (local) |
| Text-to-Speech | Coqui TTS |
| AI Questions | HuggingFace Transformers (FLAN-T5) |
| Voice Analytics | librosa + pyAudioAnalysis |

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
cd "ai interviewer"
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
ai interviewer/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # API endpoints
│   │   ├── core/            # Config, database
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Route pages
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── Dockerfile
└── docker-compose.yml
```

## 📖 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/resume/upload` | Upload and parse resume |
| `GET /api/resume/{id}` | Get resume details |
| `POST /api/interview/create` | Create interview session |
| `POST /api/interview/{id}/start` | Start interview |
| `WS /ws/interview/{id}` | WebSocket for voice interview |
| `GET /api/evaluation/{id}/report` | Get evaluation report |

## 🎯 Interview Flow

1. **Upload Resume** → AI extracts skills, projects, experience
2. **Setup Interview** → Choose type (Technical/HR/Mixed) and difficulty
3. **Voice Interview** → AI asks questions, you respond via microphone
4. **Get Results** → Detailed score, strengths, areas to improve

## 🤝 SATA Integration

Connect to existing SATA database for:
- Academic performance correlation
- GPA-based question adaptation
- Comprehensive student profiles

## 📄 License

MIT License - Free for educational and commercial use.
