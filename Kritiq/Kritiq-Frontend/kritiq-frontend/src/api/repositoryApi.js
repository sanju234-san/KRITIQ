import axiosInstance from "./axiosInstance";

export const connectRepository = (repoUrl) => {
  return axiosInstance.post(
    `/repositories/connect?repo_url=${encodeURIComponent(repoUrl)}`
  );
};

export const getRepositories = () => {
  return axiosInstance.get("/repositories/");
};