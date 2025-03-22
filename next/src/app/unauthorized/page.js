export default function UnauthorizedPage() {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h1 className="text-3xl font-bold text-red-500">Unauthorized</h1>
          <p className="mt-2 text-gray-600">You are not registered for this examination</p>
          <a href="/login" className="mt-4 inline-block bg-blue-500 text-white px-4 py-2 rounded">
            Go to Login
          </a>
        </div>
      </div>
    );
  }