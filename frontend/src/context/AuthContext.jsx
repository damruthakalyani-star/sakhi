import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { api, setAuthToken, getAuthToken } from "../lib/api";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchUserProfile = useCallback(async () => {
    try {
      const token = getAuthToken();
      if (!token) {
        setUser(null);
        setLoading(false);
        return;
      }
      const userData = await api.get("/auth/me");
      setUser(userData);
    } catch (err) {
      console.warn("Failed to fetch user profile, session may have expired:", err.message);
      setAuthToken(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUserProfile();

    const handleAuthExpired = () => {
      setUser(null);
      setAuthToken(null);
    };

    window.addEventListener("auth:expired", handleAuthExpired);
    return () => {
      window.removeEventListener("auth:expired", handleAuthExpired);
    };
  }, [fetchUserProfile]);

  const login = async (email, password) => {
    const data = await api.post("/auth/login", { email, password });
    if (data.access_token) {
      setAuthToken(data.access_token);
      setUser(data.user);
    }
    return data;
  };

  const register = async (userData) => {
    const data = await api.post("/auth/signup", userData);
    if (data.access_token) {
      setAuthToken(data.access_token);
      setUser(data.user);
    }
    return data;
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout", {});
    } catch {
      // Ignore network errors on logout
    } finally {
      setAuthToken(null);
      setUser(null);
    }
  };

  const refreshProfile = async () => {
    if (getAuthToken()) {
      await fetchUserProfile();
    }
  };

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
