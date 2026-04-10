"use client";

import { useState } from "react";
import type { CSSProperties } from "react";
import { useRouter } from "next/navigation";
import { loginUser, logoutUser, registerUser } from "@/lib/api/client";
import type { UserDto } from "@/lib/api/types";

type AuthPanelProps = {
  user: UserDto;
};

export function AuthPanel({ user }: AuthPanelProps) {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === "register") {
        await registerUser({ email, name, password });
      } else {
        await loginUser({ email, password });
      }
      router.refresh();
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : "Authentication failed.");
      setIsSubmitting(false);
    }
  }

  async function handleLogout() {
    setIsSubmitting(true);
    setError(null);

    try {
      await logoutUser();
      router.refresh();
    } catch (logoutError) {
      setError(logoutError instanceof Error ? logoutError.message : "Logout failed.");
      setIsSubmitting(false);
    }
  }

  if (user.authSource === "session") {
    return (
      <section style={panelStyle}>
        <div style={{ display: "grid", gap: 6 }}>
          <strong style={{ fontSize: 16 }}>Signed In</strong>
          <span style={copyStyle}>
            {user.name} · {user.email}
          </span>
        </div>
        <button disabled={isSubmitting} onClick={() => void handleLogout()} style={secondaryButtonStyle} type="button">
          {isSubmitting ? "Signing out..." : "Sign Out"}
        </button>
        {error ? <p style={errorStyle}>{error}</p> : null}
      </section>
    );
  }

  return (
    <section style={panelStyle}>
      <div style={{ display: "grid", gap: 6 }}>
        <strong style={{ fontSize: 16 }}>Demo Auth</strong>
        <span style={copyStyle}>
          You are currently using the seeded dev fallback. Register or sign in to use a real session-backed account.
        </span>
      </div>
      <div style={toggleRowStyle}>
        <button onClick={() => setMode("login")} style={toggleButtonStyle(mode === "login")} type="button">
          Login
        </button>
        <button onClick={() => setMode("register")} style={toggleButtonStyle(mode === "register")} type="button">
          Register
        </button>
      </div>
      <form onSubmit={handleSubmit} style={formStyle}>
        {mode === "register" ? (
          <label style={labelStyle}>
            Name
            <input onChange={(event) => setName(event.target.value)} style={inputStyle} value={name} />
          </label>
        ) : null}
        <label style={labelStyle}>
          Email
          <input onChange={(event) => setEmail(event.target.value)} style={inputStyle} value={email} />
        </label>
        <label style={labelStyle}>
          Password
          <input onChange={(event) => setPassword(event.target.value)} style={inputStyle} type="password" value={password} />
        </label>
        <button disabled={isSubmitting || email.trim().length === 0 || password.trim().length < 8 || (mode === "register" && name.trim().length === 0)} style={primaryButtonStyle} type="submit">
          {isSubmitting ? (mode === "register" ? "Registering..." : "Signing in...") : mode === "register" ? "Register" : "Sign In"}
        </button>
      </form>
      {error ? <p style={errorStyle}>{error}</p> : null}
    </section>
  );
}

const panelStyle: CSSProperties = {
  display: "grid",
  gap: 14,
  padding: 20,
  border: "1px solid #262b36",
  borderRadius: 16,
  background: "#171a21"
};

const copyStyle: CSSProperties = {
  color: "#9ba3b4",
  fontSize: 14,
  lineHeight: 1.6
};

const toggleRowStyle: CSSProperties = {
  display: "inline-flex",
  gap: 8
};

function toggleButtonStyle(isActive: boolean): CSSProperties {
  return {
    padding: "8px 10px",
    border: `1px solid ${isActive ? "#7fa4ff" : "#3b4254"}`,
    borderRadius: 10,
    background: isActive ? "#18253d" : "#171a21",
    color: isActive ? "#dce8ff" : "#eef1f6",
    cursor: "pointer",
    fontSize: 12,
    fontWeight: 600,
  };
}

const formStyle: CSSProperties = {
  display: "grid",
  gap: 10
};

const labelStyle: CSSProperties = {
  display: "grid",
  gap: 6,
  color: "#c8d0de",
  fontSize: 13
};

const inputStyle: CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  border: "1px solid #313748",
  borderRadius: 12,
  background: "#0f1115",
  color: "#eef1f6"
};

const primaryButtonStyle: CSSProperties = {
  width: "fit-content",
  padding: "10px 14px",
  border: "1px solid #3b4254",
  borderRadius: 12,
  background: "#eef1f6",
  color: "#0f1115",
  cursor: "pointer"
};

const secondaryButtonStyle: CSSProperties = {
  ...primaryButtonStyle,
  background: "#171a21",
  color: "#eef1f6"
};

const errorStyle: CSSProperties = {
  margin: 0,
  color: "#ff8d8d",
  fontSize: 13
};
