import React, { useState, useEffect, createContext, useContext } from 'react';
import { apiClient } from '../lib/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    console.log("checkAuthStatus called");
    try {
      const token = localStorage.getItem("access_token");
      console.log("Token from localStorage:", token);
      if (token) {
        apiClient.setToken(token);
        const userData = await apiClient.getCurrentUser();
        console.log("User data from getCurrentUser:", userData);
        setUser(userData);
      }
    } catch (error) {
      console.error("Auth check failed:", error);
      localStorage.removeItem("access_token");
      apiClient.setToken(null);
    } finally {
      setLoading(false);
      console.log("Loading set to false");
    }
  };

  const login = async (username, password) => {
    console.log("Login function called with username:", username);
    try {
      setError(null);
      setLoading(true);
      const response = await apiClient.login(username, password);
      console.log("Login API response:", response);
      if (response.access_token) {
        apiClient.setToken(response.access_token);
        const userData = await apiClient.getCurrentUser();
        console.log("User data after login:", userData);
        setUser(userData);
      }
      return response;
    } catch (error) {
      setError(error.message);
      console.error("Login error:", error);
      throw error;
    } finally {
      setLoading(false);
      console.log("Loading set to false after login");
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      setLoading(true);
      const response = await apiClient.register(userData);
      if (response.access_token) {
        apiClient.setToken(response.access_token);
        setUser(response.user);
      }
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.logout();
      setUser(null);
      setError(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const hasRole = (requiredRoles) => {
    if (!user) return false;
    if (Array.isArray(requiredRoles)) {
      return requiredRoles.includes(user.role);
    }
    return user.role === requiredRoles;
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    hasRole,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

