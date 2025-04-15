"use client";
import React, { useState } from "react";
import { createChatbot } from "@/app/apis";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";

const CreateChatbotForm = ({ onSuccess }) => {
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      await createChatbot({ name });
      toast.success("Chatbot created successfully");
      setName("");
      onSuccess?.();
    } catch (err) {
      toast.error(err.message || "Failed to create chatbot");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="name">Chatbot Name</Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter chatbot name"
          required
        />
      </div>

      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "Creating..." : "Create Chatbot"}
      </Button>
    </form>
  );
};

export default CreateChatbotForm;
