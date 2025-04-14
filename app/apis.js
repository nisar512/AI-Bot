import axios from "axios";
import Cookies from "js-cookie";

const getToken = () => Cookies.get("token");
const getUserId = () => Cookies.get("user_id");


const axiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

axiosInstance.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = async (data) => {
  try {
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/auth/login`,
      data,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};
export const createChatbot = async (data) => {
  try {
    const userId = getUserId();
    data.user_id = userId;
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots`,
      data,
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

const handleApiError = (error) => {
  if (error.response) {
    // console.error("API Error:", error.response.data);
    throw new Error(error.response.data.detail || "An error occurred");
  } else {
    // console.error("API Error:", error.message);
    throw new Error("Network error or server not reachable");
  }
};
