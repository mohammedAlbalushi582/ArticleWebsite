"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { clearTokens, getStoredUser, isLoggedIn, type User } from "@/lib/api";

export function useAuth({ redirect = true } = {}) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const loggedIn = isLoggedIn();
    if (loggedIn) {
      setUser(getStoredUser());
    } else if (redirect) {
      router.replace("/login");
    }
    setLoading(false);
  }, [redirect, router]);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    router.replace("/login");
  }, [router]);

  return { user, loading, logout };
}
