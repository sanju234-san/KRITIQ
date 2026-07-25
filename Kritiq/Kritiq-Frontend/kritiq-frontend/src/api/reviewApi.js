import axiosInstance from "./axiosInstance";

export const reviewCode = (payload) => {
  return axiosInstance.post("/reviews/", payload);
};