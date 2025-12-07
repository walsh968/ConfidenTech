import React, {createContext, useContext, useState, useEffect, ReactNode, useCallback} from "react";
import { User, getUserProfile, logoutUser } from "../services/api";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (
    email: string,
    password: string
  ) => Promise<{ success: boolean; error?: string; user?: User }>;
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
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const isAuthenticated = !!user;

  const checkAuth = useCallback(async () => {
    console.log("[Auth] checkAuth start");
    setIsLoading(true);
    try {
      const response: any = await getUserProfile();
      console.log("[Auth] profile response:", response);

      if (response.success && response.data) {
        const userData = response.data.user ?? response.data;
        setUser(userData as User);
      } else {
        setUser(null);
      }
    } catch (e) {
      console.warn("[Auth] checkAuth error:", e);
      setUser(null);
    } finally {
      console.log("[Auth] checkAuth finished, setIsLoading(false)");
      setIsLoading(false);
    }
  }, []);

  const login = async (
    email: string,
    password: string
  ): Promise<{ success: boolean; error?: string; user?: User }> => {
    const { loginUser } = await import("../services/api");
    const response = await loginUser({ email, password });

    if (response.success && response.data) {
      const loggedInUser = response.data.user;
      setUser(loggedInUser);
      return { success: true, user: loggedInUser };
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
    const currentUser = user; 
    try {
      await logoutUser();
    } catch (e) {
      console.error("Logout error:", e);
    }

    setUser(null);
  };

  useEffect(() => {

    checkAuth();
  }, [checkAuth]);

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated, login, logout, checkAuth }}
    >
      {children}
    </AuthContext.Provider>
  );
};
