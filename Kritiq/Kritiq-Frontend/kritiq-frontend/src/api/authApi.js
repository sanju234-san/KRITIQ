import axiosInstance from "./axiosInstance";

export const loginUser = (credentials) =>
  axiosInstance.post("/auth/login", credentials);

export const registerUser = (userData) =>
  axiosInstance.post("/auth/register", userData);

export const getProfile = () =>
  axiosInstance.get("/auth/profile");