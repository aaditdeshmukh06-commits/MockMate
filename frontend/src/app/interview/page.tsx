'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useApp } from '@/lib/store';
import { usePresence, useBodyLanguageCollector } from '@/lib/use-presence';
import { ProtectedRoute } from '@/lib/auth-guard';
import type { BodyLanguageMetrics } from '@/lib/types';
import type { RetryAction } from '@/lib/api';

interface QuestionTimerProps {
  timeRemaining: number;
  totalTime: number;
}

function QuestionTimer({ timeRemaining, totalTime }: QuestionTimerProps) {
  const progress = (timeRemaining / totalTime) * 100;
  const minutes = Math.floor(timeRemaining / 60);
  const seconds = timeRemaining % 60;
  const isWarning = timeRemaining < 60;

  return (
    <div className="flex items-center gap-4">
      <div className="flex-1 h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-1000 ${
            isWarning ? 'bg-red-500' : 'bg-blue-600'
          }`}
          style={{ width: `${progress}%` }}
        />
      </div>
      <span className={`font-mono text-lg font-semibold ${isWarning ? 'text-red-500' : 'text-gray-900 dark:text-white'}`}>
        {minutes}:{seconds.toString().padStart(2, '0')}
      </span>
    </div>
  );
}

interface PresenceIndicatorProps {
  presence: ReturnType<typeof usePresence>['presence'];
  mode: ReturnType<typeof usePresence>['mode'];
}

function PresenceIndicator({ presence, mode }: PresenceIndicatorProps) {
  const metrics = [
    { label: 'Eye Contact', value: Math.round(Math.min(100, Math.max(0, presence.eyeContact))), color: 'text-blue-500' },
    { label: 'Posture', value: Math.round(Math.min(100, Math.max(0, presence.posture))), color: 'text-green-500' },
    { label: 'Gestures', value: Math.round(Math.min(100, Math.max(0, presence.gestures))), color: 'text-purple-500' },
    { label: 'Attention', value: Math.round(Math.min(100, Math.max(0, presence.attention))), color: 'text-orange-500' },
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-4 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900 dark:text-white">Presence Metrics</h3>
        <span className={`px-2 py-1 text-xs rounded-full ${
          presence.isPresent ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
        }`}>
          {presence.isPresent ? '● Active' : '○ Inactive'}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        {metrics.map((metric) => (
          <div key={metric.label} className="text-center">
            <div className="relative w-20 h-20 mx-auto mb-2">
              <svg className="w-full h-full transform -rotate-90">
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="8"
                  className="text-gray-200 dark:text-gray-700"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="45"
                  fill="none"
                  stroke={metric.color.replace('text-', '')}
                  strokeWidth="8"
                  strokeDasharray={283}
                  strokeDashoffset={283 - (283 * metric.value) / 100}
                  strokeLinecap="round"
                  className="transition-all duration-500"
                />
              </svg>
              <span className="absolute inset-0 flex items-center justify-center text-2xl font-bold text-gray-900 dark:text-white">
                {metric.value}%
              </span>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400">{metric.label}</p>
          </div>
        ))}
      </div>

      <div className="text-center text-sm text-gray-500 dark:text-gray-400">
        Mode: <span className="font-medium capitalize">{mode}</span>
      </div>
    </div>
  );
}

function InterviewContent() {
  const router = useRouter();
  const { state, startInterview, submitAnswer, retryLastAction, clearRetry } = useApp();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [showSetup, setShowSetup] = useState(true);
  const [formData, setFormData] = useState<{
    role: string;
    difficulty: 'easy' | 'medium' | 'hard';
    language: string;
    jdText: string;
    resumeText: string;
  }>({
    role: 'Software Engineer',
    difficulty: 'medium',
    language: 'English',
    jdText: '',
    resumeText: '',
  });
  const [answer, setAnswer] = useState('');
  const [timeRemaining, setTimeRemaining] = useState(300);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [elapsedMinutes, setElapsedMinutes] = useState(0);
  const [answerError, setAnswerError] = useState('');

  // Ref to hold the latest handleSubmit for use in effects
  const handleSubmitRef = useRef<() => Promise<void>>(null);

  const { presence, mode } = usePresence(videoRef, {
    enabled: isInterviewActive,
    mode: 'mediapipe',
    onMetrics: () => {
      // Metrics are collected automatically by useBodyLanguageCollector
    },
  });

  const { metrics: bodyLanguageMetrics, addMetrics, clear: clearMetrics } = useBodyLanguageCollector();

  // Define handleSubmit early so it can be used in effects
  const handleSubmit = useCallback(async () => {
    if (!state.currentSession || isSubmitting) return;

    const trimmed = answer.trim();
    const wordCount = trimmed.split(/\s+/).filter(w => w.length > 0).length;

    // Validate minimum 5 words
    if (!trimmed || wordCount < 5) {
      setAnswerError('Please give a more complete answer (at least 5 words)');
      return;
    }

    setAnswerError('');
    setIsSubmitting(true);

    // Get latest body language metrics
    const latestMetrics = bodyLanguageMetrics[bodyLanguageMetrics.length - 1];

    try {
      await submitAnswer(trimmed, latestMetrics);
      setAnswer('');
      setTimeRemaining(300);
    } finally {
      // Always reset submitting state, even if submitAnswer throws
      setIsSubmitting(false);
    }
  }, [state.currentSession, answer, isSubmitting, submitAnswer, bodyLanguageMetrics]);

  // Update handleSubmit ref
  useEffect(() => {
    handleSubmitRef.current = handleSubmit;
  }, [handleSubmit]);

  // Timer effect
  useEffect(() => {
    if (!isInterviewActive || !state.currentSession) return;

    let initialTimeSet = false;
    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        // Set initial time on first run
        if (!initialTimeSet) {
          initialTimeSet = true;
          return 300;
        }
        if (prev <= 1) {
          // Auto-submit when time runs out
          handleSubmitRef.current?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isInterviewActive, state.currentSession]);

  // Collect body language metrics periodically
  useEffect(() => {
    if (!isInterviewActive) return;

    const interval = setInterval(() => {
      if (presence.isPresent) {
        const metrics: BodyLanguageMetrics = {
          timestamp: Date.now(),
          eyeContactScore: presence.eyeContact,
          postureScore: presence.posture,
          gestureScore: presence.gestures,
          attentionScore: presence.attention,
          presenceDetected: true,
        };
        addMetrics(metrics);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [isInterviewActive, presence, addMetrics]);

  // Update elapsed time
  useEffect(() => {
    if (!isInterviewActive || !state.currentSession) return;

    const interval = setInterval(() => {
      setElapsedMinutes(Math.floor((Date.now() - state.currentSession!.startTime) / 60000));
    }, 60000);

    return () => clearInterval(interval);
  }, [isInterviewActive, state.currentSession]);

  const handleSetupSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setShowSetup(false);
    await startInterview(formData);
    setIsInterviewActive(true);
    clearMetrics();
  };

  const handleStartNew = () => {
    setShowSetup(true);
    setIsInterviewActive(false);
    setAnswer('');
    setTimeRemaining(300);
  };

  // Show setup form
  if (showSetup || !state.currentSession) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
        <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-8">
                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">🎤 MockMate</span>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <Link href="/dashboard" className="block mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700 text-center">
              <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">🎤 MockMate</span>
            </div>
          </Link>
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Start New Interview</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-2">Configure your mock interview session</p>
            </div>

            <form onSubmit={handleSetupSubmit} className="space-y-6">
              {/* Retry banner for startInterview failures */}
              {state.error && state.retryAction?.type === 'startInterview' && (
                <div className="p-4 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-yellow-600 dark:text-yellow-400">⚠</span>
                      <span className="text-sm text-yellow-800 dark:text-yellow-200">{state.error}</span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={retryLastAction}
                        disabled={state.isLoading}
                        className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-400 text-white text-sm font-medium rounded-lg transition-colors"
                      >
                        {state.isLoading ? 'Retrying...' : 'Retry'}
                      </button>
                      <button
                        type="button"
                        onClick={clearRetry}
                        className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              )}
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Target Role
                </label>
                <select
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                >
                  <option value="Software Engineer">Software Engineer</option>
                  <option value="Frontend Developer">Frontend Developer</option>
                  <option value="Backend Developer">Backend Developer</option>
                  <option value="Full Stack Developer">Full Stack Developer</option>
                  <option value="DevOps Engineer">DevOps Engineer</option>
                  <option value="Data Scientist">Data Scientist</option>
                  <option value="Product Manager">Product Manager</option>
                  <option value="Other">Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Difficulty
                </label>
                <div className="flex gap-4">
                  {(['easy', 'medium', 'hard'] as const).map((diff) => (
                    <label key={diff} className="flex-1">
                      <input
                        type="radio"
                        name="difficulty"
                        value={diff}
                        checked={formData.difficulty === diff}
                        onChange={(e) => setFormData(prev => ({ ...prev, difficulty: e.target.value as 'easy' | 'medium' | 'hard' }))}
                        className="sr-only peer"
                      />
                      <div className={`p-4 rounded-lg border-2 text-center cursor-pointer transition-colors ${
                        formData.difficulty === diff
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                      }`}>
                        <p className="font-medium capitalize text-gray-900 dark:text-white">{diff}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <label htmlFor="language" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Language
                </label>
                <select
                  id="language"
                  value={formData.language}
                  onChange={(e) => setFormData(prev => ({ ...prev, language: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                >
                  <option value="English">English</option>
                  <option value="Hindi">Hindi</option>
                  <option value="English + Hindi">English + Hindi</option>
                </select>
              </div>

              <div>
                <label htmlFor="jdText" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Job Description (Optional)
                </label>
                <textarea
                  id="jdText"
                  value={formData.jdText}
                  onChange={(e) => setFormData(prev => ({ ...prev, jdText: e.target.value }))}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  placeholder="Paste the job description here for tailored questions..."
                />
              </div>

              <div>
                <label htmlFor="resumeText" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Resume / Background (Optional)
                </label>
                <textarea
                  id="resumeText"
                  value={formData.resumeText}
                  onChange={(e) => setFormData(prev => ({ ...prev, resumeText: e.target.value }))}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                  placeholder="Paste your resume or background info for personalized interview..."
                />
              </div>

              <button
                type="submit"
                disabled={state.isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-4 rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
              >
                {state.isLoading ? 'Starting Interview...' : 'Start Interview'}
              </button>
            </form>
          </div>
        </main>
      </div>
    );
  }

  // Interview complete - show report link
  if (!state.currentSession.isActive && state.currentReport) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700 max-w-md w-full text-center">
          <div className="w-20 h-20 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-6">
            <span className="text-4xl">✅</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Interview Complete!</h1>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            You&apos;ve completed all {state.currentSession.totalQuestions} questions.
            Your report is ready.
          </p>
          <div className="space-y-3">
            <button
              onClick={() => router.push('/reports')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              View Report
            </button>
            <button
              onClick={handleStartNew}
              className="w-full bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white font-semibold py-3 px-4 rounded-lg transition-colors"
            >
              Start Another Interview
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Active interview UI
  const session = state.currentSession;
  const progress = (session.currentQuestion / session.totalQuestions) * 100;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-4">
              <Link href="/dashboard" className="text-xl font-bold text-blue-600 dark:text-blue-400 hover:underline">🎤 MockMate</Link>
              <span className="px-3 py-1 text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full">
                Live Session
              </span>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden sm:block w-48">
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-600 transition-all duration-500"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Question {session.currentQuestion} of {session.totalQuestions}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Left: Question & Answer */}
          <div className="lg:col-span-2 space-y-6">
            {/* Question Card */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Question {session.currentQuestion}</h2>
                <QuestionTimer timeRemaining={timeRemaining} totalTime={300} />
              </div>
              <p className="text-xl text-gray-900 dark:text-white leading-relaxed">
                {session.currentQuestionText}
              </p>
            </div>

            {/* Answer Input */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Your Answer</h3>
              <textarea
                value={answer}
                onChange={(e) => {
                  setAnswer(e.target.value);
                  // Clear error when user starts typing
                  if (answerError) setAnswerError('');
                }}
                rows={8}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none resize-none font-medium"
                placeholder="Type your answer here..."
                disabled={isSubmitting}
              />
              {answerError && (
                <p className="mt-2 text-sm text-red-600 dark:text-red-400" role="alert">{answerError}</p>
              )}
              {/* Retry banner for submitAnswer failures */}
              {state.error && state.retryAction?.type === 'submitAnswer' && (
                <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className="text-yellow-600 dark:text-yellow-400">⚠</span>
                      <span className="text-sm text-yellow-800 dark:text-yellow-200">{state.error}</span>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={retryLastAction}
                        disabled={state.isLoading}
                        className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 disabled:bg-yellow-400 text-white text-sm font-medium rounded-lg transition-colors"
                      >
                        {state.isLoading ? 'Retrying...' : 'Retry'}
                      </button>
                      <button
                        onClick={clearRetry}
                        className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 text-sm font-medium rounded-lg transition-colors"
                      >
                        Dismiss
                      </button>
                    </div>
                  </div>
                </div>
              )}
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <video
                    ref={videoRef}
                    className="w-20 h-20 rounded-lg border border-gray-200 dark:border-gray-600"
                    autoPlay
                    muted
                    playsInline
                    style={{ display: mode === 'mediapipe' ? 'block' : 'none' }}
                  />
                  <span>
                    Camera: {presence.isPresent ? '🟢 Detected' : '🔴 Not detected'}
                  </span>
                </div>
                <button
                  onClick={handleSubmit}
                  disabled={isSubmitting || !answer.trim() || answerError !== ''}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Answer'}
                </button>
              </div>
            </div>
          </div>

          {/* Right: Presence & Progress */}
          <div className="space-y-6">
            {/* Progress Gauge */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4 text-center">Interview Progress</h3>
              <div className="relative w-48 h-48 mx-auto">
                <svg className="w-full h-full transform -rotate-90">
                  <circle
                    cx="96"
                    cy="96"
                    r="90"
                    fill="none"
                    stroke="#E5E7EB"
                    strokeWidth="12"
                    className="dark:stroke-gray-700"
                  />
                  <circle
                    cx="96"
                    cy="96"
                    r="90"
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="12"
                    strokeDasharray={565}
                    strokeDashoffset={565 - (565 * progress) / 100}
                    strokeLinecap="round"
                    className="transition-all duration-500"
                  />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold text-gray-900 dark:text-white">{Math.round(progress)}%</span>
                  <span className="text-sm text-gray-500 dark:text-gray-400">{session.currentQuestion}/{session.totalQuestions}</span>
                </div>
              </div>
            </div>

            {/* Presence Metrics */}
            <PresenceIndicator presence={presence} mode={mode} />

            {/* Quick Stats */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 p-4">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Session Stats</h3>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Questions Answered</span>
                  <span className="font-medium text-gray-900 dark:text-white">{session.qaHistory.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Body Language Samples</span>
                  <span className="font-medium text-gray-900 dark:text-white">{bodyLanguageMetrics.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500 dark:text-gray-400">Time Elapsed</span>
                  <span className="font-medium text-gray-900 dark:text-white">
                    {elapsedMinutes} min
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function InterviewPage() {
  return (
    <ProtectedRoute>
      <InterviewContent />
    </ProtectedRoute>
  );
}