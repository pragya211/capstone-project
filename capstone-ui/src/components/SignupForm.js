import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";

const SignupForm = ({ onSuccess }) => {
  const { signup, authError, clearError } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [localError, setLocalError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLocalError(null);
    setSuccessMessage(null);
    clearError();

    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters long.");
      return;
    }

    if (password !== confirmPassword) {
      setLocalError("Passwords do not match.");
      return;
    }

    setIsSubmitting(true);
    try {
      await signup({ email, password, fullName });
      setSuccessMessage(
        "Account created successfully! You can now sign in with your credentials."
      );
      setEmail("");
      setFullName("");
      setPassword("");
      setConfirmPassword("");
      if (onSuccess) {
        onSuccess();
      }
    } catch (error) {
      // Error handled by context
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="auth-card" onSubmit={handleSubmit}>
      <h3 className="auth-card__title">Create Account</h3>

      <div className="auth-card__field">
        <label className="auth-card__label" htmlFor="signup-email">
          Email
        </label>
        <input
          id="signup-email"
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
        <label className="auth-card__label" htmlFor="signup-full-name">
          Full Name <span className="auth-card__label-hint">(optional)</span>
        </label>
        <input
          id="signup-full-name"
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          className="auth-card__input"
          placeholder="Ada Lovelace"
          autoComplete="name"
        />
      </div>

      <div className="auth-card__field">
        <label className="auth-card__label" htmlFor="signup-password">
          Password
        </label>
        <input
          id="signup-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="auth-card__input"
          placeholder="Create a secure password"
          autoComplete="new-password"
          required
          minLength={8}
        />
      </div>

      <div className="auth-card__field">
        <label className="auth-card__label" htmlFor="signup-confirm-password">
          Confirm Password
        </label>
        <input
          id="signup-confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          className="auth-card__input"
          placeholder="Re-enter your password"
          autoComplete="new-password"
          required
          minLength={8}
        />
      </div>

      {(localError || authError) && (
        <div className="auth-card__message auth-card__message--error">
          {localError || authError}
        </div>
      )}

      {successMessage && (
        <div className="auth-card__message auth-card__message--success">{successMessage}</div>
      )}

      <button className="auth-card__submit auth-card__submit--accent" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creating account..." : "Sign Up"}
      </button>
    </form>
  );
};

export default SignupForm;

