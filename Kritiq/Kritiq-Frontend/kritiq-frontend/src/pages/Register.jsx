import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { registerUser, getProfile } from "../api/authApi";
import { useAuth } from "../context/AuthContext";

import AuthLogo from "../components/auth/AuthLogo";
import AuthCard from "../components/auth/AuthCard";
import RegisterForm from "../components/auth/RegisterForm";

export default function Register() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [form, setForm] = useState({
    name: "",
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
      const registerResponse = await registerUser(form);

      const token = registerResponse.data.access_token;

      localStorage.setItem("token", token);

      const profileResponse = await getProfile();

      login(profileResponse.data, token);

      navigate("/dashboard");
    } catch (err) {
      console.error(err);

      const detail = err.response?.data?.detail;

      if (Array.isArray(detail)) {
        setError(detail[0].msg);
      } else {
        setError(detail || "Registration failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center auth-background px-4">
      <div className="w-full max-w-md">
        <AuthLogo />

        <AuthCard
          title="Create your account"
          subtitle="Start reviewing and translating code with Kritiq."
        >
          <RegisterForm
            form={form}
            handleChange={handleChange}
            handleSubmit={handleSubmit}
            loading={loading}
            error={error}
          />
        </AuthCard>
      </div>
    </div>
  );
}