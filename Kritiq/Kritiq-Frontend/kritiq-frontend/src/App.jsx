import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";

import Dashboard from "./pages/Dashboard";
import RepositoryConnect from "./pages/RepositoryConnect";
import CodeReview from "./pages/CodeReview";
import CodeTranslation from "./pages/CodeTranslation";
import History from "./pages/History";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Register from "./pages/Register";

import DashboardLayout from "./layouts/DashboardLayout";
import AuthLayout from "./layouts/AuthLayout";

import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing Page */}
        <Route path="/" element={<Home />} />

        {/* Public Routes */}
        <Route element={<AuthLayout />}>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/repository" element={<RepositoryConnect />} />
            <Route path="/review" element={<CodeReview />} />
            <Route path="/translation" element={<CodeTranslation />} />
            <Route path="/history" element={<History />} />
            <Route path="/settings" element={<Settings />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;