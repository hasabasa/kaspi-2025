// Мок версия useAuth для диагностики
import { useState, useEffect } from 'react';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Симулируем быструю загрузку без реального auth
    console.log("Mock useAuth: Быстрая инициализация без реального auth");
    
    setTimeout(() => {
      setLoading(false);
      console.log("Mock useAuth: Загрузка завершена, пользователь не авторизован");
    }, 100);
  }, []);

  const signUp = async (email: string, password: string) => {
    console.log("Mock signUp called");
    return { data: null, error: null };
  };

  const signIn = async (email: string, password: string) => {
    console.log("Mock signIn called");
    return { data: null, error: null };
  };

  const signOut = async () => {
    console.log("Mock signOut called");
    setUser(null);
    setSession(null);
  };

  const resetPassword = async (email: string) => {
    console.log("Mock resetPassword called");
    return { data: null, error: null };
  };

  return {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    resetPassword
  };
};
