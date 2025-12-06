import axios from "axios";

export const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "https://capstone-project-81fb.onrender.com";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
});

export const setAuthToken = (token) => {
  if (token) {
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common.Authorization;
  }
};

export default apiClient;

