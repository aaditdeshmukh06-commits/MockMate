/**
 * MockMate - Mock Backend Server
 * Simulates Lambda API endpoints for local development
 * Run with: node mock-server.js
 */

const http = require('http');
const url = require('url');

// In-memory storage
const sessions = new Map();
const reports = new Map();
const users = new Map();

// Mock data generators
function generateSessionId() {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

function generateQuestion(role, difficulty, questionNumber) {
  const questions = {
    easy: {
      'Software Engineer': [
        'Tell me about yourself and your background.',
        'What programming languages are you most comfortable with?',
        'Describe a project you worked on recently.',
        'How do you approach debugging a difficult issue?',
        'What do you know about our company?'
      ],
      'Data Scientist': [
        'Tell me about your experience with data analysis.',
        'What tools do you use for data visualization?',
        'Explain a machine learning project you\'ve worked on.',
        'How do you handle missing data in a dataset?',
        'What interests you about this role?'
      ],
      'Product Manager': [
        'Tell me about a product you launched.',
        'How do you prioritize features?',
        'Describe a time you had to say no to a stakeholder.',
        'How do you measure product success?',
        'What\'s your favorite product and why?'
      ]
    },
    medium: {
      'Software Engineer': [
        'Explain the difference between REST and GraphQL.',
        'How would you design a URL shortener service?',
        'Describe a time you optimized a slow database query.',
        'What are the trade-offs of microservices vs monolith?',
        'How do you ensure code quality in your team?'
      ],
      'Data Scientist': [
        'Explain bias-variance tradeoff.',
        'How would you detect fraud in credit card transactions?',
        'Describe a time your model failed in production.',
        'What\'s the difference between L1 and L2 regularization?',
        'How do you explain technical results to non-technical stakeholders?'
      ],
      'Product Manager': [
        'How do you handle competing priorities from different teams?',
        'Describe a product decision you made based on data.',
        'How would you improve our onboarding flow?',
        'Tell me about a time you failed and what you learned.',
        'How do you balance technical debt vs new features?'
      ]
    },
    hard: {
      'Software Engineer': [
        'Design a distributed rate limiter.',
        'How would you implement eventual consistency?',
        'Explain the CAP theorem with real-world examples.',
        'Design a system like Uber\'s dispatch.',
        'How do you handle distributed transactions?'
      ],
      'Data Scientist': [
        'Design an A/B testing framework.',
        'How would you build a recommendation system from scratch?',
        'Explain transformer architecture attention mechanism.',
        'How do you handle concept drift in production models?',
        'Design an experiment to measure feature impact.'
      ],
      'Product Manager': [
        'How would you enter a new market with an existing product?',
        'Design a pricing strategy for a SaaS product.',
        'How do you manage a product through its lifecycle?',
        'Describe a strategic pivot you led.',
        'How do you align engineering and business goals?'
      ]
    }
  };

  const roleQuestions = (questions[difficulty] && questions[difficulty][role]) || (questions[difficulty] && questions[difficulty]['Software Engineer']) || [];
  return roleQuestions[questionNumber - 1] || 'Tell me about a challenging problem you solved.';
}

function generateEvaluation(answer, questionNumber) {
  // Improved evaluation: check for actual words, penalize gibberish
  const trimmed = answer.trim();
  const words = trimmed.split(/\s+/).filter(w => w.length > 0);
  const wordCount = words.length;
  const charCount = trimmed.length;

  // Detect gibberish: repeated characters, low unique character ratio, no vowels
  const uniqueChars = new Set(trimmed.toLowerCase()).size;
  const charDiversity = uniqueChars / Math.max(1, charCount);
  const hasVowels = /[aeiou]/i.test(trimmed);
  const hasRepeatedChars = /(.)\1{3,}/.test(trimmed); // 4+ same chars in a row
  const avgWordLength = wordCount > 0 ? charCount / wordCount : 0;

  // Gibberish penalty
  let gibberishPenalty = 0;
  if (!hasVowels) gibberishPenalty += 30;
  if (hasRepeatedChars) gibberishPenalty += 25;
  if (charDiversity < 0.15) gibberishPenalty += 20; // Very low character diversity
  if (avgWordLength > 15) gibberishPenalty += 15; // Suspiciously long "words"
  if (wordCount < 3) gibberishPenalty += 20; // Too few words

  // Positive signals
  const hasExamples = /example|instance|project|experience|built|created|developed|implemented|solved/i.test(trimmed);
  const hasTechnical = /api|database|algorithm|framework|architecture|system|design|scale|performance|optimize|debug|test|deploy|ci\/cd|docker|kubernetes|aws|cloud/i.test(trimmed);
  const hasStructure = /first|second|then|finally|because|therefore|however|additionally|furthermore/i.test(trimmed);

  // Base score: 20-40 based on word count (capped at 30 words)
  let baseScore = Math.min(20 + wordCount, 50);

  // Bonuses
  if (hasExamples) baseScore += 10;
  if (hasTechnical) baseScore += 10;
  if (hasStructure) baseScore += 5;
  if (wordCount >= 20) baseScore += 5; // Good length
  if (wordCount >= 50) baseScore += 5; // Very thorough

  // Apply gibberish penalty
  baseScore = Math.max(10, baseScore - gibberishPenalty);
  baseScore = Math.min(baseScore, 95);

  // Generate feedback based on quality
  let feedback = '';
  if (gibberishPenalty > 30) {
    feedback = 'Answer appears to be gibberish or too short. Please provide a meaningful response.';
  } else if (gibberishPenalty > 15) {
    feedback = 'Answer needs more substance. Try to elaborate with specific examples.';
  } else if (baseScore >= 70) {
    feedback = 'Strong answer with good detail and relevant examples.';
  } else if (baseScore >= 50) {
    feedback = 'Decent answer. Consider adding more specific examples or technical details.';
  } else {
    feedback = 'Answer is too brief. Please elaborate more on your experience.';
  }

  return {
    score: Math.round(baseScore),
    confidence: Math.round(baseScore * 0.9),
    clarity: Math.round(baseScore * 0.95),
    relevance: Math.round(baseScore * 0.9),
    technicalAccuracy: Math.round(baseScore * 0.85),
    communication: Math.round(baseScore * 0.9),
    strengths: hasExamples ? ['Good use of examples', 'Clear communication'] : hasTechnical ? ['Technical knowledge shown'] : ['Attempted to answer'],
    improvements: gibberishPenalty > 15 ? ['Provide a coherent, meaningful answer', 'Use real words and sentences'] : hasTechnical ? ['Add more technical depth', 'Include specific examples'] : ['Add specific examples', 'Include technical details', 'Elaborate more on your experience'],
    feedback
  };
}

function generateReport(sessionId, userId, role, difficulty, qaHistory, bodyLanguageMetrics) {
  const scores = qaHistory.map(q => q.evaluation.score);
  const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 75;

  const blScores = bodyLanguageMetrics.length > 0 ? {
    eyeContact: bodyLanguageMetrics.reduce((a, b) => a + b.eyeContactScore, 0) / bodyLanguageMetrics.length,
    posture: bodyLanguageMetrics.reduce((a, b) => a + b.postureScore, 0) / bodyLanguageMetrics.length,
    gestures: bodyLanguageMetrics.reduce((a, b) => a + b.gestureScore, 0) / bodyLanguageMetrics.length,
    attention: bodyLanguageMetrics.reduce((a, b) => a + b.attentionScore, 0) / bodyLanguageMetrics.length,
    presence: bodyLanguageMetrics.filter(b => b.presenceDetected).length / bodyLanguageMetrics.length * 100
  } : { eyeContact: 80, posture: 75, gestures: 70, attention: 85, presence: 90 };

  const categoryScores = {
    technical: Math.round(avgScore * 0.95),
    communication: Math.round(avgScore * 1.05),
    confidence: Math.round(avgScore * 0.9),
    problemSolving: Math.round(avgScore * 0.88),
    bodyLanguage: Math.round((blScores.eyeContact + blScores.posture + blScores.gestures + blScores.attention) / 4)
  };

  const overallScore = Math.round(Object.values(categoryScores).reduce((a, b) => a + b, 0) / 5);

  return {
    sessionId,
    userId,
    role,
    difficulty,
    overallScore,
    categoryScores,
    qaHistory,
    bodyLanguageSummary: {
      averageEyeContact: Math.round(blScores.eyeContact),
      averagePosture: Math.round(blScores.posture),
      averageGestures: Math.round(blScores.gestures),
      averageAttention: Math.round(blScores.attention),
      presencePercentage: Math.round(blScores.presence),
      feedback: [
        blScores.eyeContact > 75 ? 'Good eye contact maintained' : 'Work on maintaining eye contact',
        blScores.posture > 70 ? 'Good posture' : 'Improve posture during interview'
      ]
    },
    aiSummary: {
      overallFeedback: `Strong performance in ${role} interview. ${overallScore > 80 ? 'Excellent' : overallScore > 60 ? 'Good' : 'Needs improvement'} overall.`,
      strengths: ['Technical knowledge', 'Clear communication', 'Problem-solving approach'],
      improvements: ['Add more specific examples', 'Slow down speech pace', 'Elaborate on technical decisions'],
      recommendations: ['Practice STAR method', 'Record yourself answering', 'Review system design fundamentals'],
      candidateLevel: overallScore > 80 ? 'senior' : overallScore > 60 ? 'intermediate' : 'junior'
    },
    createdAt: new Date().toISOString(),
    durationMinutes: Math.round((Date.now() - (sessions.get(sessionId)?.startTime || Date.now())) / 60000) || 15
  };
}

// HTTP Server
const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  const method = req.method;

  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  // Parse body for POST requests
  let body = '';
  if (method === 'POST') {
    for await (const chunk of req) {
      body += chunk;
    }
  }

  try {
    // POST /interview/start
    if (method === 'POST' && pathname === '/interview/start') {
      const data = JSON.parse(body);
      const sessionId = generateSessionId();
      const firstQuestion = generateQuestion(data.role, data.difficulty, 1);

      const session = {
        sessionId,
        userId: data.userId,
        role: data.role,
        difficulty: data.difficulty,
        language: data.language,
        currentQuestion: 1,
        totalQuestions: 5,
        qaHistory: [],
        bodyLanguageMetrics: [],
        startTime: Date.now(),
        isActive: true
      };
      sessions.set(sessionId, session);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        sessionId,
        firstQuestion,
        questionNumber: 1,
        totalQuestions: 5
      }));
      return;
    }

    // POST /interview/answer
    if (method === 'POST' && pathname === '/interview/answer') {
      const data = JSON.parse(body);
      const session = sessions.get(data.sessionId);

      if (!session) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Session not found', code: 'SESSION_NOT_FOUND', status: 404 }));
        return;
      }

      const evaluation = generateEvaluation(data.answer, data.questionNumber);
      const qaItem = {
        questionNumber: data.questionNumber,
        question: session.currentQuestionText || generateQuestion(session.role, session.difficulty, data.questionNumber),
        answer: data.answer,
        evaluation,
        bodyLanguageMetrics: data.bodyLanguageMetrics
      };

      session.qaHistory.push(qaItem);
      if (data.bodyLanguageMetrics) {
        session.bodyLanguageMetrics.push(data.bodyLanguageMetrics);
      }

      const nextQuestionNumber = data.questionNumber + 1;
      const isComplete = nextQuestionNumber > session.totalQuestions;

      let nextQuestion = null;
      if (!isComplete) {
        nextQuestion = generateQuestion(session.role, session.difficulty, nextQuestionNumber);
        session.currentQuestion = nextQuestionNumber;
        session.currentQuestionText = nextQuestion;
      } else {
        session.isActive = false;
      }

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        nextQuestion,
        questionNumber: nextQuestionNumber,
        totalQuestions: session.totalQuestions,
        isComplete,
        evaluation
      }));
      return;
    }

    // POST /interview/report
    if (method === 'POST' && pathname === '/interview/report') {
      const data = JSON.parse(body);
      const session = sessions.get(data.sessionId);

      if (!session) {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'Session not found', code: 'SESSION_NOT_FOUND', status: 404 }));
        return;
      }

      const report = generateReport(
        data.sessionId,
        data.userId,
        session.role,
        session.difficulty,
        data.qaHistory,
        data.bodyLanguageMetrics
      );

      reports.set(data.sessionId, report);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ report }));
      return;
    }

    // GET /interviews?userId=
    if (method === 'GET' && pathname === '/interviews') {
      const userId = parsedUrl.query.userId;

      if (!userId) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ message: 'userId required', code: 'BAD_REQUEST', status: 400 }));
        return;
      }

      const userReports = Array.from(reports.values())
        .filter(r => r.userId === userId)
        .map(r => ({
          sessionId: r.sessionId,
          role: r.role,
          difficulty: r.difficulty,
          overallScore: r.overallScore,
          date: r.createdAt,
          durationMinutes: r.durationMinutes,
          status: 'completed'
        }));

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ interviews: userReports }));
      return;
    }

    // POST /interview/report/save (no-op)
    if (method === 'POST' && pathname === '/interview/report/save') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true }));
      return;
    }

    // Health check
    if (method === 'GET' && pathname === '/health') {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
      return;
    }

    // 404
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'Not found', code: 'NOT_FOUND', status: 404 }));

  } catch (error) {
    console.error('Server error:', error);
    res.writeHead(500, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ message: 'Internal server error', code: 'INTERNAL_ERROR', status: 500 }));
  }
});

const PORT = 3001;
server.listen(PORT, () => {
  console.log(`🚀 MockMate Mock Backend running at http://localhost:${PORT}`);
  console.log('Endpoints:');
  console.log('  POST   /interview/start     - Create interview session');
  console.log('  POST   /interview/answer    - Submit answer');
  console.log('  POST   /interview/report    - Generate report');
  console.log('  GET    /interviews?userId=  - Get interview history');
  console.log('  POST   /interview/report/save - Save report (no-op)');
  console.log('  GET    /health              - Health check');
});