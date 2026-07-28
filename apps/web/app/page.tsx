"use client";

import { useEffect, useState } from "react";

type HealthResponse = {
  status: string;
  service: string;
  version: string;
};

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchHealth() {
      try {
        const response = await fetch("http://127.0.0.1:8000/health");
        const data = await response.json();
        setHealth(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    }

    fetchHealth();
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <main style={{ padding: "2rem" }}>
      <h1>Project Ascension</h1>

      {health ? (
        <>
          <p>Status: {health.status}</p>
          <p>Service: {health.service}</p>
          <p>Version: {health.version}</p>
        </>
      ) : (
        <p>Failed to connect to API.</p>
      )}
    </main>
  );
  
}