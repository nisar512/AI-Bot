"use client";
import React, { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import UploadDocumentTab from "@/app/components/knowledge/UploadDocumentTab";
import UrlScrapeTab from "@/app/components/knowledge/UrlScrapeTab";
import SitemapTab from "@/app/components/knowledge/SitemapTab";
import { Card } from "@/components/ui/card";
import { useParams } from "next/navigation";

const KnowledgePage = () => {
  const params = useParams();
  const chatbotId = params.id;
  const [activeTab, setActiveTab] = useState("document");

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <div className="container mx-auto px-4 py-8">
        <Card className="p-6 bg-white shadow-lg rounded-xl border-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800">Add Knowledge</h2>
            <p className="text-sm text-gray-500">
              Choose a method to add content to your chatbot's knowledge base
            </p>
          </div>

          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="document">Upload Document</TabsTrigger>
              <TabsTrigger value="url">Scrape URL</TabsTrigger>
              <TabsTrigger value="sitemap">Process Sitemap</TabsTrigger>
            </TabsList>

            <TabsContent value="document" className="mt-6">
              <UploadDocumentTab chatbotId={chatbotId} />
            </TabsContent>

            <TabsContent value="url" className="mt-6">
              <UrlScrapeTab chatbotId={chatbotId} />
            </TabsContent>

            <TabsContent value="sitemap" className="mt-6">
              <SitemapTab chatbotId={chatbotId} />
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
};

export default KnowledgePage;
