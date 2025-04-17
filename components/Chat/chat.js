"use client";

import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { getChatbots, getChat, getAccessKey } from "@/app/apis";
import { toast } from "sonner";
import MarkdownPreview from "@uiw/react-markdown-preview";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useSearchParams } from "next/navigation";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";



export default function ChatWindow() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const chatbotId = searchParams.get("chatbot_id");
  const q = searchParams.get("q");


  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedChatbot, setSelectedChatbot] = useState(null);
  const [chatbots, setChatbots] = useState([]);
  const bottomRef = useRef(null);
  const [showAccessDialog, setShowAccessDialog] = useState(false);
  const [accessKey, setAccessKey] = useState("");
  const [accessScript, setAccessScript] = useState("");

  useEffect(() => {
    fetchChatbots();
  }, []);

  useEffect(() => {
    if (sessionId && chatbotId) {
      loadSessionMessages(sessionId, chatbotId);
      // Update selected chatbot if it exists in the chatbots list
      if (chatbots.length > 0) {
        const chatbot = chatbots.find((bot) => bot.id === parseInt(chatbotId));
        if (chatbot) {
          setSelectedChatbot(chatbot);
        }
      }
    }
    else {
      // Clear messages when there's no session (new chat)
      if(sessionId && q){

      }else{
        setMessages([]);
        setInput("");
      }
  
    }
  }, [sessionId, chatbotId, chatbots]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchChatbots = async () => {
    try {
      const data = await getChatbots();
      setChatbots(data);
      if (data.length > 0) {
        const initialChatbot = chatbotId
          ? data.find((bot) => bot.id === parseInt(chatbotId))
          : data[0];
        setSelectedChatbot(initialChatbot);
      }
    } catch (err) {
      toast.error("Failed to fetch chatbots");
    }
  };

  const loadSessionMessages = async (chatbotId, sessionId) => {
    try {
      setIsLoading(true);
      const data = await getChat(sessionId, chatbotId);
      const formattedMessages = data.messages.map((msg) => ({
        role: msg.role,
        content: msg.message,
      }));
      setMessages(formattedMessages);
    } catch (err) {
      toast.error("Failed to load chat history");
    } finally {
      setIsLoading(false);
    }
  };

  const handleChatbotChange = (chatbotId) => {
    const newChatbot = chatbots.find((bot) => bot.id === parseInt(chatbotId));
    if (newChatbot) {
      setSelectedChatbot(newChatbot);
      // Clear messages when switching chatbots
      setMessages([]);
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
      let newSessionId = null;

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
              if (parsed.content) {
                assistantMessage += parsed.content;
                setMessages((prev) => {
                  const newMessages = [...prev];
                  if (
                    newMessages[newMessages.length - 1]?.role === "assistant"
                  ) {
                    newMessages[newMessages.length - 1].content =
                      assistantMessage;
                  } else {
                    newMessages.push({
                      role: "assistant",
                      content: assistantMessage,
                    });
                  }
                  return newMessages;
                });
              }
              // Set session ID from the first response if it's null
              if (!sessionId && parsed.session_id && !newSessionId) {
                newSessionId = parsed.session_id;
                // Update URL with new session ID
                const url = new URL(window.location.href);
                url.searchParams.set("session_id", newSessionId);
                url.searchParams.set("q", userMessage);

                window.history.pushState({}, "", url);
              }
            } catch (e) {
              console.error("Error parsing chunk:", e);
            }
          }
        }
      }
    } catch (err) {
      toast.error(err.message || "Failed to send message");
      setMessages((prev) => [
        ...prev,
        { role: "error", content: "Failed to send message" },
      ]);
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

  const handleGetAccess = async () => {
    if (!selectedChatbot) return;
    
    try {
      const response = await getAccessKey({
        chatbot_id: selectedChatbot.id
      });
      
      if (response && response.key) {
        setAccessKey(response.key);
        const script = `<script src='http://localhost:3000/bundle.js' key=${response.key} chatbot_id=${selectedChatbot.id} class='build-chat-ai-bot' defer ></script>`;
        setAccessScript(script);
        setShowAccessDialog(true);
      }
    } catch (err) {
      toast.error("Failed to get access key");
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
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleGetAccess}
              disabled={!selectedChatbot}
            >
              Access External
            </Button>
            <Select
              value={selectedChatbot?.id?.toString()}
              onValueChange={handleChatbotChange}
            >
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Select a chatbot" />
              </SelectTrigger>
              <SelectContent>
                {chatbots.map((chatbot) => (
                  <SelectItem key={chatbot.id} value={chatbot.id.toString()}>
                    {chatbot.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
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
                      : ""
                  }`}
                >
                  <MarkdownPreview
                    source={message.content}
                    className="!bg-transparent !text-inherit prose prose-neutral dark:prose-invert max-w-none"
                  />
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
      <Dialog open={showAccessDialog} onOpenChange={setShowAccessDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>External Access Script</DialogTitle>
          </DialogHeader>
          <div className="mt-4">
            <p className="text-sm text-gray-500 mb-2">Copy and paste this script into your website:</p>
            <div className="bg-gray-100 p-4 rounded-md">
              <code className="text-sm break-all">{accessScript}</code>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </SidebarInset>
  );
}
