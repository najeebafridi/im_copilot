import { createContext, useEffect, useState, type PropsWithChildren, useContext } from "react";

import {
  clear,
  getToken,
  getTokenStorageMode,
  removeToken,
  saveToken,
  saveUser,
} from "@/services/storage/localStorage";
import { LoadingScreen } from "@/components/common/LoadingScreen";
import { type AuthContextValue, type AuthLoginRequest, type AuthSession, type UserProfile } from "@/types";
import { getCurrentUser, login as loginRequest, logout as logoutRequest } from "@/services/api/authService";

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: PropsWithChildren) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  async function restoreSession(): Promise<void> {
    const token = getToken();

    if (!token) {
      setIsAuthenticated(false);
      setUser(null);
      setLoading(false);
      return;
    }

    try {
      const verifiedUser = await getCurrentUser(token);
      const storageMode = getTokenStorageMode() ?? "localStorage";
      saveToken(token, storageMode);
      saveUser(verifiedUser, storageMode);
      setIsAuthenticated(true);
      setUser(verifiedUser);
    } catch {
      clear();
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void restoreSession();
  }, []);

  async function login(request: AuthLoginRequest): Promise<UserProfile> {
    const session: AuthSession = await loginRequest(request);

    if (session.user.role !== request.mode) {
      clear();
      setIsAuthenticated(false);
      setUser(null);
      throw new Error("You do not have access to this login area.");
    }

    const storageMode = request.rememberMe ? "localStorage" : "sessionStorage";
    clear();
    saveToken(session.token, storageMode);
    saveUser(session.user, storageMode);
    setIsAuthenticated(true);
    setUser(session.user);
    return session.user;
  }

  async function logout(): Promise<void> {
    await logoutRequest();
    clear();
    removeToken();
    setIsAuthenticated(false);
    setUser(null);
  }

  const value: AuthContextValue = {
    isAuthenticated,
    user,
    loading,
    login,
    restoreSession,
    logout,
  };

  if (loading) {
    return <LoadingScreen />;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return context;
}
