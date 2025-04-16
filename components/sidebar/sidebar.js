"use client"
import { Plus, MessageSquare, Settings, User, Bot, LogOut } from "lucide-react"
import { useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { getSessions } from "@/app/apis"
import { useChat } from "@/context/ChatContext"
import { Skeleton } from "@/components/ui/skeleton"
import Cookies from "js-cookie"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export default function ChatSidebar() {
  const router = useRouter();
  const [sessions, setSessions] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const { refreshSessions } = useChat();

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

  useEffect(() => {
    fetchSessions();
  }, [refreshSessions]);

  // Expose fetchSessions to window for other components to use
  useEffect(() => {
    window.fetchSessions = fetchSessions;
    return () => {
      delete window.fetchSessions;
    };
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return "Today";
    if (diffInDays === 1) return "Yesterday";
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    return date.toLocaleDateString();
  };

  return (
    <Sidebar>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Button variant="outline"
              onClick={() => router.push("/dashboard/chat")}
              className="w-full justify-start gap-2">
                <Plus size={16} />
                <span>New Chat</span>
              </Button>
            </SidebarMenuButton>
          </SidebarMenuItem>
          <SidebarMenuItem>
            <SidebarMenuButton asChild>
              <Button 
                variant="outline" 
                className="w-full justify-start gap-2"
                onClick={() => router.push("/dashboard")}
              >
                <Bot size={16} />
                <span>Create New Bot</span>
              </Button>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Recent Chats</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {isLoading ? (
                <div className="space-y-3 px-2">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="flex items-center gap-3 p-2 rounded-md hover:bg-accent/50">
                      <Skeleton className="h-5 w-5 rounded-full bg-muted-foreground/20" />
                      <div className="flex flex-col gap-2 w-full">
                        <Skeleton className="h-4 w-[80%] bg-muted-foreground/20" />
                        <Skeleton className="h-3 w-[60%] bg-muted-foreground/20" />
                      </div>
                    </div>
                  ))}
                </div>
              ) : sessions.length === 0 ? (
                <div className="p-2 text-sm text-muted-foreground">No recent chats</div>
              ) : (
                [...sessions].reverse().map((session) => (
                  <SidebarMenuItem key={session.id}>
                    <SidebarMenuButton
                      onClick={() => router.push(`/dashboard/chat?session_id=${session.id}&chatbot_id=${session.chatbot_id}`)}
                    >
                      <MessageSquare size={16} />
                      <div className="flex flex-col items-start">
                        <span className="truncate max-w-[200px]">{session.first_message}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatDate(session.created_at)} • {session.chatbot_name}
                        </span>
                      </div>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                ))
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter>
        <Separator className="my-2" />
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={() => {
                Cookies.remove("token");
                Cookies.remove("user_id");
                router.push("/login");
              }}
            >
              <LogOut size={16} />
              <span>Logout</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}
