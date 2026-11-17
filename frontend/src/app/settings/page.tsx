'use client';

import { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import { useApp } from '@/lib/store';
import { ProtectedRoute } from '@/lib/auth-guard';
import type { UserPreferences } from '@/lib/types';

const DEFAULT_PREFERENCES: UserPreferences = {
  language: 'English',
  difficulty: 'medium',
  enableCamera: true,
  enableMicrophone: true,
  darkMode: false,
};

function SettingsContent() {
  const { state, dispatch, logout } = useApp();

  const [preferences, setPreferences] = useState<UserPreferences>(
    state.user?.preferences || DEFAULT_PREFERENCES
  );
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Reset preferences when user changes (e.g., after login)
  // Using key prop on the component would be better, but this works for now
  const prevUserId = useRef(state.user?.id);
  useEffect(() => {
    if (state.user?.id !== prevUserId.current) {
      prevUserId.current = state.user?.id;
      setPreferences(state.user?.preferences || DEFAULT_PREFERENCES);
    }
  }, [state.user?.id, state.user?.preferences]);

  const handleChange = (key: keyof UserPreferences, value: string | boolean) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    if (!state.user) return;

    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));

      dispatch({ type: 'UPDATE_PREFERENCES', payload: preferences });
      setMessage({ type: 'success', text: 'Settings saved successfully!' });
    } catch {
      setMessage({ type: 'error', text: 'Failed to save settings. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  if (!state.user) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

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
                <Link href="/reports" className="text-sm font-medium text-gray-500 dark:text-gray-400 hover:text-blue-600">Reports</Link>
                <Link href="/settings" className="text-sm font-medium text-gray-900 dark:text-white">Settings</Link>
              </nav>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm text-gray-700 dark:text-gray-300 hidden sm:block">
                Welcome, {state.user.name}!
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Settings</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">Manage your interview preferences and account settings</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-400 border border-green-200 dark:border-green-800' : 'bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-200 dark:border-red-800'}`}>
            {message.text}
          </div>
        )}

        <div className="space-y-6">
          {/* Interview Preferences */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Interview Preferences</h2>

            <div className="space-y-6">
              <div>
                <label htmlFor="language" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Interview Language
                </label>
                <select
                  id="language"
                  value={preferences.language}
                  onChange={(e) => handleChange('language', e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
                >
                  <option value="English">English</option>
                  <option value="Hindi">Hindi</option>
                  <option value="English + Hindi">English + Hindi</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Default Difficulty
                </label>
                <div className="flex gap-4">
                  {(['easy', 'medium', 'hard'] as const).map((diff) => (
                    <label key={diff} className="flex-1">
                      <input
                        type="radio"
                        name="difficulty"
                        value={diff}
                        checked={preferences.difficulty === diff}
                        onChange={(e) => handleChange('difficulty', e.target.value as 'easy' | 'medium' | 'hard')}
                        className="sr-only peer"
                      />
                      <div className={`p-4 rounded-lg border-2 text-center cursor-pointer transition-colors ${
                        preferences.difficulty === diff
                          ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                          : 'border-gray-200 dark:border-gray-600 hover:border-gray-300'
                      }`}>
                        <p className="font-medium capitalize text-gray-900 dark:text-white">{diff}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Enable Camera</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Use camera for body language analysis during interviews</p>
                </div>
                <button
                  onClick={() => handleChange('enableCamera', !preferences.enableCamera)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
                    preferences.enableCamera ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                  }`}
                  role="switch"
                  aria-checked={preferences.enableCamera}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      preferences.enableCamera ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">Enable Microphone</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">Use microphone for voice input (coming soon)</p>
                </div>
                <button
                  onClick={() => handleChange('enableMicrophone', !preferences.enableMicrophone)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
                    preferences.enableMicrophone ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                  }`}
                  role="switch"
                  aria-checked={preferences.enableMicrophone}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      preferences.enableMicrophone ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </div>
          </section>

          {/* Appearance */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Appearance</h2>

            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900 dark:text-white">Dark Mode</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Toggle dark/light theme (coming soon)</p>
              </div>
              <button
                onClick={() => handleChange('darkMode', !preferences.darkMode)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800 ${
                  preferences.darkMode ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-600'
                }`}
                role="switch"
                aria-checked={preferences.darkMode}
                disabled
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    preferences.darkMode ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </section>

          {/* Account */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-100 dark:border-gray-700">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Account</h2>

            <div className="space-y-4">
              <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center text-xl">
                  {state.user.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <p className="font-medium text-gray-900 dark:text-white">{state.user.name}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{state.user.email}</p>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">Sign out of your account</p>
                <button
                  onClick={logout}
                  className="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 bg-red-50 dark:bg-red-900/20 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </section>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={isSaving}
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold rounded-lg transition-colors focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
            >
              {isSaving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}

export default function SettingsPage() {
  return (
    <ProtectedRoute>
      <SettingsContent />
    </ProtectedRoute>
  );
}