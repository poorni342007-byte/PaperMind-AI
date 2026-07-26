import axios from 'axios';

const BACKEND_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const API_BASE_URL = `${BACKEND_URL.replace(/\/$/, '')}/api`;

// Request interceptor to attach JWT authorization token if present
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('paperpal_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const authAPI = {
  signup: async (name, email, password) => {
    const response = await api.post('/auth/signup', { name, email, password });
    return response.data;
  },
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    if (response.data.access_token) {
      localStorage.setItem('paperpal_token', response.data.access_token);
    }
    return response.data;
  },
  getMe: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
  logout: () => {
    localStorage.removeItem('paperpal_token');
  }
};

export const pdfAPI = {
  upload: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  list: async () => {
    const response = await api.get('/pdf/list');
    return response.data;
  },
  getSummary: async (documentId) => {
    const response = await api.get(`/pdf/${documentId}/summary`);
    return response.data;
  },
  delete: async (documentId) => {
    const response = await api.delete(`/pdf/${documentId}`);
    return response.data;
  }
};

export const chatAPI = {
  ask: async (documentId, question) => {
    const response = await api.post('/chat/ask', { document_id: documentId, question });
    return response.data;
  },
  getQuiz: async (documentId) => {
    const response = await api.get(`/chat/${documentId}/quiz`);
    return response.data;
  }
};

export const historyAPI = {
  getChatsForDoc: async (documentId) => {
    const response = await api.get(`/history/chats/${documentId}`);
    return response.data;
  },
  getAllHistory: async () => {
    const response = await api.get('/history/all');
    return response.data;
  }
};

export default api;
