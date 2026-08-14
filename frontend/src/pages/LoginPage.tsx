import { useState } from "react";
import type { FormEvent } from "react";

import { useAuth } from "@/hooks/AuthContext";

export function LoginPage() {
  const { signIn, expired } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await signIn(username, password);
    } catch (cause) {
      setError((cause as Error).message);
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="login">
      <form className="card login-card" onSubmit={submit}>
        <div className="row">
          <span className="brand-mark">TT</span>
          <div className="stack">
            <h1 className="card-title">Task Tracker</h1>
            <span className="cell-sub">Boshqaruvchi paneli</span>
          </div>
        </div>

        <div className="field">
          <label htmlFor="username">Foydalanuvchi nomi</label>
          <input
            id="username"
            className="input"
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            autoComplete="username"
            required
          />
        </div>

        <div className="field">
          <label htmlFor="password">Parol</label>
          <input
            id="password"
            type="password"
            className="input"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            autoComplete="current-password"
            required
          />
        </div>

        {!error && expired && (
          <p className="muted">Sessiya muddati tugadi. Iltimos, qaytadan kiring.</p>
        )}

        {error && <p className="error-text">{error}</p>}

        <button type="submit" className="primary-button" disabled={pending}>
          {pending ? "Kirilmoqda…" : "Kirish"}
        </button>
      </form>
    </div>
  );
}
