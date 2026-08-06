"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useCallback,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import {
  getCurrentUser,
  loginUser,
  logoutSession,
  refreshSession,
  registerUser,
} from "@/lib/api";

const STORAGE_KEY = "project-ascension-session";

type User = {
  id: string;
  email: string;
  username: string;
  is_verified: boolean;
};

type Organization = {
  id: string;
  name: string;
  slug: string;
  owner_id: string;
  role: string;
};

type SessionState = {
  accessToken: string;
  refreshToken: string;
  organizationId: string | null;
  user: User | null;
  organization: Organization | null;
};

type AuthContextValue = {
  session: SessionState | null;
  status: "loading" | "authenticated" | "unauthenticated";
  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    username?: string,
  ) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function loadSession(): SessionState | null {
  if (typeof window === "undefined") {
    return null;
  }

  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as SessionState;
  } catch {
    return null;
  }
}

function persistSession(session: SessionState | null) {
  if (typeof window === "undefined") {
    return;
  }

  if (!session) {
    window.localStorage.removeItem(STORAGE_KEY);
    return;
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [session, setSession] = useState<SessionState | null>(null);
  const [status, setStatus] = useState<AuthContextValue["status"]>("loading");

  useEffect(() => {
    const existing = loadSession();
    if (existing) {
      setSession(existing);
      setStatus("authenticated");
    } else {
      setStatus("unauthenticated");
    }
  }, []);

  useEffect(() => {
    persistSession(session);
  }, [session]);

  const refresh = useCallback(async () => {
    if (!session?.refreshToken) {
      setSession(null);
      setStatus("unauthenticated");
      return;
    }

    try {
      const result = await refreshSession({
        refresh_token: session.refreshToken,
      });
      setSession((current) =>
        current
          ? {
              ...current,
              accessToken: result.access_token,
              refreshToken: result.refresh_token,
            }
          : null,
      );
      setStatus("authenticated");
    } catch {
      setSession(null);
      setStatus("unauthenticated");
      router.replace("/login");
    }
  }, [router, session?.refreshToken]);

  const hydrateProfile = useCallback(
    async (nextSession: SessionState | null) => {
      if (!nextSession?.accessToken) {
        return;
      }

      try {
        const user = await getCurrentUser(nextSession.accessToken);
        setSession((current) =>
          current
            ? {
                ...current,
                user,
              }
            : null,
        );
      } catch (error) {
        if (error instanceof Error && error.message === "token_expired") {
          await refresh();
          return;
        }

        setSession(null);
        setStatus("unauthenticated");
      }
    },
    [refresh],
  );

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }

    void hydrateProfile(session);
  }, [hydrateProfile, session]);

  const login = useCallback(
    async (email: string, password: string) => {
      const result = await loginUser({ email, password });
      const nextSession: SessionState = {
        accessToken: result.access_token,
        refreshToken: result.refresh_token,
        organizationId: null,
        user: result.user,
        organization: null,
      };

      setSession(nextSession);
      setStatus("authenticated");
      router.replace("/dashboard");
    },
    [router],
  );

  const register = useCallback(
    async (email: string, password: string, username?: string) => {
      const result = await registerUser({
        email,
        password,
        username: username ?? email.split("@", 1)[0] ?? "user",
      });
      const nextSession: SessionState = {
        accessToken: result.access_token,
        refreshToken: result.refresh_token,
        organizationId: result.organization_id,
        user: result.user,
        organization: null,
      };

      setSession(nextSession);
      setStatus("authenticated");
      router.replace("/dashboard");
    },
    [router],
  );

  const logout = useCallback(async () => {
    if (session?.refreshToken) {
      try {
        await logoutSession({ refresh_token: session.refreshToken });
      } catch {
        // ignore logout errors and clear local state
      }
    }

    setSession(null);
    setStatus("unauthenticated");
    router.replace("/login");
  }, [router, session?.refreshToken]);

  const value = useMemo<AuthContextValue>(
    () => ({
      session,
      status,
      login,
      register,
      logout,
      refresh,
    }),
    [login, logout, refresh, register, session, status],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
