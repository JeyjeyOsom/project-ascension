"use client";

import { useState, type FormEvent } from "react";

type AuthFormProps = {
  title: string;
  subtitle: string;
  submitLabel: string;
  onSubmit: (values: {
    email: string;
    password: string;
    username?: string;
  }) => Promise<void>;
  showUsername?: boolean;
};

export function AuthForm({
  title,
  subtitle,
  submitLabel,
  onSubmit,
  showUsername = false,
}: AuthFormProps) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      await onSubmit({
        email,
        password,
        username: showUsername ? username : undefined,
      });
      setMessage("Success");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
        <p className="mt-1 text-sm text-slate-600">{subtitle}</p>
      </div>

      {showUsername ? (
        <label className="block text-sm font-medium text-slate-700">
          Username
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 outline-none ring-0"
            placeholder="Your name"
          />
        </label>
      ) : null}

      <label className="block text-sm font-medium text-slate-700">
        Email
        <input
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 outline-none ring-0"
          placeholder="you@example.com"
        />
      </label>

      <label className="block text-sm font-medium text-slate-700">
        Password
        <input
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          className="mt-1 w-full rounded-2xl border border-slate-200 px-3 py-2 outline-none ring-0"
          placeholder="••••••••"
        />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="w-full rounded-2xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? "Working..." : submitLabel}
      </button>

      {message ? <p className="text-sm text-slate-600">{message}</p> : null}
    </form>
  );
}
