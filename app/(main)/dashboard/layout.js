import ChatSidebar from "@/components/sidebar/sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";
const layout = ({ children }) => {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-screen bg-background">
        <ChatSidebar />
        <div className="flex-1">
          <div className="w-full h-screen overflow-y-auto">{children}</div>
        </div>
      </div>
    </SidebarProvider>
  );
};

export default layout;
