"use client";
import React, { useState, useRef } from "react";
import { uploadDocument } from "@/app/apis";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Upload } from "lucide-react";

const UploadDocumentTab = ({ chatbotId }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    try {
      setIsUploading(true);
      const formData = new FormData();
      formData.append("file", file);

      await uploadDocument(chatbotId,formData);
      toast.success("Document uploaded successfully");
      setFile(null);
      // Reset the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    } catch (err) {
      toast.error(err.message || "Failed to upload document");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Upload className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Upload Document</h3>
        </div>
        <p className="text-sm text-gray-500">
          Upload a document to add to your chatbot's knowledge base. Supported formats: PDF, DOCX, TXT.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="file">Document</Label>
            <Input
              id="file"
              type="file"
              ref={fileInputRef}
              onChange={(e) => setFile(e.target.files[0])}
              accept=".pdf,.docx,.txt"
              required
            />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={isUploading || !file}
          >
            {isUploading ? "Uploading..." : "Upload Document"}
          </Button>
        </form>
      </div>
    </Card>
  );
};

export default UploadDocumentTab; 