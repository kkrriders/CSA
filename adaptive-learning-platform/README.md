# 🎓 Adaptive Learning Platform

A production-ready AI-powered adaptive learning system with exam integrity, cognitive profiling, and intelligent question generation.

## 🌟 Key Features

### 📚 Document Processing
- Upload PDF or Markdown files
- Intelligent text extraction and section detection
- Automatic topic identification
- Background processing for large files

### 🤖 AI Question Generation
- Generate MCQs, Short Answer, and Conceptual questions
- Multiple difficulty levels: Easy, Medium, Hard, Tricky
- Context-aware generation (no hallucination)
- Powered by Llama/Mistral LLMs

### ⏱️ Strict Exam Mode
- **90-second timer per question** (configurable)
- **One-way navigation** - no going back to previous questions
- **Time-locked answers** - cannot change after time expires
- **No cheating** - answers evaluated only on explicit submission

### 🏷️ Question Tagging
- Mark questions as "Tricky" during the test
- Flag questions for "Review Later"
- Persistent review panel shows marked questions
- Post-exam interactive review mode

### 📊 Scoring & Analytics
- Real-time score calculation
- Detailed breakdown: Correct, Wrong, Skipped
- Time spent tracking
- Marked questions summary

### 🧠 AI Intelligence Layer

#### Pattern Detection
- **Fast Wrong** (< 30s) → You guessed
- **Slow Wrong** (> 60s) → You're confused
- **Easy Wrong** → Critical knowledge gap
- **Tricky + Wrong** → High-priority weakness
- **Repeated Failures** → Concept not understood

#### Cognitive Weakness Map
- Topic-by-topic mastery percentage
- Priority scoring (0-100) for each weakness
- Actionable recommendations
- Dangerous knowledge gap detection

#### Smart Review Ordering
Questions ordered by priority:
1. Critical knowledge gaps (easy questions wrong)
2. High-confidence mistakes
3. Confusion points (slow wrong)
4. Guessed incorrectly (fast wrong)
5. Minor mistakes

#### Adaptive Targeting
- Recommends topics for next test based on weaknesses
- Adjusts difficulty based on mastery level
- Estimates questions needed for improvement

#### AI Explanations
- Detailed "why you got it wrong" analysis
- Concept explanations
- Common mistake identification

## 🏗️ Architecture

### Backend (Python/FastAPI)
```
backend/
├── app/
│   ├── core/              # Configuration, database, security
│   ├── models/            # Pydantic schemas
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   │   ├── document_processor.py    # PDF/Markdown parsing
│   │   ├── llm_service.py           # AI integration
│   │   └── analytics_service.py     # Pattern detection
│   └── main.py            # FastAPI application
└── requirements.txt
```

**Tech Stack:**
- FastAPI (async Python web framework)
- MongoDB (Motor async driver)
- PyPDF2 (PDF parsing)
- Ollama/HuggingFace (LLM integration)
- JWT authentication
- Background tasks

### Frontend (React)
```
frontend/
├── src/
│   ├── api/               # Axios API client
│   ├── components/        # Reusable components
│   │   ├── Timer.jsx     # 90-second countdown
│   │   └── ReviewPanel.jsx  # Sidebar review panel
│   ├── pages/             # Page components
│   │   ├── TestPage.jsx  # Exam interface
│   │   ├── ResultsPage.jsx
│   │   └── AnalyticsPage.jsx
│   ├── store/             # Zustand state management
│   └── main.jsx           # Entry point
└── package.json
```

**Tech Stack:**
- React 18
- Vite (build tool)
- Tailwind CSS
- Zustand (state management)
- React Router
- Axios

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MongoDB
- Ollama (for local LLM) or HuggingFace API key

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env

# Edit .env with your settings
nano .env

# Install Ollama (recommended for local LLM)
curl https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama2

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will run at:** `http://localhost:8000`

**API Documentation:** `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
echo "VITE_API_URL=http://localhost:8000/api" > .env.local

# Run development server
npm run dev
```

**Frontend will run at:** `http://localhost:3000`

## 📖 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)
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
- `GET /api/tests/{id}/review-questions` - Get marked/wrong questions

### Analytics (AI Intelligence)
- `GET /api/analytics/session/{id}/patterns` - Detect answer patterns
- `GET /api/analytics/session/{id}/topic-mastery` - Topic mastery analysis
- `GET /api/analytics/session/{id}/weakness-map` - Cognitive weakness map
- `GET /api/analytics/session/{id}/adaptive-targeting` - Next test recommendations
- `GET /api/analytics/session/{id}/review-order` - Smart review ordering
- `POST /api/analytics/explain-wrong-answer` - AI explanation for wrong answer

## 🌐 Deployment

### Backend → Render.com

1. Push code to GitHub
2. Create Web Service on Render
3. Connect GitHub repository
4. Set environment variables:
   - `MONGODB_URI`
   - `SECRET_KEY`
   - `LLM_PROVIDER`
   - `CORS_ORIGINS`
5. Deploy!

**Build Command:** `pip install -r requirements.txt`

**Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel

```bash
cd frontend
npm install -g vercel
vercel deploy --prod
```

Set environment variable in Vercel:
- `VITE_API_URL` = Your Render backend URL

## 📊 Usage Flow

1. **Register/Login** → Create account or sign in
2. **Upload Document** → PDF or Markdown file
3. **Generate Questions** → AI creates questions from content
4. **Configure Test** → Select number of questions, difficulty, topics
5. **Take Test** → 90-second timer per question, strict navigation
6. **Mark Questions** → Tag tricky ones during the test
7. **Submit Test** → See immediate results
8. **View Analytics** → AI-generated weakness map
9. **Review Questions** → Smart-ordered review of mistakes
10. **Next Test** → Adaptive targeting suggests focus areas

## 🎯 Exam Integrity Rules

The system enforces strict exam rules to simulate real competitive exams:

1. ✅ **Fixed time per question** (90 seconds)
2. ✅ **No backwards navigation** - Cannot go to previous questions
3. ✅ **Answer lock** - Cannot change answer after submission
4. ✅ **Time expiry** - Question auto-submits when time runs out
5. ✅ **Explicit submission** - Must click "Check Answer" to submit
6. ✅ **One-way progress** - Must complete current question to move forward

## 🧪 AI Pattern Detection Examples

### Scenario 1: Fast Wrong (< 30s)
**Signal:** You guessed quickly
**Recommendation:** Slow down, read questions carefully

### Scenario 2: Slow Wrong (> 60s)
**Signal:** You spent time but still got it wrong - concept is unclear
**Recommendation:** Revisit source material, study the concept

### Scenario 3: Easy Wrong
**Signal:** You failed an easy question - critical knowledge gap
**Recommendation:** ⚠️ URGENT - Review fundamental concepts immediately

### Scenario 4: Tricky + Wrong
**Signal:** You marked it tricky AND got it wrong - high priority
**Recommendation:** This is a confusion point - needs focused study

### Scenario 5: Repeated Topic Failures
**Signal:** Multiple failures in same topic
**Recommendation:** Major knowledge gap - dedicate study session to this topic

## 🔧 Configuration

### Backend Environment Variables

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017/adaptive_learning
MONGODB_DB_NAME=adaptive_learning

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM Provider (ollama, huggingface, lmstudio)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Application
MAX_FILE_SIZE=52428800
DEFAULT_QUESTION_TIME=90
CORS_ORIGINS=http://localhost:3000
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000/api
```

## 📚 Additional Resources

- [Complete Implementation Guide](./IMPLEMENTATION_GUIDE.md) - Detailed code examples and architecture
- [Backend README](./backend/README.md) - Backend-specific documentation
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (Swagger UI)

## 🤝 Contributing

This is a fully-featured adaptive learning platform ready for production use or further customization.

## 📄 License

MIT License - Feel free to use this for personal or commercial projects!

---

## 💡 Why This System is Unique

### Traditional Quiz Apps
❌ Can go back to previous questions
❌ Generic scoring (just percentage)
❌ No pattern detection
❌ Random question review
❌ No adaptive targeting

### This Adaptive Learning Platform
✅ Strict exam mode (no going back)
✅ AI-powered cognitive profiling
✅ Pattern detection (fast wrong, slow wrong, etc.)
✅ Smart review ordering by priority
✅ Adaptive next-test targeting
✅ Detailed AI explanations
✅ Weakness mapping with recommendations

**This isn't just a quiz app - it's an intelligent learning coach.**

---

Built with ❤️ using FastAPI, React, and AI
