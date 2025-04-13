"use client";
import { SidebarProvider } from "@/components/ui/sidebar";
import ChatSidebar from "../sidebar/sidebar";
import ChatWindow from "../Chat/chat";
export default function ChatLayout() {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen bg-background">
        <ChatSidebar />

        <ChatWindow />
      </div>
    </SidebarProvider>
  );
}
