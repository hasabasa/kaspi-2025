
import { useState, useEffect, useRef } from 'react';
import { supabase } from "@/integrations/supabase/client";
import { User, Session } from '@supabase/supabase-js';

export const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const isInitialized = useRef(false);

  useEffect(() => {
    if (isInitialized.current) {
      return; // Убираем лишний лог
    }

    isInitialized.current = true;

    // Set up auth state listener
    const { data: authListener } = supabase.auth.onAuthStateChange(
      (event, currentSession) => {
        // Логируем только важные события
        if (event === 'SIGNED_IN' || event === 'SIGNED_OUT') {
          console.log("useAuth: Auth state changed:", event);
        }
        
        if (currentSession?.user) {
          setSession(currentSession);
          setUser(currentSession.user);
        } else {
          setSession(null);
          setUser(null);
        }
        setLoading(false);
      }
    );

    // Get initial session
    const getSession = async () => {
      try {
        const { data } = await supabase.auth.getSession();
        
        if (data?.session?.user) {
          setSession(data.session);
          setUser(data.session.user);
        } else {
          setSession(null);
          setUser(null);
        }
      } catch (error) {
        console.error('useAuth: Error checking session:', error);
        setUser(null);
        setSession(null);
      } finally {
        setLoading(false);
      }
    };
    
    getSession();

    return () => {
      authListener.subscription.unsubscribe();
    };
  }, []);

  const signUp = async (email: string, password: string, options?: any) => {
    const redirectUrl = `${window.location.origin}/`;
    
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        emailRedirectTo: redirectUrl,
        data: options?.data || {}
      }
    });
    
    return { data, error };
  };

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({ email, password });
    return { data, error };
  };

  const signOut = async () => {
    console.log("useAuth: Starting sign out process");
    
    try {
      // Clear auth state immediately
      setUser(null);
      setSession(null);
      
      // Then call Supabase signOut
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        console.error("useAuth: Error during sign out:", error);
        throw error;
      }
      
      console.log("useAuth: Sign out completed successfully");
    } catch (error) {
      console.error("useAuth: Sign out failed:", error);
      throw error;
    }
  };

  return { 
    user, 
    session,
    signUp, 
    signIn, 
    signOut,
    loading,
    isSupabaseConfigured: true 
  };
};

export default useAuth;
