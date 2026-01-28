"use client";

import { Message } from "@/types/chat";
import { ChatBubble } from "./ChatBubble";
import { useRef, useEffect } from "react";

interface MessageListProps {
    messages: Message[];
    isLoading?: boolean;
}

export function MessageList({ messages, isLoading }: MessageListProps) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, isLoading]);

    return (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-muted scrollbar-track-transparent">
            {messages.map((msg) => (
                <ChatBubble key={msg.id} message={msg} />
            ))}

            {isLoading && (
                <div className="flex justify-start mb-4">
                    <div className="flex max-w-[80%] gap-3 flex-row">
                        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center border border-white/10">
                            <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" />
                        </div>
                        <div className="p-4 rounded-2xl bg-card/50 glass-dark rounded-tl-sm flex items-center gap-1">
                            <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce [animation-delay:-0.3s]" />
                            <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce [animation-delay:-0.15s]" />
                            <span className="w-2 h-2 bg-foreground/50 rounded-full animate-bounce" />
                        </div>
                    </div>
                </div>
            )}
            <div ref={bottomRef} />
        </div>
    );
}
