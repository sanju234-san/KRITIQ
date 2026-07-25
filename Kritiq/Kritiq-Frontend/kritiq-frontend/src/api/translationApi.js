import axiosInstance from "./axiosInstance";

export const translateCode = (data) => {
  return axiosInstance.post("/translations/", data);
};

export const getTranslation = (translationId) => {
  return axiosInstance.get(`/translations/${translationId}`);
};