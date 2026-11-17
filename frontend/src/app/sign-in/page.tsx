'use client';

import { useEffect, useState, Suspense } from 'react';
import { useRouter } from 'next/navigation';
import { Authenticator, useAuthenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import { getCurrentUser } from '@/lib/amplify-config';
import { useApp } from '@/lib/store';

function SignInContent() {
  const router = useRouter();
  const { user } = useAuthenticator();
  const { state, dispatch } = useApp();
  const [isLoading, setIsLoading] = useState(true);

  // Sync Amplify user with our app state
  useEffect(() => {
    const syncUser = async () => {
      if (user) {
        const appUser = await getCurrentUser();
        if (appUser) {
          dispatch({ type: 'SET_USER', payload: appUser });
        }
        setIsLoading(false);
      } else if (state.user) {
        // User signed out in Amplify but still in our state
        dispatch({ type: 'SET_USER', payload: null });
        setIsLoading(false);
      } else {
        setIsLoading(false);
      }
    };
    syncUser();
  }, [user, state.user, dispatch]);

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!isLoading && state.user) {
      router.push('/dashboard');
    }
  }, [isLoading, state.user, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="text-4xl mb-4">🎤</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MockMate</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Loading...</p>
        </div>
      </div>
    );
  }

  // If already authenticated, show loading/redirect
  if (state.user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">Redirecting to dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-700 overflow-hidden min-w-0">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🎤 MockMate</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">Practice. Improve. Get Hired.</p>
          </div>

          <div className="w-full max-w-[420px] mx-auto min-w-0">
            <style jsx>{`
              [data-amplify-authenticator] {
                width: 100%;
                max-width: 420px;
                box-sizing: border-box;
              }
              .amplify-tabs {
                width: 100%;
                box-sizing: border-box;
              }
              .amplify-form-section {
                width: 100%;
                box-sizing: border-box;
              }
              .amplify-form-fields {
                width: 100%;
                box-sizing: border-box;
              }
              .amplify-button {
                width: 100%;
                box-sizing: border-box;
              }
              .amplify-form-field {
                width: 100%;
                box-sizing: border-box;
              }
              .amplify-input {
                width: 100%;
                box-sizing: border-box;
              }
            `}</style>
            <Authenticator>
              {() => (
                <>
                  <div className="mt-4 text-center text-xs text-gray-500 dark:text-gray-400">
                    At least 8 characters, with an uppercase letter, a lowercase letter, a number and a special character.
                  </div>
                  <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
                    By signing in, you agree to our Terms of Service and Privacy Policy
                  </div>
                </>
              )}
            </Authenticator>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SignInPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="text-4xl mb-4">🎤</div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">MockMate</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2">Loading...</p>
        </div>
      </div>
    }>
      <SignInContent />
    </Suspense>
  );
}