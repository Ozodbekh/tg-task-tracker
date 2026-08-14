import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import { ApiError, setUnauthorizedHandler } from "@/api/client";
import { backend } from "@/api/resources";
import type { Session } from "@/types/domain";

interface AuthValue {
  session: Session | null;
  ready: boolean;
  expired: boolean;
  signIn: (username: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthValue | null>(null);

function signInError(cause: unknown): string {
  if (cause instanceof ApiError) {
    if (cause.status === 401) return "Foydalanuvchi nomi yoki parol noto'g'ri";
    if (cause.status === 400) return "Ma'lumotlar to'liq kiritilmadi";
    if (cause.status >= 500) return "Server javob bermayapti, keyinroq urinib ko'ring";
    return cause.message;
  }
  return "Serverga ulanib bo'lmadi";
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    backend
      .me()
      .then(setSession)
      .catch(() => setSession(null))
      .finally(() => setReady(true));
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      setSession(null);
      setExpired(true);
    });
    return () => setUnauthorizedHandler(() => {});
  }, []);

  const signIn = useCallback(async (username: string, password: string) => {
    try {
      setSession(await backend.login(username, password));
      setExpired(false);
    } catch (cause) {
      throw new Error(signInError(cause));
    }
  }, []);

  const signOut = useCallback(async () => {
    try {
      await backend.logout();
    } finally {
      setSession(null);
      setExpired(false);
    }
  }, []);

  const value = useMemo(
    () => ({ session, ready, expired, signIn, signOut }),
    [session, ready, expired, signIn, signOut],
  );

  return <AuthContext value={value}>{children}</AuthContext>;
}

export function useAuth(): AuthValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
