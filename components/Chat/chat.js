"use client";

import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getChatbots } from "@/app/apis";
import { toast } from "sonner";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

// Sample messages
const initialMessages = [
  { id: 1, role: "system", content: "How can I help you today?" },
  {
    id: 2,
    role: "user",
    content: "I need help with creating a responsive layout.",
  },
  {
    id: 3,
    role: "system",
    content:
      "Sure, I can help with that. Would you like to use CSS Grid, Flexbox, or a combination of both?",
  },
];

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [chatbots, setChatbots] = useState([]);
  const bottomRef = useRef(null);

  useEffect(() => {
    fetchChatbots();
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchChatbots = async () => {
    try {
      const data = await getChatbots();
      setChatbots(data);
      if (data.length > 0) {
        setSelectedChatbot(data[0]);
      }
    } catch (err) {
      toast.error("Failed to fetch chatbots");
    }
  };

  const handleChatbotChange = (chatbotId) => {
    const newChatbot = chatbots.find((bot) => bot.id === chatbotId);
    if (newChatbot) {
      setSelectedChatbot(newChatbot);
      // Clear messages and session ID when switching chatbots
      setMessages([]);
      setSessionId(null);
    }
  };

  const handleSendMessage = async () => {
    if (!input.trim() || !selectedChatbot) return;

    const userMessage = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    setIsLoading(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/chatbots/${selectedChatbot.id}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: userMessage,
            chatbot_id: selectedChatbot.id,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const reader = response.body.getReader();
      let assistantMessage = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const data = line.slice(6);
            if (data === "[DONE]") {
              break;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed.session_id && !sessionId) {
                setSessionId(parsed.session_id);
              }
              if (parsed.content) {
                assistantMessage += parsed.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  if (newMessages[newMessages.length - 1]?.role === "assistant") {
                    newMessages[newMessages.length - 1].content = assistantMessage;
                  } else {
                    newMessages.push({ role: "assistant", content: assistantMessage });
                  }
                  return newMessages;
                });
              }
            } catch (e) {
              console.error("Error parsing chunk:", e);
            }
          }
        }
      }
    } catch (err) {
      toast.error(err.message || "Failed to send message");
      setMessages((prev) => [...prev, { role: "error", content: "Failed to send message" }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <SidebarInset className="flex flex-col h-screen">
      {" "}
      {/* Full height of screen */}
      <header className="flex h-14 items-center border-b px-4">
        <SidebarTrigger className="mr-2" />
        <div className="flex-1 flex items-center justify-between">
          <h1 className="text-lg font-semibold">Chat</h1>
          <Select
            value={selectedChatbot?.id}
            onValueChange={handleChatbotChange}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Select a chatbot" />
            </SelectTrigger>
            <SelectContent>
              {chatbots.map((chatbot) => (
                <SelectItem key={chatbot.id} value={chatbot.id}>
                  {chatbot.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </header>
      {/* Message area */}
      <div className="flex-1 overflow-hidden">
        {" "}
        {/* Take all remaining space */}
        <ScrollArea className="h-full">
          <div className="max-w-[786px] mx-auto flex flex-col space-y-4 p-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : message.role === "error"
                      ? "bg-red-100 text-red-900"
                      : "bg-muted"
                  }`}
                >
                  {message.content}
                </div>
              </div>
            ))}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>
      </div>
      {/* Input box */}
      <div className="border-t p-4">
        <div className="flex items-end gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="min-h-[60px] resize-none"
            disabled={isLoading || !selectedChatbot}
          />
          <Button
            onClick={handleSendMessage}
            size="icon"
            className="h-10 w-10 shrink-0"
            disabled={isLoading || !input.trim() || !selectedChatbot}
          >
            <Send size={18} />
          </Button>
        </div>
      </div>
    </SidebarInset>
  );
}
