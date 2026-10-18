"use client";

import { useState, useEffect } from "react";

export interface GuestUsageState {
  isGuest: boolean;
  user: {
    username?: string;
    email?: string;
    role?: string;
  } | null;
  count: number;
  limit: number;
  remaining: number;
  isLimitReached: boolean;
  incrementUsage: () => boolean;
}

const GUEST_LIMIT = 10;
const STORAGE_KEY = "visionlytics_guest_upload_count";

export function useGuestQuota(): GuestUsageState {
  const [user, setUser] = useState<{ username?: string; email?: string; role?: string } | null>(null);
  const [count, setCount] = useState<number>(0);
  const [isMounted, setIsMounted] = useState<boolean>(false);

  useEffect(() => {
    setIsMounted(true);
    // Check if user is logged in
    try {
      const stored = localStorage.getItem("visionlytics_user");
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && (parsed.username || parsed.email)) {
          setUser(parsed);
          return;
        }
      }
    } catch {
      // Ignore parse errors
    }

    // Guest user - load usage count
    try {
      const savedCount = parseInt(localStorage.getItem(STORAGE_KEY) || "0", 10);
      setCount(isNaN(savedCount) ? 0 : savedCount);
    } catch {
      setCount(0);
    }
  }, []);

  const isGuest = !user;
  const remaining = isGuest ? Math.max(0, GUEST_LIMIT - count) : Infinity;
  const isLimitReached = isGuest && count >= GUEST_LIMIT;

  const incrementUsage = (): boolean => {
    // If logged in, unlimited usage allowed
    if (user) {
      return true;
    }

    const current = parseInt(localStorage.getItem(STORAGE_KEY) || "0", 10) || 0;
    if (current >= GUEST_LIMIT) {
      setCount(current);
      return false;
    }

    const next = current + 1;
    try {
      localStorage.setItem(STORAGE_KEY, next.toString());
    } catch {
      // LocalStorage error fallback
    }
    setCount(next);
    return true;
  };

  return {
    isGuest,
    user,
    count: isGuest ? count : 0,
    limit: GUEST_LIMIT,
    remaining: isGuest ? remaining : 999999,
    isLimitReached: isMounted ? isLimitReached : false,
    incrementUsage,
  };
}
