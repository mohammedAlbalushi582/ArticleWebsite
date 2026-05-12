"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { Loader2, Link as LinkIcon, FileText } from "lucide-react";

import { apiFetch, type Article } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

const urlSchema = z.object({
  url: z.string().url("Enter a valid URL"),
});

const textSchema = z.object({
  text: z.string().min(50, "Text must be at least 50 characters"),
});

export default function NewArticlePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);

  const urlForm = useForm<z.infer<typeof urlSchema>>({
    resolver: zodResolver(urlSchema),
  });

  const textForm = useForm<z.infer<typeof textSchema>>({
    resolver: zodResolver(textSchema),
  });

  async function submitAnalysis(body: { url?: string; text?: string }) {
    setLoading(true);
    try {
      const article = await apiFetch<Article>("/articles/analyze/", {
        method: "POST",
        body: JSON.stringify(body),
      });
      toast.success("Article analyzed successfully");
      router.push(`/articles/${article.id}`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-2">Analyze an Article</h1>
      <p className="text-muted-foreground mb-8">
        Submit a URL or paste article text to get an AI-generated summary and key points.
      </p>

      <Card>
        <CardHeader>
          <CardTitle>Submit Article</CardTitle>
          <CardDescription>Choose how you want to provide the article content.</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="url">
            <TabsList className="mb-6">
              <TabsTrigger value="url" className="gap-2">
                <LinkIcon className="h-4 w-4" />
                From URL
              </TabsTrigger>
              <TabsTrigger value="text" className="gap-2">
                <FileText className="h-4 w-4" />
                Paste Text
              </TabsTrigger>
            </TabsList>

            <TabsContent value="url">
              <form
                onSubmit={urlForm.handleSubmit((data) => submitAnalysis({ url: data.url }))}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label htmlFor="url">Article URL</Label>
                  <Input
                    id="url"
                    placeholder="https://example.com/article"
                    {...urlForm.register("url")}
                  />
                  {urlForm.formState.errors.url && (
                    <p className="text-sm text-destructive">
                      {urlForm.formState.errors.url.message}
                    </p>
                  )}
                </div>
                <Button type="submit" disabled={loading}>
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Analyze Article
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="text">
              <form
                onSubmit={textForm.handleSubmit((data) => submitAnalysis({ text: data.text }))}
                className="space-y-4"
              >
                <div className="space-y-2">
                  <Label htmlFor="text">Article Text</Label>
                  <Textarea
                    id="text"
                    placeholder="Paste the article content here..."
                    rows={10}
                    {...textForm.register("text")}
                  />
                  {textForm.formState.errors.text && (
                    <p className="text-sm text-destructive">
                      {textForm.formState.errors.text.message}
                    </p>
                  )}
                </div>
                <Button type="submit" disabled={loading}>
                  {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Analyze Article
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
