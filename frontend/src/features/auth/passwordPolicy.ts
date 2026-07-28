/** Client-side password policy aligned with backend PASSWORD_MIN_LENGTH (default 8). */

export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 72;

export type PasswordStrengthLevel = "empty" | "weak" | "fair" | "good" | "strong";

export interface PasswordStrength {
  level: PasswordStrengthLevel;
  score: number;
  label: string;
}

export function evaluatePasswordStrength(password: string): PasswordStrength {
  if (!password) {
    return { level: "empty", score: 0, label: "Enter a password" };
  }

  let score = 0;
  if (password.length >= PASSWORD_MIN_LENGTH) score += 1;
  if (password.length >= 12) score += 1;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score += 1;
  if (/\d/.test(password)) score += 1;
  if (/[^A-Za-z0-9]/.test(password)) score += 1;

  if (score <= 1) return { level: "weak", score, label: "Weak" };
  if (score === 2) return { level: "fair", score, label: "Fair" };
  if (score === 3) return { level: "good", score, label: "Good" };
  return { level: "strong", score, label: "Strong" };
}

export function validateNewPassword(password: string): string | null {
  if (!password || !password.trim()) {
    return "Password must not be blank";
  }
  if (password.trim() !== password) {
    return "Password must not have leading or trailing whitespace";
  }
  if (password.length < PASSWORD_MIN_LENGTH) {
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters`;
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    return `Password must be at most ${PASSWORD_MAX_LENGTH} characters`;
  }
  return null;
}

export function validatePasswordConfirmation(
  password: string,
  confirmPassword: string,
): string | null {
  if (password !== confirmPassword) {
    return "Passwords do not match";
  }
  return null;
}

/** Map reset-token API details.reason to a user-facing message. */
export function resetTokenErrorMessage(
  reason: unknown,
  fallback: string,
): string {
  switch (reason) {
    case "expired":
      return "This reset link has expired. Request a new one.";
    case "reused":
      return "This reset link has already been used. Request a new one.";
    case "invalid":
    case "inactive_user":
      return "This reset link is invalid. Request a new one.";
    default:
      return fallback || "Invalid or expired reset token";
  }
}
