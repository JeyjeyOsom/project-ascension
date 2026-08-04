"use client";

import { useCallback, useEffect, useState } from "react";
import { AuthForm } from "@/components/auth-form";
import { StatusBanner } from "@/components/status-banner";
import {
  getCurrentUser,
  getOrganization,
  loginUser,
  logoutSession,
  registerUser,
} from "@/lib/api";

const STORAGE_KEY = "project-ascension-session";

type SessionState = {
  accessToken: string;
  refreshToken: string;
  organizationId: string | null;
  user: {
    id: string;
    email: string;
    username: string;
    is_verified: boolean;
  } | null;
  organization: {
    id: string;
    name: string;
    slug: string;
    owner_id: string;
    role: string;
  } | null;
};

function loadSession() {
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

export default function Home() {
  const [session, setSession] = useState<SessionState | null>(null);
  const [status, setStatus] = useState<{
    kind: "success" | "error" | "info";
    title: string;
    message?: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const existing = loadSession();
    if (existing) {
      setSession(existing);
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }

    if (!session) {
      window.localStorage.removeItem(STORAGE_KEY);
      return;
    }

    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }, [session]);

  const loadProfile = useCallback(async () => {
    if (!session?.accessToken) {
      return;
    }

    try {
      const user = await getCurrentUser(session.accessToken);
      const organization = session.organizationId
        ? await getOrganization(session.accessToken, session.organizationId)
        : null;

      setSession((current) =>
        current
          ? {
              ...current,
              user,
              organization,
            }
          : null,
      );
      setStatus({
        kind: "info",
        title: "Profile loaded",
        message: "Your account details are ready.",
      });
    } catch (error) {
      setStatus({
        kind: "error",
        title: "Profile unavailable",
        message:
          error instanceof Error ? error.message : "Unable to load profile",
      });
    }
  }, [session?.accessToken, session?.organizationId]);

  useEffect(() => {
    if (!session?.accessToken) {
      return;
    }

    void loadProfile();
  }, [loadProfile, session?.accessToken]);

  async function handleLogin(values: { email: string; password: string }) {
    const result = await loginUser({
      email: values.email,
      password: values.password,
    });
    const nextSession = {
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      organizationId: null,
      user: result.user,
      organization: null,
    };

    setSession(nextSession);
    setStatus({
      kind: "success",
      title: "Signed in",
      message: `Welcome back, ${result.user.username}.`,
    });
  }

  async function handleRegister(values: {
    email: string;
    password: string;
    username?: string;
  }) {
    const fallbackUsername = values.email.split("@", 1)[0] ?? "user";
    const result = await registerUser({
      email: values.email,
      password: values.password,
      username: values.username ?? fallbackUsername,
    });

    const nextSession = {
      accessToken: result.access_token,
      refreshToken: result.refresh_token,
      organizationId: result.organization_id,
      user: result.user,
      organization: null,
    };

    setSession(nextSession);
    setStatus({
      kind: "success",
      title: "Account created",
      message: "Your organization has also been prepared.",
    });
  }

  async function handleLogout() {
    if (!session?.refreshToken) {
      setSession(null);
      setStatus({ kind: "info", title: "Signed out" });
      return;
    }

    try {
      await logoutSession({ refresh_token: session.refreshToken });
    } finally {
      setSession(null);
      setStatus({ kind: "info", title: "Signed out" });
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-slate-50 p-8 text-slate-700">
        Loading...
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(148,163,184,0.12),_transparent_35%)] bg-slate-50 p-6 text-slate-800 md:p-10">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="rounded-3xl border border-slate-200 bg-white/80 px-6 py-5 shadow-sm backdrop-blur">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-sm font-medium uppercase tracking-[0.25em] text-slate-500">
                Project Ascension
              </p>
              <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">
                Modern auth workspace
              </h1>
            </div>
            <div className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
              {session?.user
                ? `Signed in as ${session.user.username}`
                : "Ready for sign in"}
            </div>
          </div>
        </header>

        {status ? (
          <StatusBanner kind={status.kind} title={status.title}>
            {status.message}
          </StatusBanner>
        ) : null}

        {!session?.user ? (
          <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
                Overview
              </p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-900">
                A calm, modular entrypoint for your API.
              </h2>
              <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
                This experience surfaces the current authentication flows with a
                minimal layout and clear state handling.
              </p>
              <ul className="mt-6 space-y-3 text-sm text-slate-600">
                <li>
                  • Register and sign in with the existing backend endpoints.
                </li>
                <li>
                  • View your profile and organization after authentication.
                </li>
                <li>
                  • Keep session data in local storage for a simple
                  single-device experience.
                </li>
              </ul>
            </div>
            <div className="space-y-6">
              <AuthForm
                title="Create account"
                subtitle="Register a new identity and organization."
                submitLabel="Register"
                showUsername
                onSubmit={handleRegister}
              />
              <AuthForm
                title="Sign in"
                subtitle="Use your existing credentials to continue."
                submitLabel="Login"
                onSubmit={handleLogin}
              />
            </div>
          </section>
        ) : (
          <section className="grid gap-6 lg:grid-cols-[1fr_0.75fr]">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
                    Account
                  </p>
                  <h2 className="mt-1 text-2xl font-semibold text-slate-900">
                    Welcome back
                  </h2>
                </div>
                <button
                  onClick={() => void handleLogout()}
                  className="rounded-full border border-slate-200 px-3 py-2 text-sm text-slate-700 transition hover:bg-slate-50"
                >
                  Sign out
                </button>
              </div>

              <div className="mt-6 grid gap-4 md:grid-cols-2">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-medium text-slate-500">User</p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">
                    {session.user?.username}
                  </p>
                  <p className="text-sm text-slate-600">
                    {session.user?.email}
                  </p>
                </div>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                  <p className="text-sm font-medium text-slate-500">
                    Organization
                  </p>
                  <p className="mt-2 text-lg font-semibold text-slate-900">
                    {session.organization?.name ?? "Pending"}
                  </p>
                  <p className="text-sm text-slate-600">
                    {session.organization?.slug ?? "Load organization details"}
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-500">
                Session actions
              </p>
              <div className="mt-4 space-y-3 text-sm text-slate-600">
                <button
                  onClick={() => void loadProfile()}
                  className="w-full rounded-2xl border border-slate-200 px-3 py-3 text-left transition hover:bg-slate-50"
                >
                  Reload profile and organization
                </button>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-3">
                  <p className="font-medium text-slate-700">Access token</p>
                  <p className="mt-1 break-all text-xs text-slate-500">
                    {session.accessToken.slice(0, 24)}...
                  </p>
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}
