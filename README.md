# 🎤 MockMate

Practice. Improve. Get Hired.

MockMate is an AI-powered mock interview platform that helps users prepare for interviews through realistic AI-driven conversations, performance analysis, and personalized feedback.

## Features

- 🎤 **AI Mock Interviews** - Realistic interview simulations with role-specific questions
- 📊 **Performance Analysis** - Detailed scoring across technical, communication, confidence, problem-solving, and body language
- 📈 **Confidence Tracking** - Track improvement over time with interview history
- 📋 **Reports Dashboard** - Comprehensive reports with AI feedback and body language analysis
- 🔐 **Secure Authentication** - AWS Cognito integration via Amplify
- 📹 **Body Language Analysis** - Real-time MediaPipe Face Mesh for eye contact, posture, gestures, and attention

## Tech Stack

### Frontend (Next.js)
- **Framework**: Next.js 16.4.6 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS 4
- **Auth**: AWS Amplify v6 + Cognito + @aws-amplify/ui-react
- **Body Language**: MediaPipe Face Mesh
- **State Management**: React Context + useReducer

### Backend (Lambda)
- **Runtime**: Node.js / Python
- **API**: REST API via API Gateway
- **Auth**: AWS Cognito User Pools
- **Storage**: DynamoDB (interview history, reports)

### Deployment
- **Frontend**: AWS Amplify Hosting
- **Backend**: AWS Lambda + API Gateway
- **Auth**: AWS Cognito

## Project Structure

```
MockMate/
├── frontend/                 # Next.js frontend application
│   ├── src/
│   │   ├── app/             # App Router pages
│   │   │   ├── dashboard/   # Dashboard page
│   │   │   ├── interview/   # Live interview page
│   │   │   ├── reports/     # Reports list & detail
│   │   │   ├── settings/    # User settings
│   │   │   └── sign-in/     # Authentication page
│   │   ├── lib/             # Shared libraries
│   │   │   ├── api.ts       # API client
│   │   │   ├── types.ts     # TypeScript types
│   │   │   ├── store.tsx    # Global state (Context + useReducer)
│   │   │   ├── use-presence.ts # MediaPipe body language hook
│   │   │   ├── amplify-config.ts # Amplify configuration
│   │   │   └── auth-guard.tsx  # Route protection
│   │   └── components/      # Reusable components
│   ├── public/
│   │   └── mediapipe/       # MediaPipe WASM models (for production)
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   └── .env.local           # Environment variables
├── mock-server.js           # Local mock backend for development
├── app.py                   # Legacy Streamlit app
├── pages/                   # Legacy Streamlit pages
└── README.md
```

## Quick Start

### Prerequisites
- Node.js 18+
- npm or yarn
- AWS Account (for Cognito/Amplify deployment)

### Local Development (Real AWS API - Default)

1. **Install frontend dependencies**
```bash
cd frontend
npm install
```

2. **Configure environment variables**
```bash
# Copy and edit .env.local
cp .env.local.example .env.local
# Edit NEXT_PUBLIC_API_BASE_URL (your API Gateway URL), COGNITO credentials
```

3. **Start frontend development server**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

4. **Test the full flow**
- Open http://localhost:3000
- Sign up / Sign in with Cognito
- Start an interview
- Answer 5 questions
- View your report

### Local Development (Mock Backend - Optional)

If you don't have AWS credentials configured, you can use the local mock server:

```bash
# From project root (terminal 1)
node mock-server.js
# Runs on http://localhost:3001

# In .env.local, set:
# NEXT_PUBLIC_API_BASE_URL=http://localhost:3001

# Then start frontend (terminal 2)
cd frontend
npm run dev
```

### Environment Variables

Create `.env.local` in the frontend directory:

```env
# API Backend URL (Lambda + API Gateway)
NEXT_PUBLIC_API_BASE_URL=https://your-api-gateway-url.amazonaws.com/prod

# AWS Cognito Configuration
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
NEXT_PUBLIC_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_COGNITO_DOMAIN=your-domain.auth.us-east-1.amazoncognito.com
```

## Deployment

### Backend (Lambda + API Gateway)
1. Deploy Lambda functions for:
   - `POST /interview/start` - Create interview session
   - `POST /interview/answer` - Submit answer & get next question
   - `POST /interview/report` - Generate performance report
   - `GET /interviews?userId=` - Get interview history
   - `POST /interview/report/save` - Save report (no-op)

2. Configure API Gateway with CORS and Cognito Authorizer

3. Set Lambda environment variable: `USE_MOCK=false`

### Frontend (AWS Amplify)
1. Connect GitHub repository to Amplify
2. Configure build settings:
   ```yaml
   version: 1
   frontend:
     phases:
       preBuild:
         commands:
           - npm ci
       build:
         commands:
           - npm run build
     artifacts:
       baseDirectory: .next
       files:
         - '**/*'
     cache:
       paths:
         - node_modules/**/*
   ```

3. Set environment variables in Amplify Console:
   - `NEXT_PUBLIC_API_BASE_URL`
   - `NEXT_PUBLIC_COGNITO_USER_POOL_ID`
   - `NEXT_PUBLIC_COGNITO_CLIENT_ID`
   - `NEXT_PUBLIC_COGNITO_DOMAIN`

4. MediaPipe WASM files are in `public/mediapipe/` and will be deployed automatically

### Cognito Setup
1. Create User Pool with email as username
2. Create App Client (public client, no secret)
3. Configure callback URLs:
   - Sign-in: `https://your-domain.amplifyapp.com/sign-in`
   - Sign-out: `https://your-domain.amplifyapp.com/sign-in`
4. Note User Pool ID and Client ID for frontend config

## API Contract

### POST /interview/start
```json
Request:  { "userId": "string", "role": "string", "difficulty": "easy|medium|hard", "language": "string", "jdText?": "string", "resumeText?": "string" }
Response: { "sessionId": "string", "firstQuestion": "string", "questionNumber": 1, "totalQuestions": 5 }
```

### POST /interview/answer
```json
Request:  { "sessionId": "string", "answer": "string", "questionNumber": 1, "bodyLanguageMetrics?": {...} }
Response: { "nextQuestion": "string|null", "questionNumber": 2, "totalQuestions": 5, "isComplete": false, "evaluation": {...} }
```

### POST /interview/report
```json
Request:  { "sessionId": "string", "userId": "string", "qaHistory": [...], "bodyLanguageMetrics": [...] }
Response: { "report": {...} }
```

### GET /interviews?userId=xxx
```json
Response: { "interviews": [{ "sessionId", "role", "difficulty", "overallScore", "date", "durationMinutes", "status" }] }
```

## Scripts

```bash
# Frontend
cd frontend
npm run dev      # Development server
npm run build    # Production build
npm run lint     # ESLint
npm run start    # Production server

# Mock Backend (from project root)
node mock-server.js
```

## License

MIT