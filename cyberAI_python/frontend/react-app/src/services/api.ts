// API 服务层 - axios 封装, 统一处理 token
import axios from "axios";

const api = axios.create({ baseURL: "/api" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = \`Bearer \${token}\`;
  return config;
});

export const authApi = {
  login: (u, p) => api.post("/auth/login", { username: u, password: p }),
};

export const chatApi = {
  send: (msg) => api.post("/chat", { message: msg }),
};
