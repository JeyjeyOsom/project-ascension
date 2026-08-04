"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { AuthForm } from "@/components/auth-form";
import { loginUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  async function handleLogin(values: { email: string; password: string }) {
    try {
      const result = await loginUser({
        email: values.email,
        password: values.password,
      });
      window.localStorage.setItem(
        "project-ascension-session",
        JSON.stringify({
          accessToken: result.access_token,
          refreshToken: result.refresh_token,
          organizationId: null,
          user: result.user,
          organization: null,
        }),
      );
      router.replace("/");
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
