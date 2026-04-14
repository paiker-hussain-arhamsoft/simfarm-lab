import { useEffect, useState } from "react";

const SESSION_KEY = "compliance_session_id";

export function useSessionId(): string {
  const [sessionId, setSessionId] = useState<string>(() => {
    const existing = sessionStorage.getItem(SESSION_KEY);
    if (existing) return existing;
    const fresh = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, fresh);
    return fresh;
  });

  return sessionId;
}
