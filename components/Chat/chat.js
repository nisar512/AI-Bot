"use client";

import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";

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
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);
  const handleSendMessage = () => {
    if (!input.trim()) return;

    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      role: "user",
      content: input,
    };

    // Add system response (in a real app, this would come from an API)
    const newSystemMessage = {
      id: messages.length + 2,
      role: "system",
      content: `This is a simulated response to: "${input}"`,
    };

    setMessages([...messages, newUserMessage, newSystemMessage]);
    setInput("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  return (
    <SidebarInset className="flex flex-col h-screen">
      {" "}
      {/* Full height of screen */}
      <header className="flex h-14 items-center border-b px-4">
        <SidebarTrigger className="mr-2" />
        <h1 className="text-lg font-semibold">Chat</h1>
      </header>
      {/* Message area */}
      <div className="flex-1 overflow-hidden">
        {" "}
        {/* Take all remaining space */}
        <ScrollArea className="h-full">
          <div className="max-w-[786px] mx-auto flex flex-col space-y-4 p-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-2 ${
                    message.role === "user"
                      ? "bg-primary text-primary-foreground"
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
          />
          <Button
            onClick={handleSendMessage}
            size="icon"
            className="h-10 w-10 shrink-0"
          >
            <Send size={18} />
          </Button>
        </div>
      </div>
    </SidebarInset>
  );
}
