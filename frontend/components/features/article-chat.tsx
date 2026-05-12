"use client";

import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Send, MessageSquare, Loader2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import TextareaAutosize from "react-textarea-autosize";

import { apiFetch, type ChatMessage } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const STARTER_QUESTIONS = [
  "What is this article about?",
  "What are the key takeaways?",
  "Are there any terms I should understand?",
];

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2.5 text-sm",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted text-foreground"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm dark:prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-muted rounded-2xl px-4 py-3">
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce [animation-delay:-0.3s]" />
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce [animation-delay:-0.15s]" />
          <div className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-bounce" />
        </div>
      </div>
    </div>
  );
}

function EmptyState({ onSelect }: { onSelect: (q: string) => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="rounded-full bg-muted p-4 mb-4">
        <MessageSquare className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="font-semibold text-lg mb-1">Ask AI about this article</h3>
      <p className="text-sm text-muted-foreground mb-6 max-w-sm">
        Ask questions about the article content — meanings of terms,
        clarifications, implications, and more.
      </p>
      <div className="flex flex-col gap-2 w-full max-w-sm">
        {STARTER_QUESTIONS.map((q) => (
          <button
            key={q}
            onClick={() => onSelect(q)}
            className="text-left text-sm px-4 py-2.5 rounded-lg border border-border hover:bg-muted transition-colors"
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

export function ArticleChat({ articleId }: { articleId: number }) {
  const [input, setInput] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  const { data: messages = [], isLoading } = useQuery({
    queryKey: ["chat", articleId],
    queryFn: () => apiFetch<ChatMessage[]>(`/chat/${articleId}/`),
  });

  const [optimisticMessages, setOptimisticMessages] = useState<ChatMessage[]>(
    []
  );

  const displayMessages = [...messages, ...optimisticMessages];

  const sendMutation = useMutation({
    mutationFn: (message: string) =>
      apiFetch<ChatMessage>(`/chat/${articleId}/`, {
        method: "POST",
        body: JSON.stringify({ message }),
      }),
    onMutate: (message) => {
      const optimistic: ChatMessage = {
        id: -Date.now(),
        role: "user",
        content: message,
        created_at: new Date().toISOString(),
      };
      setOptimisticMessages((prev) => [...prev, optimistic]);
    },
    onSuccess: () => {
      setOptimisticMessages([]);
      queryClient.invalidateQueries({ queryKey: ["chat", articleId] });
    },
    onError: () => {
      setOptimisticMessages([]);
    },
  });

  // Auto-scroll when messages change or when sending
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [displayMessages.length, sendMutation.isPending]);

  const handleSend = (text?: string) => {
    const message = (text || input).trim();
    if (!message || sendMutation.isPending) return;
    setInput("");
    sendMutation.mutate(message);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[500px]">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-1 space-y-3">
        {displayMessages.length === 0 && !sendMutation.isPending ? (
          <EmptyState onSelect={(q) => handleSend(q)} />
        ) : (
          <>
            {displayMessages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {sendMutation.isPending && <TypingIndicator />}
          </>
        )}
        <div ref={scrollRef} />
      </div>

      {/* Input area */}
      <div className="border-t pt-3 mt-3">
        {sendMutation.isError && (
          <p className="text-sm text-destructive mb-2">
            Failed to send message. Please try again.
          </p>
        )}
        <div className="flex items-end gap-2">
          <TextareaAutosize
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about this article..."
            minRows={1}
            maxRows={4}
            className="flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            disabled={sendMutation.isPending}
          />
          <Button
            size="icon"
            onClick={() => handleSend()}
            disabled={!input.trim() || sendMutation.isPending}
          >
            {sendMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
