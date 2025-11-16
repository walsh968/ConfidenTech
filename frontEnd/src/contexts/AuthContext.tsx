import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, getUserProfile, logoutUser } from '../services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  // Try to restore user from localStorage on initial load
  const getStoredUser = (): User | null => {
    try {
      const stored = localStorage.getItem('confidenTech_user');
      if (stored) {
        const parsed = JSON.parse(stored);
        console.log('Restored user from localStorage:', parsed?.email);
        return parsed;
      }
    } catch (error) {
      console.error('Error reading user from localStorage:', error);
    }
    return null;
  };

  // Initialize user from localStorage immediately
  const initialUser = getStoredUser();
  const [user, setUser] = useState<User | null>(initialUser);
  const [isLoading, setIsLoading] = useState(true);
  
  console.log('AuthProvider initialized with user:', initialUser?.email || 'none');

  const isAuthenticated = !!user;

  // Store user in localStorage whenever it changes
  React.useEffect(() => {
    if (user) {
      try {
        localStorage.setItem('confidenTech_user', JSON.stringify(user));
      } catch (error) {
        console.error('Error storing user in localStorage:', error);
      }
    } else {
      // Clear localStorage when user logs out
      try {
        localStorage.removeItem('confidenTech_user');
      } catch (error) {
        console.error('Error clearing user from localStorage:', error);
      }
    }
  }, [user]);

  // Check if user is authenticated on app load
  const checkAuth = async () => {
    // Always preserve existing user state - only clear on explicit 401/403
    const currentUser = user || getStoredUser();
    
    try {
      setIsLoading(true);
      const response = await getUserProfile();
      const status = (response as any).status;
      
      console.log('checkAuth response:', { success: response.success, status, hasData: !!response.data, error: response.error, currentUser: !!currentUser });
      
      if (response.success && response.data) {
        // Update user with fresh data from backend
        // Backend might return { user: ... } or just the user object directly
        const userData = response.data.user || response.data;
        if (userData && (userData.email || userData.id)) {
          setUser(userData);
        } else {
          // Invalid user data - preserve existing user
          console.log('Invalid user data from backend, preserving existing user');
          if (currentUser) {
            setUser(currentUser);
          }
        }
      } else {
        // ONLY clear user if it's an explicit authentication error (401/403)
        // For ALL other cases, preserve the user from localStorage/state
        if (status === 401 || status === 403) {
          // Authentication failed - user is not logged in
          console.log('Authentication failed (401/403), clearing user');
          setUser(null);
        } else {
          // Any other error (network, server, 404, etc.) - preserve session
          console.log('Auth check failed but preserving session. Status:', status, 'Error:', response.error);
          // Always preserve user - restore from localStorage if needed
          if (currentUser) {
            setUser(currentUser);
          } else {
            const storedUser = getStoredUser();
            if (storedUser) {
              setUser(storedUser);
            }
          }
        }
      }
    } catch (error) {
      // Network errors or other exceptions - ALWAYS preserve session
      console.error('Auth check failed (exception):', error);
      // Always restore from localStorage/current state on any error
      if (currentUser) {
        console.log('Preserving current user after error');
        setUser(currentUser);
      } else {
        const storedUser = getStoredUser();
        if (storedUser) {
          console.log('Restoring user from localStorage after error');
          setUser(storedUser);
        }
      }
      // NEVER set user to null on errors - always preserve existing session
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const { loginUser } = await import('../services/api');
      const response = await loginUser({ email, password });
      
      if (response.success && response.data) {
        setUser(response.data.user);
        return { success: true };
      } else {
        const errorMessage = response.errors?.email?.[0] || 
                           response.errors?.password?.[0] || 
                           response.errors?.non_field_errors?.[0] ||
                           'Login failed';
        return { success: false, error: errorMessage };
      }
    } catch (error) {
      return { 
        success: false, 
        error: error instanceof Error ? error.message : 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
