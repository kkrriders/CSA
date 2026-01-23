# Adaptive Learning Platform - Next.js Frontend

Modern, responsive frontend built with Next.js 14, TypeScript, and Tailwind CSS.

## 🎯 Features

- ✅ **Authentication** - Login & Register with JWT
- ✅ **Document Management** - Upload PDF/Markdown files
- ✅ **Test Interface** - 90-second timer, strict navigation
- ✅ **Review Panel** - Sidebar with marked questions
- ✅ **Analytics Dashboard** - AI-powered insights
- ✅ **Responsive Design** - Works on all devices
- ✅ **Type-Safe** - Full TypeScript coverage

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Charts**: Recharts
- **Notifications**: React Hot Toast

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ installed
- Backend running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.local.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Run development server
npm run dev
```

Visit http://localhost:3000

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── auth/              # Authentication pages
│   │   ├── login/         # Login page
│   │   └── register/      # Register page
│   ├── dashboard/         # Dashboard page
│   ├── test/              # Test pages
│   │   ├── configure/     # Test configuration
│   │   ├── [sessionId]/   # Test interface
│   │   └── results/       # Results page
│   ├── analytics/         # Analytics dashboard
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Landing page
├── components/            # Reusable components
│   ├── Timer.tsx          # 90-second countdown timer
│   ├── ReviewPanel.tsx    # Review sidebar
│   └── QuestionCard.tsx   # Question display
├── lib/                   # Utilities
│   ├── api.ts             # API client
│   └── store.ts           # Zustand stores
└── types/                 # TypeScript types
    └── index.ts           # All type definitions
```

## 🔗 API Integration

The frontend connects to the FastAPI backend via Axios client:

```typescript
import { api } from '@/lib/api';

// Authentication
await api.login(email, password);
await api.register(email, password, name);

// Documents
await api.uploadDocument(file);
await api.getDocuments();

// Tests
await api.startTest(documentId, config);
await api.submitAnswer(sessionId, questionId, answer, timeTaken);

// Analytics
await api.getWeaknessMap(sessionId);
await api.getAdaptiveTargeting(sessionId);
```

## 🎨 Pages

### Landing Page (`/`)
- Hero section
- Feature showcase
- How it works
- Call to action

### Authentication
- **Login** (`/auth/login`)
- **Register** (`/auth/register`)

### Dashboard (`/dashboard`)
- Document list
- Upload new documents
- Start tests
- Delete documents

### Test Flow
1. **Configure** (`/test/configure?documentId=xxx`)
   - Select number of questions
   - Choose time per question
   - Filter by topics

2. **Take Test** (`/test/[sessionId]`)
   - 90-second timer per question
   - One-way navigation
   - Mark as tricky
   - Submit answer
   - Review panel sidebar

3. **Results** (`/test/results/[sessionId]`)
   - Score breakdown
   - Time spent
   - Marked questions
   - Wrong questions

### Analytics (`/analytics/[sessionId]`)
- Topic mastery chart
- Weakness map
- Adaptive targeting
- AI explanations

## 🔐 Authentication Flow

```typescript
// Register
const response = await api.register(email, password, name);
useAuthStore.getState().setAuth(response.access_token, response.user);

// Login
const response = await api.login(email, password);
useAuthStore.getState().setAuth(response.access_token, response.user);

// Logout
useAuthStore.getState().logout();
```

Tokens are stored in localStorage and auto-attached to API requests.

## 🧩 State Management

Using Zustand for global state:

```typescript
// Auth Store
const { user, token, setAuth, logout } = useAuthStore();

// Test Store
const {
  currentQuestion,
  timeRemaining,
  reviewQuestions,
  markedQuestions,
  setCurrentQuestion,
  setTimeRemaining,
  addMarkedQuestion
} = useTestStore();
```

## 🎯 Key Features

### 1. Exam Integrity
- ✅ 90-second strict timer
- ✅ No backwards navigation
- ✅ Answer locking
- ✅ Time expiry handling

### 2. Review Panel
- ✅ Persistent sidebar
- ✅ Shows marked questions
- ✅ Shows wrong questions
- ✅ Quick preview
- ✅ Read-only during test

### 3. Real-time Timer
```typescript
useEffect(() => {
  const timer = setInterval(() => {
    setTimeRemaining((prev) => {
      if (prev <= 0) {
        handleTimeout();
        return 0;
      }
      return prev - 1;
    });
  }, 1000);

  return () => clearInterval(timer);
}, []);
```

### 4. Analytics Visualization
- Topic mastery bar charts
- Weakness priority scores
- Pattern detection display
- Adaptive recommendations

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel deploy --prod
```

Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = Your backend URL

### Manual Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## 📱 Responsive Design

All pages are fully responsive:
- Mobile: Single column, touch-optimized
- Tablet: Adaptive layouts
- Desktop: Full features, sidebars

## 🔧 Configuration

### Environment Variables

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Tailwind Theme

Customize colors in `tailwind.config.ts`:

```typescript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#3b82f6',
        600: '#2563eb',
        // ... more shades
      },
    },
  },
}
```

## 🧪 Development

### Hot Reload
```bash
npm run dev
```

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

## 📚 Documentation

- [Next.js Documentation](https://nextjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Zustand Guide](https://docs.pmnd.rs/zustand)

## 🤝 Contributing

This is a production-ready frontend for the Adaptive Learning Platform. All core features are implemented and tested.

## 📄 License

MIT License

---

## ✨ What's Implemented

✅ Complete authentication flow
✅ Document upload & management
✅ Test configuration
✅ Test interface with timer
✅ Review panel sidebar
✅ Results display
✅ Analytics dashboard
✅ Responsive design
✅ Type-safe API client
✅ State management
✅ Error handling
✅ Toast notifications

## 🎉 You're Ready!

The Next.js frontend is fully configured and ready to connect to your backend!

Start the backend on port 8000, then run:
```bash
npm run dev
```

Visit http://localhost:3000 and start learning! 🚀
