"use client";

export default function ExamCompletionPage() {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
        <div className="bg-white shadow-lg rounded-2xl p-8 text-center max-w-md w-full">
          <h1 className="text-3xl font-bold text-green-600">Exam Submitted!</h1>
          <p className="mt-4 text-gray-600">Thank you for completing the exam. Your responses have been successfully recorded.</p>
          <div className="mt-6">
            <p className="text-lg font-semibold text-gray-800">Best of luck with your results!</p>
          </div>
          <button
            className="mt-6 px-6 py-3 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 transition"
            onClick={() => window.location.href = '/login'}
          >
            Go to Login
          </button>
        </div>
      </div>
    );
  }
  