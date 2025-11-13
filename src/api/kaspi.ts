import axios from 'axios';
import { API_URL, API_BASE_PATH } from '@/config';

const API_BASE_URL = `${API_URL}${API_BASE_PATH}`;

export const kaspiApi = {
  // Авторизация магазина Kaspi
  async authenticate(userId: string, email: string, password: string) {
    try {
      const response = await axios.post(`${API_BASE_URL}/kaspi/auth`, {
        user_id: userId,
        email,
        password,
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Ошибка авторизации');
    }
  },

  // Получение списка подключенных магазинов
  async getStores(userId: string) {
    try {
      const response = await axios.get(`${API_BASE_URL}/kaspi/stores`, {
        params: { user_id: userId },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Ошибка получения магазинов');
    }
  },  
};
