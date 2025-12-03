import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User, getUserProfile, logoutUser } from "../services/api";

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
  if (!context) throw new Error("useAuth must be used within an AuthProvider");
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // 🔥 NEW: First ping the backend health route
  const checkBackendAvailable = async () => {
    try {
      const res = await fetch(
        "https://confidentech.onrender.com/api/users/health/",
        { method: "GET" }
      );
      return res.ok;
    } catch {
      return false;
    }
  };

  // 🔥 FIX: Only check /profile/ if backend is reachable AND cookies exist
  const checkAuth = async () => {
    setIsLoading(true);

    const backendOk = await checkBackendAvailable();
    if (!backendOk) {
      console.warn("Backend unreachable — skipping profile check");
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Don't call /profile/ unless cookies exist
    const hasSessionCookie = document.cookie.includes("sessionid=");
    if (!hasSessionCookie) {
      console.log("No session cookie — user is logged out");
      setUser(null);
      setIsLoading(false);
      return;
    }

    // Now safe to call /profile/
    const response = await getUserProfile();

    if (response.success && response.data) {
      setUser(response.data.user);
    } else {
      setUser(null);
    }

    setIsLoading(false);
  };

  const login = async (email: string, password: string) => {
    const { loginUser } = await import("../services/api");
    const response = await loginUser({ email, password });

    if (response.success && response.data) {
      setUser(response.data.user);
      return { success: true };
    }

    return {
      success: false,
      error:
        response.errors?.non_field_errors?.[0] ||
        response.errors?.email?.[0] ||
        response.errors?.password?.[0] ||
        "Login failed",
    };
  };

  const logout = async () => {
    try {
      await logoutUser();
    } catch (e) {
      console.error("Logout error:", e);
    }
    setUser(null);
  };

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated, login, logout, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
};
