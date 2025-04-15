"use client";
import React, { useState } from "react";
import { processSitemap } from "@/app/apis";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Network } from "lucide-react";

const SitemapTab = ({ chatbotId }) => {
  const [sitemapUrl, setSitemapUrl] = useState("");
  const [limit, setLimit] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = async (e) => {
    console.log("sitemapUrl",sitemapUrl);
    console.log("limit",limit);
    console.log("chatbotId",chatbotId);
    
    e.preventDefault();
    if (!sitemapUrl) {
      toast.error("Please enter a sitemap URL");
      return;
    }

    try {
      setIsProcessing(true);
      await processSitemap(sitemapUrl, chatbotId,limit);
      toast.success("Sitemap processed successfully");
      setSitemapUrl("");
      setLimit("");
    } catch (err) {
      toast.error(err.message || "Failed to process sitemap");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Network className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Process Sitemap</h3>
        </div>
        <p className="text-sm text-gray-500">
          Enter a sitemap URL to process its pages and add them to your chatbot's knowledge base.
          You can optionally limit the number of pages to process.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="sitemap">Sitemap URL</Label>
            <Input
              id="sitemap"
              type="url"
              value={sitemapUrl}
              onChange={(e) => setSitemapUrl(e.target.value)}
              placeholder="https://example.com/sitemap.xml"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="limit">Page Limit (Optional)</Label>
            <Input
              id="limit"
              type="number"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              placeholder="Enter number of pages to process"
              min="1"
            />
            <p className="text-xs text-gray-500">
              Leave empty to process all pages
            </p>
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={isProcessing || !sitemapUrl}
          >
            {isProcessing ? "Processing..." : "Process Sitemap"}
          </Button>
        </form>
      </div>
    </Card>
  );
};

export default SitemapTab; 