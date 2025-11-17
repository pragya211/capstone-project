import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";

const LoginForm = () => {
  const { login, authError, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError(null);
    clearError();

    if (!email || !password) {
      setLocalError("Email and password are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      await login({ email, password });
      setEmail("");
      setPassword("");
    } catch (error) {
      // Error is managed in context; optional local handling
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="auth-card" onSubmit={handleSubmit}>
      <h3 className="auth-card__title">Log In</h3>
      <div className="auth-card__field">
        <label className="auth-card__label" htmlFor="login-email">
          Email
        </label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="auth-card__input"
          placeholder="you@example.com"
          autoComplete="email"
          required
        />
      </div>
      <div className="auth-card__field">
        <label className="auth-card__label" htmlFor="login-password">
          Password
        </label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="auth-card__input"
          placeholder="••••••••"
          autoComplete="current-password"
          required
          minLength={8}
        />
      </div>
      {(localError || authError) && (
        <div className="auth-card__message auth-card__message--error">
          {localError || authError}
        </div>
      )}
      <button className="auth-card__submit" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Signing in..." : "Sign In"}
      </button>
    </form>
  );
};
export default LoginForm;

