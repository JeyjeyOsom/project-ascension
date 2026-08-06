"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/auth-provider";

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { status, session } = useAuth();

  useEffect(() => {
    if (status === "unauthenticated" && !session?.accessToken) {
      router.replace("/login");
    }
  }, [router, session?.accessToken, status]);

  if (status === "loading") {
    return (
      <main className="min-h-screen bg-slate-50 p-6 text-slate-700">
        Loading session…
      </main>
    );
  }

  if (status === "unauthenticated" && !session?.accessToken) {
    return null;
  }

  return <>{children}</>;
}
