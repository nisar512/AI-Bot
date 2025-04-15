"use client";
import React, { useState } from "react";
import CreateChatbotForm from "@/app/components/CreateChatbotForm";
import ChatbotsTable from "@/app/components/ChatbotsTable";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Plus } from "lucide-react";

const DashboardPage = () => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSuccess = () => {
    setIsDialogOpen(false);
    setRefreshTrigger(prev => prev + 1); // Increment to trigger refresh
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <Card className="p-6 bg-white shadow-lg rounded-xl border-0">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Your Chatbots</h2>
              <div className="text-sm text-gray-500">
                Manage your AI assistants
              </div>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Bot
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Create New Bot</DialogTitle>
                </DialogHeader>
                <CreateChatbotForm onSuccess={handleSuccess} />
              </DialogContent>
            </Dialog>
          </div>
          <ChatbotsTable refreshTrigger={refreshTrigger} />
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage; 