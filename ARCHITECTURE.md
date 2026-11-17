# MockMate Architecture

## Overview

MockMate is a full-stack AI-powered mock interview platform with a modern Next.js frontend and serverless AWS backend.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER FLOW                                       │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐     ┌──────────────┐     ┌─────────────┐     ┌────────────┐
  │  Browser │────▶│   Next.js    │────▶│  Amplify    │────▶│  Cognito   │
  │  (React) │     │   Frontend   │     │  Hosting    │     │  Auth      │
  └──────────┘     └──────────────┘     └─────────────┘     └────────────┘
       │                   │                                      │
       │                   ▼                                      │
       │            ┌──────────────┐                              │
       │            │  MediaPipe   │                              │
       │            │  Face Mesh   │                              │
       │            └──────────────┘                              │
       │                   │                                      │
       ▼                   ▼                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API GATEWAY (REST)                                │
│                    (Cognito Authorizer + CORS)                               │
└─────────────────────────────────────────────────────────────────────────────┘
       │                    │                    │                    │
       ▼                    ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Lambda:    │      │  Lambda:    │      │  Lambda:    │      │  Lambda:    │
│  start      │      │  answer     │      │  report     │      │  history    │
│  interview  │      │  interview  │      │  build      │      │  get        │
└─────────────┘      └─────────────┘      └─────────────┘      └─────────────┘
       │                    │                    │                    │
       └────────────────────┴────────────────────┴────────────────────┘
                                    │
                                    ▼
                          ┌─────────────────┐
                          │   DynamoDB      │
                          │  (Interviews,   │
                          │   Reports,      │
                          │   Users)        │
                          └─────────────────┘
```

## Frontend Architecture (Next.js 16)

### App Router Structure
```
src/app/
├── layout.tsx              # Root layout with Providers
├── page.tsx                # Landing page (redirects to dashboard)
├── providers.tsx           # AppProvider + Authenticator.Provider
├── sign-in/
│   └── page.tsx            # Cognito Authenticator UI
├── dashboard/
│   └── page.tsx            # Metrics, quick actions, history
├── interview/
│   └── page.tsx            # Live interview with timer, camera
├── reports/
│   └── page.tsx            # Reports list + detail view
└── settings/
    └── page.tsx            # Preferences, account management
```

### State Management (React Context + useReducer)
```typescript
// src/lib/store.tsx
interface AppState {
  user: User | null;
  interviewSession: InterviewSession | null;
  interviewHistory: InterviewHistoryItem[];
  currentReport: Report | null;
  preferences: UserPreferences;
}

type Action =
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_SESSION'; payload: InterviewSession }
  | { type: 'ADD_QA'; payload: QAItem }
  | { type: 'ADD_BODY_LANGUAGE'; payload: BodyLanguageMetrics }
  | { type: 'SET_REPORT'; payload: Report }
  | { type: 'SET_HISTORY'; payload: InterviewHistoryItem[] }
  | { type: 'UPDATE_PREFERENCES'; payload: UserPreferences }
  | { type: 'LOGOUT' };
```

### Key Libraries

**API Client** (`src/lib/api.ts`)
- Singleton `APIClient` with fetch wrapper
- Error handling via `APIError` class
- Endpoints: `createSession`, `submitAnswer`, `buildReport`, `getHistory`, `saveReport`

**Body Language Detection** (`src/lib/use-presence.ts`)
- MediaPipe Face Mesh integration
- Mock fallback when camera unavailable
- Real-time metrics: eyeContact, posture, gestures, attention, presence
- `useBodyLanguageCollector` for periodic sampling during interview

**Authentication** (`src/lib/amplify-config.ts`, `src/lib/auth-guard.tsx`)
- Amplify v6 configuration with Cognito
- `ProtectedRoute` component for route guards
- Client-side only configuration to avoid SSR issues

## Backend Architecture (AWS Lambda)

### API Endpoints

| Method | Path | Description | Lambda Function |
|--------|------|-------------|-----------------|
| POST | `/interview/start` | Create new interview session | `mockmate-start` |
| POST | `/interview/answer` | Submit answer, get next question | `mockmate-answer` |
| POST | `/interview/report` | Generate final report | `mockmate-report` |
| GET | `/interviews` | Get user interview history | `mockmate-history` |
| POST | `/interview/report/save` | Save report (no-op) | `mockmate-save` |

### Data Models

**Interview Session** (DynamoDB)
```json
{
  "sessionId": "string (PK)",
  "userId": "string (GSI)",
  "role": "string",
  "difficulty": "easy|medium|hard",
  "language": "string",
  "status": "in_progress|completed",
  "qaHistory": "QAItem[]",
  "bodyLanguageMetrics": "BodyLanguageMetrics[]",
  "createdAt": "ISO timestamp",
  "updatedAt": "ISO timestamp"
}
```

**Report** (DynamoDB)
```json
{
  "reportId": "string (PK)",
  "sessionId": "string (GSI)",
  "userId": "string",
  "overallScore": "number",
  "categoryScores": "CategoryScores",
  "qaHistory": "QAItem[]",
  "bodyLanguageSummary": "BodyLanguageSummary",
  "aiSummary": "AISummary",
  "createdAt": "ISO timestamp"
}
```

### Lambda Implementation Notes

1. **Start Interview** (`mockmate-start`)
   - Validate user via Cognito JWT
   - Generate sessionId
   - Fetch first question from question bank (role + difficulty)
   - Store session in DynamoDB
   - Return sessionId + first question

2. **Submit Answer** (`mockmate-answer`)
   - Validate session exists and belongs to user
   - Call Bedrock/Claude for answer evaluation
   - Generate next question or mark complete
   - Store QA + body language metrics
   - Return evaluation + next question

3. **Build Report** (`mockmate-report`)
   - Aggregate all QA evaluations
   - Calculate category scores
   - Compute body language averages
   - Call Bedrock/Claude for AI summary
   - Store report in DynamoDB
   - Return full report

4. **Get History** (`mockmate-history`)
   - Query DynamoDB by userId (GSI)
   - Return completed interviews with scores

## Authentication Flow

```
1. User visits /sign-in
2. Amplify Authenticator renders Cognito Hosted UI
3. User signs up/in with email + password
4. Cognito returns JWT tokens (access, id, refresh)
5. Amplify stores tokens in localStorage/IndexedDB
6. Frontend calls getCurrentUser() to decode idToken
7. User object stored in React Context (AppState)
8. ProtectedRoute checks state.user on each navigation
9. API calls include Authorization: Bearer <accessToken>
10. API Gateway validates token via Cognito Authorizer
```

## Body Language Pipeline

```
Camera Feed (getUserMedia)
       │
       ▼
┌──────────────────┐
│  MediaPipe Face  │
│     Mesh         │
│  (WASM/WebGL)    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Landmark        │
│  Processing      │
│  (478 points)    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Metric          │
│  Calculation     │
│                  │
│  Eye Contact:    │  ← Iris position relative to eye corners
│  Posture:        │  ← Nose/forehead alignment
│  Gestures:       │  ← Hand/face distance changes
│  Attention:      │  ← Head pose + eye gaze vector
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Sampling        │
│  (1Hz during    │
│  interview)      │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│  Submit with     │
│  each answer     │
│  (bodyLanguage   │
│   Metrics)       │
└──────────────────┘
```

### Fallback Strategy
- If `getUserMedia` fails → Mock mode (random realistic metrics)
- If MediaPipe fails to load → Mock mode
- If `enableCamera` preference is false → Mock mode
- Mock mode generates plausible metrics (70-95 range)

## Deployment Architecture

### Amplify Console (Frontend)
```
GitHub Push
     │
     ▼
┌──────────────────┐
│  Amplify Build   │
│  (amplify.yml)   │
│                  │
│  npm ci          │
│  npm run build   │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Deploy to       │
│  Amplify CDN     │
│  (CloudFront)    │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Environment     │
│  Variables       │
│                  │
│  NEXT_PUBLIC_*   │
└──────────────────┘
```

### Lambda + API Gateway (Backend)
```
SAM/Serverless/CDK Deploy
     │
     ▼
┌──────────────────┐
│  API Gateway     │
│  (Regional)      │
│                  │
│  CORS +          │
│  Cognito Author  │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  Lambda Functions│
│  (Node.js 20.x)  │
│                  │
│  VPC (optional)  │
└──────────────────┘
     │
     ▼
┌──────────────────┐
│  DynamoDB        │
│  (On-Demand)     │
└──────────────────┘
```

### Environment Variables (Production)

**Frontend (Amplify)**
```
NEXT_PUBLIC_API_BASE_URL=https://xxx.execute-api.region.amazonaws.com/prod
NEXT_PUBLIC_COGNITO_USER_POOL_ID=us-east-1_XXXXXXXXX
NEXT_PUBLIC_COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
NEXT_PUBLIC_COGNITO_DOMAIN=your-domain.auth.us-east-1.amazoncognito.com
```

**Backend (Lambda)**
```
USE_MOCK=false
TABLE_NAME=MockMateInterviews
REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

## Security Considerations

1. **Authentication**: All API routes protected by Cognito Authorizer
2. **Authorization**: Users can only access their own data (userId in JWT)
3. **CORS**: Configured to allow only Amplify domain
4. **Secrets**: No secrets in frontend; Lambda uses IAM roles
5. **Rate Limiting**: API Gateway usage plans + throttling
6. **HTTPS**: Enforced by Amplify + API Gateway

## Monitoring & Observability

- **Frontend**: Amplify access logs + custom metrics
- **Backend**: CloudWatch Logs + X-Ray tracing
- **API**: API Gateway CloudWatch metrics
- **Auth**: Cognito sign-in/up metrics

## Future Enhancements

1. **Voice Input**: Polly TTS + Transcribe for voice interviews
2. **Real-time Collaboration**: WebRTC for live interviewer
3. **Advanced Analytics**: Trends, comparisons, skill gaps
4. **Question Bank**: Dynamic questions from JD/resume via Bedrock
5. **Multi-language**: Full i18n support