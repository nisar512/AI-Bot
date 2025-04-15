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
    console.log(userId);

    data["user_id"] = userId;
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots`,
      data
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

///api/v1/chatbots/user/{user_id}

export const getChatbots = async () => {
  try {
    const userId = getUserId();

    const response = await axiosInstance.get(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots/user/${userId}`
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

///api/v1/chatbots/{chatbot_id}

export const deleteChatbot = async (chatbotId) => {
  try {
    const response = await axiosInstance.delete(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots/${chatbotId}`
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

///api/v1/chatbots/{chatbot_id}/upload-document

export const uploadDocument = async (chatbotId, data) => {
  try {
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots/${chatbotId}/upload-document`, 
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

///api/v1/scrape/scrape

export const scrape = async (url,chatbot_id) => {
  try {
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/scrape/scrape?url=${url}&chatbot_id=${chatbot_id}`,
    );
    return response.data;
  } catch (error) {
    handleApiError(error);
  }
};

///api/v1/scrape/process-sitemap?sitemap_url={sitemap_url}&chatbot_id={chatbot_id}

export const processSitemap = async (sitemap_url,chatbot_id,limit) => {
  try {
    const response = await axiosInstance.post(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/scrape/process-sitemap?sitemap_url=${sitemap_url}&chatbot_id=${chatbot_id}&limit=${limit}`,
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
