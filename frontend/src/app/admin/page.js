"use client";

import { useState } from "react";

export default function TriggerRankPage() {
  const [examCode, setExamCode] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const triggerRankCalculation = async () => {
    if (!examCode) {
      setMessage("Please enter an exam code.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/calculate-results?exam_code=${examCode}`, {
        method: "POST",
      });

      const data = await response.json();

      if (response.ok) {
        setMessage("✅ Task triggered successfully!");
      } else {
        setMessage(`❌ Error: ${data.detail || "Something went wrong"}`);
      }
    } catch (error) {
      setMessage("❌ Failed to trigger the task.");
    }

    setLoading(false);
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white p-6 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-xl font-bold mb-4 text-center">Trigger Rank Calculation</h1>
        <input
          type="text"
          className="w-full p-3 border rounded-lg mb-4"
          placeholder="Enter Exam Code"
          value={examCode}
          onChange={(e) => setExamCode(e.target.value)}
        />
        <button
          onClick={triggerRankCalculation}
          className="w-full p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          disabled={loading}
        >
          {loading ? "Triggering..." : "Trigger Task"}
        </button>
        {message && <p className="mt-4 text-center font-semibold">{message}</p>}
      </div>
    </div>
  );
}