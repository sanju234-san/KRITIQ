import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Pipeline from "./pages/Pipeline";
import Report from "./pages/Report";
import Login from "./pages/Login";
import Playground from "./pages/Playground";
import Navbar from "./components/Navbar";
import { useAuthStore } from "./store/authStore";
import { useAuth } from "./hooks/useAuth";
import { Loader2 } from "lucide-react";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  const { loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-1 items-center justify-center bg-zinc-950 min-h-[calc(100vh-4rem)]">
        <Loader2 className="h-8 w-8 text-purple-500 animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      {isAuthenticated && <Navbar />}
      <main className="flex-1">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/playground" element={<Playground />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/pipeline/:reportId"
            element={
              <ProtectedRoute>
                <Pipeline />
              </ProtectedRoute>
            }
          />
          <Route
            path="/report/:reportId"
            element={
              <ProtectedRoute>
                <Report />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
    </div>
  );
}
