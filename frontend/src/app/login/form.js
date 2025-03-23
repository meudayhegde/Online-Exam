"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginForm() {
  const [roll_number, setRollNumber] = useState("");
  const [uic, setUIC] = useState("");
  const [error, setError] = useState(null);
  
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ roll_number: roll_number, uic: uic }),
    });

    if (res.ok) {
        const data = await res.json();
        Object.keys(data).forEach(key => localStorage.setItem(key, data[key]))
        router.push("/exam"); // Redirect on successful login

    } else {
      router.push("/unauthorized");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <p className="text-red-500">{error}</p>}
      
      <input
        type="text"
        placeholder="Roll Number"
        value={roll_number}
        onChange={(e) => setRollNumber(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <input
        placeholder="PassUnique Identification Code"
        value={uic}
        onChange={(e) => setUIC(e.target.value)}
        className="w-full p-2 border rounded"
        required
      />

      <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
        Login
      </button>
    </form>
  );
}