"use client";
import React, { useState } from "react";
import { scrape } from "@/app/apis";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { toast } from "sonner";
import { Card } from "@/components/ui/card";
import { Link } from "lucide-react";

const UrlScrapeTab = ({ chatbotId }) => {
  const [url, setUrl] = useState("");
  const [isScraping, setIsScraping] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!url) {
      toast.error("Please enter a URL");
      return;
    }

    try {
      setIsScraping(true);

      await scrape(url,chatbotId);
      toast.success("URL scraped successfully");
      setUrl("");
    } catch (err) {
      toast.error(err.message || "Failed to scrape URL");
    } finally {
      setIsScraping(false);
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <Link className="h-5 w-5 text-blue-600" />
          <h3 className="text-lg font-semibold">Scrape URL</h3>
        </div>
        <p className="text-sm text-gray-500">
          Enter a URL to scrape its content and add it to your chatbot's knowledge base.
        </p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url">URL</Label>
            <Input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
            />
          </div>
          <Button
            type="submit"
            className="w-full"
            disabled={isScraping || !url}
          >
            {isScraping ? "Scraping..." : "Scrape URL"}
          </Button>
        </form>
      </div>
    </Card>
  );
};

export default UrlScrapeTab; 