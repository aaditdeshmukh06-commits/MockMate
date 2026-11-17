'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useApp } from '@/lib/store';
import { ProtectedRoute } from '@/lib/auth-guard';
import { InterviewHistoryItem } from '@/lib/types';
import type { RetryAction } from '@/lib/api';

interface MetricCardProps {
  icon: string;
  label: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative';
}

function MetricCard({ icon, label, value, change, changeType = 'positive' }: MetricCardProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center gap-3 mb-2">
        <span className="text-2xl">{icon}</span>
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</h3>
      </div>
      <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
      {change && (
        <p className={`text-sm mt-1 ${changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
          {change}
        </p>
      )}
    </div>
  );
}

interface HistoryItemProps {
  interview: InterviewHistoryItem;
}

function HistoryItem({ interview }: HistoryItemProps) {
  const isCompleted = interview.status === 'completed';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-sm border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
            <span className="text-xl">🎤</span>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 dark:text-white">{interview.role}</h4>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              {interview.difficulty} • {interview.durationMinutes} min • {new Date(interview.date).toLocaleDateString()}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className={`text-2xl font-bold ${isCompleted ? 'text-green-600' : 'text-gray-400'}`}>
            {interview.overallScore === '--' ? '--' : `${interview.overallScore}%`}
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400 capitalize">{interview.status.replace('_', ' ')}</p>
        </div>
      </div>
    </div>
  );
}

function DashboardContent() {
  const { state, loadHistory, logout, retryLastAction, clearRetry } = useApp();

  useEffect(() => {
    if (state.user?.id) {
      loadHistory();
    }
  }, [state.user?.id, loadHistory]);

  const stats = [
    { icon: '🎤', label: 'Interviews Conducted', value: state.interviewHistory.filter(i => i.status === 'completed').length.toString(), change: '+2 this week' },
    { icon: '⭐', label: 'Average Score', value: state.interviewHistory.length > 0
      ? `${Math.round(state.interviewHistory.filter(i => i.status === 'completed').reduce((sum, i) => sum + (typeof i.overallScore === 'number' ? i.overallScore : 0), 0) / Math.max(1, state.interviewHistory.filter(i => i.status === 'completed').length))}%`
      : '--', change: '+5%' },
    { icon: '💬', label: 'Confidence', value: '91%', change: '+3%' },
    { icon: '🎯', label: 'Candidate Level', value: 'Intermediate', change: 'Improving' },
  ];

  const recentInterviews = state.interviewHistory.slice(0, 5);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-8">
              <Link href="/dashboard" className="text-2xl font-bold text-blue-600 dark:text-blue-400">🎤 MockMate</Link>
              <nav className="hidden md:flex items-center gap-6">
                <Link href="/dashboard" className="text-sm font-medium text-gray-900 dark:text-white hover:text-blue-600">Dashboard</Link>
                <Link href="/interview" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Interview</Link>
                <Link href="/reports" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Reports</Link>
                <Link href="/settings" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Settings</Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
                Welcome, {state.user?.name || 'User'}!
              </span>
              <button
                onClick={logout}
                className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Section */}
        <section className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Welcome back, {state.user?.name || 'User'}!</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">AI Powered Mock Interview Platform</p>
        </section>

        {/* Stats Grid */}
        <section className="mb-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat, index) => (
              <MetricCard key={index} {...stat} />
            ))}
          </div>
        </section>

        {/* Quick Actions */}
        <section className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link
              href="/interview"
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-2xl">🎤</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Start Interview</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Begin a new mock interview session</p>
                </div>
              </div>
            </Link>
            <Link
              href="/reports"
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-2xl">📄</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">View Reports</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Review your interview performance</p>
                </div>
              </div>
            </Link>
            <Link
              href="/settings"
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-700 transition-colors group"
            >
              <div className="flex items-center gap-4">
                <div className="w-14 h-14 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform">
                  <span className="text-2xl">⚙</span>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 dark:text-white">Settings</h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Configure your preferences</p>
                </div>
              </div>
            </Link>
          </div>
        </section>

        {/* Interview History */}
        <section>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Interview History</h2>
            <Link
              href="/reports"
              className="text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              View All →
            </Link>
          </div>

          {/* Retry banner for loadHistory failures */}
          {state.error && state.retryAction?.type === 'loadHistory' && (
            <div className="mb-4 p-4 bg-yellow-50 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-800 rounded-lg">
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

          {state.interviewHistory.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-xl p-12 text-center border border-gray-100 dark:border-gray-700">
              <span className="text-4xl mb-4 block">🎤</span>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No interviews yet</h3>
              <p className="text-gray-500 dark:text-gray-400 mb-6">Start your first mock interview to see your history here</p>
              <Link
                href="/interview"
                className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
              >
                Start Interview
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {recentInterviews.map((interview) => (
                <HistoryItem key={interview.sessionId} interview={interview} />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default function DashboardPage() {
  return (
    <ProtectedRoute>
      <DashboardContent />
    </ProtectedRoute>
  );
}