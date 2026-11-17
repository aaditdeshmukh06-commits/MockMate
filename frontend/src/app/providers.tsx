'use client';

import { ReactNode, useEffect, useRef } from 'react';
import { AppProvider } from '@/lib/store';
import { Authenticator } from '@aws-amplify/ui-react';
import { Amplify } from 'aws-amplify';
import { getCurrentUser, getAmplifyConfig } from '@/lib/amplify-config';
import { useApp } from '@/lib/store';

// Configure Amplify on client side
if (typeof window !== 'undefined') {
  Amplify.configure(getAmplifyConfig());
}

// Component to sync Amplify auth state with our app state
function AuthSync() {
  const { state, dispatch } = useApp();

  // Use ref to track latest state.user without adding to effect deps
  const stateUserRef = useRef(state.user);
  useEffect(() => {
    stateUserRef.current = state.user;
  }, [state.user]);

  useEffect(() => {
    let mounted = true;

    const checkAuth = async () => {
      try {
        const user = await getCurrentUser();
        if (mounted) {
          const currentUser = stateUserRef.current;
          if (user && !currentUser) {
            dispatch({ type: 'SET_USER', payload: user });
          } else if (!user && currentUser) {
            dispatch({ type: 'SET_USER', payload: null });
          }
        }
      } catch {
        // Ignore errors, user will be null
      }
    };

    checkAuth();

    return () => {
      mounted = false;
    };
  }, [dispatch]); // Only run once on mount

  return null;
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <AppProvider>
      <Authenticator.Provider>
        <AuthSync />
        {children}
      </Authenticator.Provider>
    </AppProvider>
  );
}