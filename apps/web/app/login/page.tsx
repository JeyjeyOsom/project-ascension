"use client";

import { useState } from "react";
import { AuthForm } from "@/components/auth-form";
import { useAuth } from "@/components/providers/auth-provider";

export default function LoginPage() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(values: { email: string; password: string }) {
    try {
      await login(values.email, values.password);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Unable to sign in");
      throw cause;
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-md">
        <AuthForm
          title="Sign in"
          subtitle="Use your email and password to continue."
          submitLabel="Login"
          onSubmit={handleLogin}
        />
        {error ? <p className="mt-4 text-sm text-red-600">{error}</p> : null}
      </div>
    </main>
  );
}
