"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/providers/auth-provider";

export default function Home() {
  const router = useRouter();
  const { status } = useAuth();

  useEffect(() => {
    if (status === "authenticated") {
      router.replace("/dashboard");
      return;
    }

    if (status === "unauthenticated") {
      router.replace("/login");
    }
  }, [router, status]);

  return (
    <main className="min-h-screen bg-slate-50 p-8 text-slate-700">
      Redirecting...
    </main>
  );
}
