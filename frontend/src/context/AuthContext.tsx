import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import api from "../api/client";

interface UserInfo {
  id: string;
  full_name: string;
  email: string;
  role: string;
  free_uses_remaining: number;
}

interface AuthContextValue {
  user: UserInfo | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (fullName: string, email: string, password: string, phone?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    const token = localStorage.getItem("spa_access_token");
    if (!token) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get("/api/auth/me");
      setUser(data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const storeTokens = (accessToken: string, refreshToken: string) => {
    localStorage.setItem("spa_access_token", accessToken);
    localStorage.setItem("spa_refresh_token", refreshToken);
  };

  const login = async (email: string, password: string) => {
    const { data } = await api.post("/api/auth/login", { email, password });
    storeTokens(data.access_token, data.refresh_token);
    await refreshUser();
  };

  const register = async (fullName: string, email: string, password: string, phone?: string) => {
    const { data } = await api.post("/api/auth/register", {
      full_name: fullName,
      email,
      password,
      phone,
    });
    storeTokens(data.access_token, data.refresh_token);
    await refreshUser();
  };

  const logout = () => {
    localStorage.removeItem("spa_access_token");
    localStorage.removeItem("spa_refresh_token");
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
