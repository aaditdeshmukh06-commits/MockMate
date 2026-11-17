'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useApp } from '@/lib/store';

export default function HomePage() {
  const router = useRouter();
  const { state } = useApp();

  useEffect(() => {
    // Wait for hydration and user state to be loaded
    if (state.user) {
      router.push('/dashboard');
    } else {
      router.push('/sign-in');
    }
  }, [state.user, router]);

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