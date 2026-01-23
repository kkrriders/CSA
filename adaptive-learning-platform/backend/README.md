# Adaptive Learning Platform - Backend

AI-powered adaptive learning system with exam integrity, pattern detection, and cognitive profiling.

## Features

- 📄 PDF & Markdown document processing
- 🤖 AI-powered question generation (MCQ, Short Answer, Conceptual)
- ⏱️ Strict timed test mode (90s per question)
- 🔒 Exam integrity (no backwards navigation, time-locked answers)
- 🧠 AI pattern detection (fast wrong, slow wrong, topic failures)
- 📊 Cognitive weakness mapping
- 🎯 Adaptive next-test targeting
- 💡 AI-generated explanations for wrong answers

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (Motor async driver)
- **AI/ML**: LLama/Mistral (via Ollama, HuggingFace, or LM Studio)
- **Auth**: JWT with bcrypt
- **File Processing**: PyPDF2, python-markdown

## Setup

### Prerequisites

- Python 3.9+
- MongoDB
- Ollama (for local LLM) or HuggingFace API key

### Install Ollama (Recommended)

```bash
# Linux/Mac
curl https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve

# Pull Llama2 model
ollama pull llama2
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env and add your configuration
nano .env
```

### Configuration

Edit `.env`:

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/adaptive_learning

# JWT Secret (change this!)
SECRET_KEY=your-super-secret-key-change-this

# LLM Provider (ollama, huggingface, lmstudio)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

### Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at: `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Documents
- `POST /api/documents/upload` - Upload PDF/Markdown
- `GET /api/documents/` - List user documents
- `GET /api/documents/{id}` - Get document details
- `DELETE /api/documents/{id}` - Delete document

### Questions
- `POST /api/questions/generate` - Generate questions from document
- `GET /api/questions/document/{id}` - Get questions for document

### Tests
- `POST /api/tests/start` - Start new test session
- `GET /api/tests/{id}/current-question` - Get current question
- `POST /api/tests/{id}/submit-answer` - Submit answer
- `POST /api/tests/{id}/mark-question` - Mark as tricky/review
- `GET /api/tests/{id}/results` - Get test results

### Analytics (AI Intelligence)
- `GET /api/analytics/session/{id}/patterns` - Detect answer patterns
- `GET /api/analytics/session/{id}/topic-mastery` - Topic mastery analysis
- `GET /api/analytics/session/{id}/weakness-map` - Cognitive weakness map
- `GET /api/analytics/session/{id}/adaptive-targeting` - Next test targeting
- `POST /api/analytics/explain-wrong-answer` - AI explanation

## Deployment to Render

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Set environment variables in Render dashboard
5. Deploy!

Build Command: `pip install -r requirements.txt`

Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Architecture

```
backend/
├── app/
│   ├── core/           # Config, database, security
│   ├── models/         # Pydantic schemas
│   ├── routes/         # API endpoints
│   ├── services/       # Business logic
│   │   ├── document_processor.py   # PDF/MD parsing
│   │   ├── llm_service.py          # AI integration
│   │   └── analytics_service.py    # Pattern detection
│   └── main.py         # FastAPI app
├── uploads/            # Uploaded files
└── requirements.txt
```

## License

MIT
