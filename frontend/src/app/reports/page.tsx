'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useApp } from '@/lib/store';
import { ProtectedRoute } from '@/lib/auth-guard';
import type { Report, InterviewHistoryItem } from '@/lib/types';
import type { RetryAction } from '@/lib/api';

interface ReportCardProps {
  report: Report;
}

function ReportCard({ report }: ReportCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Link
      href={`/reports/${report.sessionId}`}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors"
    >
      <div className="flex items-start justify-between gap-4 min-w-0">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white truncate">{report.role}</h3>
            <span className="px-2 py-1 text-xs font-medium rounded-full bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 capitalize flex-shrink-0">
              {report.difficulty}
            </span>
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
            {new Date(report.createdAt).toLocaleDateString()} • {report.durationMinutes} min
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">
            {report.aiSummary.overallFeedback}
          </p>
        </div>
        <div className="min-w-0 text-right">
          <p className={`text-4xl font-bold ${getScoreColor(report.overallScore)}`}>
            {report.overallScore}%
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {report.aiSummary.candidateLevel}
          </p>
        </div>
      </div>
    </Link>
  );
}

interface ReportDetailProps {
  report: Report;
}

function ReportDetail({ report }: ReportDetailProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100 dark:bg-green-900/30';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/30';
    return 'text-red-600 bg-red-100 dark:bg-red-900/30';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{report.role}</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-500 dark:text-gray-400">
              <span>Difficulty: <span className="font-medium text-gray-900 dark:text-white capitalize">{report.difficulty}</span></span>
              <span>Date: <span className="font-medium text-gray-900 dark:text-white">{new Date(report.createdAt).toLocaleDateString()}</span></span>
              <span>Duration: <span className="font-medium text-gray-900 dark:text-white">{report.durationMinutes} min</span></span>
            </div>
          </div>
          <div className="text-right">
            <p className={`text-4xl font-bold ${getScoreColor(report.overallScore).split(' ')[0]} px-4 py-2 rounded-lg`}>
              {report.overallScore}%
            </p>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 capitalize">{report.aiSummary.candidateLevel}</p>
          </div>
        </div>
      </div>

      {/* Category Scores */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[
          { label: 'Technical', score: report.categoryScores.technical },
          { label: 'Communication', score: report.categoryScores.communication },
          { label: 'Confidence', score: report.categoryScores.confidence },
          { label: 'Problem Solving', score: report.categoryScores.problemSolving },
          { label: 'Body Language', score: report.categoryScores.bodyLanguage },
        ].map((cat) => (
          <div key={cat.label} className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">{cat.label}</p>
            <p className={`text-3xl font-bold ${getScoreColor(cat.score).split(' ')[0]}`}>{cat.score}%</p>
          </div>
        ))}
      </div>

      {/* Body Language Summary */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Body Language Analysis</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Eye Contact', value: Math.round(Math.min(100, Math.max(0, report.bodyLanguageSummary.averageEyeContact))) },
            { label: 'Posture', value: Math.round(Math.min(100, Math.max(0, report.bodyLanguageSummary.averagePosture))) },
            { label: 'Gestures', value: Math.round(Math.min(100, Math.max(0, report.bodyLanguageSummary.averageGestures))) },
            { label: 'Attention', value: Math.round(Math.min(100, Math.max(0, report.bodyLanguageSummary.averageAttention))) },
          ].map((metric) => (
            <div key={metric.label} className="text-center">
              <div className="relative w-24 h-24 mx-auto mb-2">
                <svg className="w-full h-full transform -rotate-90">
                  <circle cx="60" cy="60" r="55" fill="none" stroke="#E5E7EB" strokeWidth="8" className="dark:stroke-gray-700" />
                  <circle
                    cx="60"
                    cy="60"
                    r="55"
                    fill="none"
                    stroke="#2563EB"
                    strokeWidth="8"
                    strokeDasharray={345}
                    strokeDashoffset={345 - (345 * metric.value) / 100}
                    strokeLinecap="round"
                    className="transition-all duration-500"
                  />
                </svg>
                <span className="absolute inset-0 flex items-center justify-center text-xl font-bold text-gray-900 dark:text-white">
                  {metric.value}%
                </span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400">{metric.label}</p>
            </div>
          ))}
        </div>
        <div>
          <p className="text-sm text-gray-500 dark:text-gray-400">Presence: {Math.round(report.bodyLanguageSummary.presencePercentage)}%</p>
          {report.bodyLanguageSummary.feedback.length > 0 && (
            <ul className="mt-3 space-y-1">
              {report.bodyLanguageSummary.feedback.map((fb, i) => (
                <li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2">
                  <span className="text-blue-500">•</span> {fb}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* AI Summary */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">AI Performance Summary</h2>
        <div className="prose dark:prose-invert max-w-none space-y-4">
          <div>
            <h3 className="font-semibold text-green-700 dark:text-green-400 mb-2">Strengths</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
              {report.aiSummary.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-red-700 dark:text-red-400 mb-2">Areas for Improvement</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
              {report.aiSummary.improvements.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-blue-700 dark:text-blue-400 mb-2">Recommendations</h3>
            <ul className="list-disc list-inside space-y-1 text-gray-600 dark:text-gray-400">
              {report.aiSummary.recommendations.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>
          <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-2">Overall Feedback</h3>
            <p className="text-gray-600 dark:text-gray-400">{report.aiSummary.overallFeedback}</p>
          </div>
        </div>
      </div>

      {/* Q&A History */}
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Interview Q&A</h2>
        <div className="space-y-4">
          {report.qaHistory.map((qa) => (
            <div key={qa.questionNumber} className="border-l-4 border-blue-500 pl-4 py-2">
              <p className="font-medium text-gray-900 dark:text-white mb-1">
                Q{qa.questionNumber}: {qa.question}
              </p>
              <p className="text-gray-600 dark:text-gray-400 mb-2 ml-4">{qa.answer}</p>
              <div className="flex flex-wrap gap-2 ml-4">
                <span className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded">
                  Score: {qa.evaluation.score}%
                </span>
                <span className="px-2 py-1 text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded">
                  Confidence: {qa.evaluation.confidence}%
                </span>
                <span className="px-2 py-1 text-xs bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 rounded">
                  Clarity: {qa.evaluation.clarity}%
                </span>
              </div>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 ml-4">{qa.evaluation.feedback}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ReportsContent() {
  const { state, loadHistory, saveReport, retryLastAction, clearRetry } = useApp();
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);

  useEffect(() => {
    if (state.user?.id) {
      loadHistory();
    }
  }, [state.user?.id, loadHistory]);

  const completedInterviews = state.interviewHistory.filter(i => i.status === 'completed');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="text-2xl font-bold text-blue-600 dark:text-blue-400">🎤 MockMate</Link>
              <nav className="hidden md:flex items-center gap-6">
                <Link href="/dashboard" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Dashboard</Link>
                <Link href="/interview" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Interview</Link>
                <Link href="/reports" className="text-sm font-medium text-gray-900 dark:text-white">Reports</Link>
                <Link href="/settings" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Settings</Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
                Welcome, {state.user?.name || 'User'}!
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Interview Reports</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Review your performance and track improvement over time</p>
        </div>

        {/* Retry banner for loadHistory failures */}
        {state.error && state.retryAction?.type === 'loadHistory' && (
          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-lg">
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

        {selectedReport ? (
          <div className="flex items-center justify-between mb-6">
            <Link
              href="/reports"
              onClick={() => setSelectedReport(null)}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Back to Reports
            </Link>
            <button
              onClick={saveReport}
              className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-sm"
            >
              Save Report
            </button>
          </div>
        ) : null}

        {selectedReport ? (
          <ReportDetail report={selectedReport} />
        ) : completedInterviews.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-12 text-center border border-gray-100 dark:border-gray-700">
            <span className="text-6xl mb-4 block">📊</span>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">No reports yet</h2>
            <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-md mx-auto">
              Complete an interview to generate your first performance report with detailed analytics and AI feedback.
            </p>
            <Link
              href="/interview"
              className="inline-flex items-center gap-2 px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Start Interview
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {completedInterviews.map((interview) => {
                const overallScore = typeof interview.overallScore === 'number' ? interview.overallScore : 0;
                const candidateLevel = overallScore > 80 ? 'senior' : overallScore > 60 ? 'intermediate' : 'junior';
                const overallFeedback = overallScore > 80
                  ? 'Excellent performance overall.'
                  : overallScore > 60
                  ? 'Good performance overall.'
                  : 'Needs improvement overall.';
                return (
                  <ReportCard
                    key={interview.sessionId}
                    report={{
                      sessionId: interview.sessionId,
                      userId: state.user!.id,
                      role: interview.role,
                      difficulty: interview.difficulty,
                      overallScore,
                      categoryScores: {
                        technical: 0,
                        communication: 0,
                        confidence: 0,
                        problemSolving: 0,
                        bodyLanguage: 0,
                      },
                      qaHistory: [],
                      bodyLanguageSummary: {
                        averageEyeContact: 0,
                        averagePosture: 0,
                        averageGestures: 0,
                        averageAttention: 0,
                        presencePercentage: 0,
                        feedback: [],
                      },
                      aiSummary: {
                        overallFeedback,
                        strengths: [],
                        improvements: [],
                        recommendations: [],
                        candidateLevel,
                      },
                      createdAt: interview.date,
                      durationMinutes: interview.durationMinutes,
                    }}
                  />
                );
              })}
          </div>
        )}
      </main>
    </div>
  );
}

export default function ReportsPage() {
  return (
    <ProtectedRoute>
      <ReportsContent />
    </ProtectedRoute>
  );
}