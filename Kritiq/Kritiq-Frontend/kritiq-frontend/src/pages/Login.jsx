import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginUser, getProfile } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

import AuthLogo from "../components/auth/AuthLogo";
import AuthCard from "../components/auth/AuthCard";
import LoginForm from "../components/auth/LoginForm";

export default function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const loginResponse = await loginUser(form);

      const token = loginResponse.data.access_token;

      localStorage.setItem("token", token);

      const profileResponse = await getProfile();

      login(profileResponse.data, token);

      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center bg-[#0d0f12] px-4 overflow-hidden relative"
      style={{
        backgroundImage: `
          linear-gradient(to right, rgba(255,255,255,0.02) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255,255,255,0.02) 1px, transparent 1px)
        `,
        backgroundSize: "40px 40px",
      }}
    >
      {/* Background Glow */}
      <div
        className="absolute pointer-events-none"
        style={{
          width: 600,
          height: 600,
          background:
            "radial-gradient(circle, rgba(139,92,246,.05) 0%, rgba(13,15,18,0) 70%)",
        }}
      />

      <main className="relative z-10 w-full max-w-[440px] flex flex-col items-center pt-16">
        <AuthLogo />

        <div className="w-full mt-10">
          <AuthCard
            title="Welcome back"
            subtitle="Enter your cordentials to access your dashboard."
          >
            <LoginForm
              form={form}
              handleChange={handleChange}
              handleSubmit={handleSubmit}
              loading={loading}
              error={error}
            />
          </AuthCard>
        </div>

        <footer className="mt-8 flex flex-col items-center space-y-6">
          <nav className="flex items-center space-x-6">
            <button className="text-[10px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-300">
              Privacy
            </button>

            <div className="h-1 w-1 rounded-full bg-gray-700" />

            <button className="text-[10px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-300">
              Terms
            </button>

            <div className="h-1 w-1 rounded-full bg-gray-700" />

            <button className="text-[10px] font-bold uppercase tracking-widest text-gray-500 hover:text-gray-300">
              Status
            </button>
          </nav>
        </footer>
      </main>
    </div>
  );
}
