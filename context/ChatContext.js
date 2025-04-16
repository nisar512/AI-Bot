"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { getSessions } from "@/app/apis";

const ChatContext = createContext();

export function ChatProvider({ children }) {
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchSessions = async () => {
    try {
      const data = await getSessions();
      setSessions(data.sessions);
    } catch (err) {
      console.error("Failed to fetch sessions:", err);
    } finally {
      setIsLoading(false);
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchSessions();
  }, []);

  const refreshSessions = () => {
    fetchSessions();
  };

  return (
    <ChatContext.Provider value={{ sessions, isLoading, refreshSessions }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
} 