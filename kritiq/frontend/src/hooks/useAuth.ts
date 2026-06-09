import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store/authStore";

export function useAuth() {
  const navigate = useNavigate();
  const location = useLocation();
  const { token, user, logout, setUser } = useAuthStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function checkAuth() {
      if (!token) {
        if (active) setLoading(false);
        if (location.pathname !== "/login") {
          navigate("/login");
        }
        return;
      }

      try {
        const response = await fetch("/api/auth/me", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          if (active) {
            setUser(userData);
            if (location.pathname === "/login") {
              navigate("/");
            }
          }
        } else {
          if (active) {
            logout();
            navigate("/login");
          }
        }
      } catch (error) {
        console.error("Authentication check failed:", error);
        // On network errors in dev, we don't force logout immediately to allow offline work
        if (active) setLoading(false);
      } finally {
        if (active) setLoading(false);
      }
    }

    checkAuth();

    return () => {
      active = false;
    };
  }, [token, location.pathname, navigate, logout, setUser]);

  return { user, token, loading, logout };
}
