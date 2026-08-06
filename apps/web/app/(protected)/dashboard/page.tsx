"use client";

import { useAuth } from "@/components/providers/auth-provider";

export default function DashboardPage() {
  const { session, logout } = useAuth();

  return (
    <main className="min-h-screen bg-slate-50 p-6 text-slate-800">
      <div className="mx-auto max-w-3xl rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <p className="text-sm font-medium uppercase tracking-[0.25em] text-slate-500">
          Protected area
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-slate-900">
          Welcome back, {session?.user?.username ?? "there"}
        </h1>
        <p className="mt-3 text-sm text-slate-600">
          This page is only reachable when the current user has an authenticated
          session.
        </p>
        <button
          onClick={() => void logout()}
          className="mt-6 rounded-2xl bg-slate-900 px-4 py-2 text-sm font-medium text-white"
        >
          Sign out
        </button>
      </div>
    </main>
  );
}
