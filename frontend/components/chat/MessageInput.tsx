"use client";

import { Send, Sparkles } from "lucide-react"; // Import Loader2 if needed for loading state, but passed as prop
import { useState, useRef, KeyboardEvent } from "react";
import { cn } from "@/lib/utils";

interface MessageInputProps {
    onSendMessage: (content: string) => void;
    isLoading?: boolean;
}

export function MessageInput({ onSendMessage, isLoading }: MessageInputProps) {
    const [content, setContent] = useState("");
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const handleSend = () => {
        if (content.trim() && !isLoading) {
            onSendMessage(content);
            setContent("");
            // Reset height
            if (textareaRef.current) {
                textareaRef.current.style.height = "auto";
            }
        }
    };

    const handleKeyDown = (e: KeyboardEvent) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const adjustHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = "auto";
            textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
        }
    };

    return (
        <div className="p-4 border-t border-white/10 bg-background/50 backdrop-blur-md">
            <div className="max-w-4xl mx-auto relative flex items-end gap-2 p-2 rounded-3xl border border-white/10 bg-white/5 shadow-inner focus-within:ring-1 focus-within:ring-primary/50 transition-all">

                {/* Magic/Tools Trigger (Future expanion) */}
                <button className="p-3 rounded-full hover:bg-white/10 text-muted-foreground transition-colors" disabled={isLoading}>
                    <Sparkles size={20} />
                </button>

                <textarea
                    ref={textareaRef}
                    value={content}
                    onChange={(e) => {
                        setContent(e.target.value);
                        adjustHeight();
                    }}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    className="flex-1 max-h-[200px] min-h-[24px] bg-transparent border-none focus:ring-0 resize-none py-3 text-sm placeholder:text-muted-foreground/50 scrollbar-none"
                    rows={1}
                    disabled={isLoading}
                />

                <button
                    onClick={handleSend}
                    disabled={!content.trim() || isLoading}
                    className={cn(
                        "p-3 rounded-full transition-all duration-300 shadow-lg",
                        content.trim() && !isLoading
                            ? "bg-primary text-primary-foreground hover:scale-105 hover:shadow-primary/25"
                            : "bg-muted text-muted-foreground opacity-50 cursor-not-allowed"
                    )}
                >
                    <Send size={18} />
                </button>
            </div>
            <div className="text-center mt-2">
                <p className="text-[10px] text-muted-foreground/60">
                    Unified GenAI Platform can make mistakes. Consider checking important information.
                </p>
            </div>
        </div>
    );
}
