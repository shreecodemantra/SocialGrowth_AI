import React, { createContext, useContext, useEffect, useState } from "react";

import { fetchCurrentUser, login as loginRequest, registerUser } from "../api/auth";
import { tokenStorage } from "../api/client";
import type { User } from "../types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadUser = async () => {
    if (!tokenStorage.getAccessToken()) {
      setIsLoading(false);
      return;
    }
    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
    } catch {
      tokenStorage.clear();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadUser();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (email: string, password: string) => {
    const tokens = await loginRequest(email, password);
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    const currentUser = await fetchCurrentUser();
    setUser(currentUser);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    await registerUser(email, password, fullName);
    await login(email, password);
  };

  const logout = () => {
    tokenStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: !!user, login, register, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
