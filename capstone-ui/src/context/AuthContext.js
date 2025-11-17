import React, {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import apiClient, { setAuthToken } from "../apiClient";

const AuthContext = createContext(null);

const ACCESS_TOKEN_STORAGE_KEY = "capstone_access_token";

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(() =>
    localStorage.getItem(ACCESS_TOKEN_STORAGE_KEY)
  );
  const [loading, setLoading] = useState(true);
  const [authError, setAuthError] = useState(null);

  useEffect(() => {
    const initialize = async () => {
      if (!accessToken) {
        setAuthToken(null);
        setLoading(false);
        return;
      }

      setAuthToken(accessToken);
      try {
        const { data } = await apiClient.get("/auth/me");
        setUser(data);
      } catch (error) {
        console.error("Failed to load current user:", error);
        localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
        setAccessToken(null);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initialize();
  }, [accessToken]);

  const signup = async ({ email, password, fullName }) => {
    try {
      await apiClient.post("/auth/signup", {
        email,
        password,
        full_name: fullName || undefined,
      });
      setAuthError(null);
      return true;
    } catch (error) {
      console.error("Signup failed:", error);
      let message = "Unable to create account";
      if (error.response?.data) {
        const detail = error.response.data.detail;
        if (typeof detail === "string") {
          message = detail;
        } else if (Array.isArray(detail) && detail.length > 0) {
          const first = detail[0];
          if (typeof first === "string") {
            message = first;
          } else if (first?.msg) {
            message = first.msg;
          }
        }
      } else if (error.message) {
        message = error.message;
      }
      setAuthError(message);
      throw error;
    }
  };

  const login = async ({ email, password }) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const { data } = await apiClient.post("/auth/login", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, data.access_token);
      setAuthToken(data.access_token);
      setAccessToken(data.access_token);
      setAuthError(null);

      const meResponse = await apiClient.get("/auth/me");
      setUser(meResponse.data);
    } catch (error) {
      console.error("Login failed:", error);
      const message =
        error.response?.data?.detail || error.message || "Invalid credentials";
      setAuthError(message);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
    setAccessToken(null);
    setUser(null);
    setAuthToken(null);
  };

  const value = useMemo(
    () => ({
      user,
      loading,
      authError,
      signup,
      login,
      logout,
      clearError: () => setAuthError(null),
    }),
    [user, loading, authError]
  );

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

