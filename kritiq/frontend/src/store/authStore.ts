import { create } from "zustand";

export interface User {
  id: string;
  provider: string;
  provider_id: string;
  email: string;
  name: string;
  avatar_url: string;
  created_at: string;
  last_login: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string, user: User) => void;
  logout: () => void;
  setUser: (user: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => {
  const storedToken = localStorage.getItem("kritiq_token");

  return {
    user: null,
    token: storedToken,
    isAuthenticated: !!storedToken,
    login: (token, user) => {
      localStorage.setItem("kritiq_token", token);
      set({ token, user, isAuthenticated: true });
    },
    logout: () => {
      localStorage.removeItem("kritiq_token");
      set({ token: null, user: null, isAuthenticated: false });
    },
    setUser: (user) => {
      set({ user, isAuthenticated: !!user });
    },
  };
});
