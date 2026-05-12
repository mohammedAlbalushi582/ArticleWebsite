"use client";

import { useRef, useState, type ReactNode } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Highlighter, MessageSquare, Trash2, X } from "lucide-react";
import { toast } from "sonner";

import { apiFetch, type Highlight } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";

const COLORS = [
  { name: "yellow", bg: "bg-yellow-200/70 dark:bg-yellow-500/30" },
  { name: "green", bg: "bg-green-200/70 dark:bg-green-500/30" },
  { name: "blue", bg: "bg-blue-200/70 dark:bg-blue-500/30" },
  { name: "pink", bg: "bg-pink-200/70 dark:bg-pink-500/30" },
] as const;

type ColorName = (typeof COLORS)[number]["name"];

function getColorClass(color: string) {
  return COLORS.find((c) => c.name === color)?.bg || COLORS[0].bg;
}

function renderHighlightedText(text: string, highlights: Highlight[]): ReactNode[] {
  if (!highlights.length) return [text];

  type Span = { start: number; end: number; highlight: Highlight };
  const spans: Span[] = [];

  for (const h of highlights) {
    let searchFrom = 0;
    while (true) {
      const idx = text.indexOf(h.text, searchFrom);
      if (idx === -1) break;
      spans.push({ start: idx, end: idx + h.text.length, highlight: h });
      searchFrom = idx + h.text.length;
    }
  }

  if (!spans.length) return [text];

  spans.sort((a, b) => a.start - b.start || b.end - a.end);

  const merged: Span[] = [];
  for (const span of spans) {
    if (!merged.length || span.start >= merged[merged.length - 1].end) {
      merged.push(span);
    }
  }

  const parts: ReactNode[] = [];
  let cursor = 0;

  for (const span of merged) {
    if (cursor < span.start) {
      parts.push(text.slice(cursor, span.start));
    }
    parts.push(
      <mark
        key={`${span.highlight.id}-${span.start}`}
        className={`${getColorClass(span.highlight.color)} rounded-sm px-0.5 cursor-help`}
        title={span.highlight.note || undefined}
      >
        {text.slice(span.start, span.end)}
        {span.highlight.note && (
          <MessageSquare className="inline h-3 w-3 ml-0.5 opacity-50" />
        )}
      </mark>
    );
    cursor = span.end;
  }

  if (cursor < text.length) {
    parts.push(text.slice(cursor));
  }

  return parts;
}

export function HighlightableText({
  articleId,
  text,
  source,
}: {
  articleId: number;
  text: string;
  source: string;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedText, setSelectedText] = useState("");
  const [note, setNote] = useState("");
  const [chosenColor, setChosenColor] = useState<ColorName | null>(null);
  const queryClient = useQueryClient();

  const { data: highlights = [] } = useQuery({
    queryKey: ["highlights", articleId],
    queryFn: () => apiFetch<Highlight[]>(`/notes/${articleId}/`),
  });

  const sourceHighlights = highlights.filter((h) => h.source === source);

  const createMutation = useMutation({
    mutationFn: (data: { text: string; color: string; note: string; source: string }) =>
      apiFetch<Highlight>(`/notes/${articleId}/`, {
        method: "POST",
        body: JSON.stringify({ ...data, article: articleId }),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["highlights", articleId] });
      resetSelection();
    },
    onError: (err) =>
      toast.error(err instanceof Error ? err.message : "Failed to save highlight"),
  });

  function resetSelection() {
    setSelectedText("");
    setNote("");
    setChosenColor(null);
    window.getSelection()?.removeAllRanges();
  }

  function handleMouseUp() {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    const selected = selection.toString().trim();
    if (selected && containerRef.current?.contains(selection.anchorNode)) {
      setSelectedText(selected);
      setChosenColor(null);
      setNote("");
    }
  }

  function handlePickColor(color: ColorName) {
    setChosenColor(color);
  }

  function handleSave() {
    if (!selectedText || !chosenColor) return;
    createMutation.mutate({ text: selectedText, color: chosenColor, note, source });
  }

  const rendered = renderHighlightedText(text, sourceHighlights);

  return (
    <div>
      <div
        ref={containerRef}
        onMouseUp={handleMouseUp}
        className="leading-relaxed whitespace-pre-wrap select-text"
      >
        {rendered}
      </div>

      {selectedText && (
        <div className="mt-3 rounded-lg border bg-muted/50 animate-in fade-in slide-in-from-bottom-2">
          <div className="flex items-center gap-2 p-3">
            <Highlighter className="h-4 w-4 text-muted-foreground shrink-0" />
            <p className="text-xs text-muted-foreground truncate flex-1">
              &ldquo;{selectedText.length > 60 ? selectedText.slice(0, 60) + "..." : selectedText}&rdquo;
            </p>
            <button
              onClick={resetSelection}
              className="text-muted-foreground hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          </div>

          <div className="px-3 pb-3 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Color:</span>
              {COLORS.map((c) => (
                <button
                  key={c.name}
                  disabled={createMutation.isPending}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handlePickColor(c.name)}
                  className={`h-7 w-7 rounded-full border-2 transition-all ${
                    chosenColor === c.name
                      ? "border-foreground scale-110"
                      : "border-transparent hover:border-foreground/40"
                  } ${c.bg}`}
                  title={c.name}
                />
              ))}
            </div>
            <Input
              placeholder="Add a note (optional)..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") handleSave();
              }}
              className="text-sm"
            />
            <div className="flex gap-2">
              <Button
                size="sm"
                onClick={handleSave}
                disabled={!chosenColor || createMutation.isPending}
              >
                {createMutation.isPending ? "Saving..." : "Save highlight"}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={resetSelection}
              >
                Cancel
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export function HighlightsSidebar({ articleId }: { articleId: number }) {
  const queryClient = useQueryClient();

  const { data: highlights = [] } = useQuery({
    queryKey: ["highlights", articleId],
    queryFn: () => apiFetch<Highlight[]>(`/notes/${articleId}/`),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      apiFetch(`/notes/${articleId}/${id}/`, { method: "DELETE" }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["highlights", articleId] });
    },
    onError: () => toast.error("Failed to delete highlight"),
  });

  if (!highlights.length) {
    return (
      <p className="text-sm text-muted-foreground py-4">
        No highlights yet. Select text in any tab and click a color to highlight it.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {highlights.map((h) => (
        <div
          key={h.id}
          className={`flex items-start gap-3 rounded-lg border p-3 ${getColorClass(h.color)}`}
        >
          <div className="flex-1 min-w-0">
            <p className="text-sm leading-relaxed font-medium">
              &ldquo;{h.text}&rdquo;
            </p>
            {h.note && (
              <p className="text-sm text-muted-foreground mt-1 flex items-start gap-1.5">
                <MessageSquare className="h-3.5 w-3.5 mt-0.5 shrink-0" />
                {h.note}
              </p>
            )}
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="outline" className="text-xs">
                {h.source}
              </Badge>
              <span className="text-xs text-muted-foreground">
                {new Date(h.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
          {h.is_own !== false && (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 shrink-0"
              onClick={() => deleteMutation.mutate(h.id)}
              disabled={deleteMutation.isPending}
            >
              <Trash2 className="h-3 w-3" />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
