"use client";

import { cn } from "@/lib/utils";
import { Message } from "@/types/chat";
import { motion } from "framer-motion";
import { Bot, User } from "lucide-react";
import { useState, useEffect } from "react";

interface ChatBubbleProps {
    message: Message;
}

export function ChatBubble({ message }: ChatBubbleProps) {
    const isUser = message.role === "user";
    const [timeString, setTimeString] = useState<string>("");

    useEffect(() => {
        // eslint-disable-next-line
        setTimeString(new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }));
    }, [message.timestamp]);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={cn(
                "flex w-full mb-4",
                isUser ? "justify-end" : "justify-start"
            )}
        >
            <div className={cn("flex max-w-[80%] gap-3", isUser ? "flex-row-reverse" : "flex-row")}>
                {/* Avatar */}
                <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0 border border-white/10 shadow-lg",
                    isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
                )}>
                    {isUser ? <User size={16} /> : <Bot size={16} />}
                </div>

                {/* Bubble */}
                <div className={cn(
                    "p-4 rounded-2xl shadow-sm backdrop-blur-md border border-white/5",
                    isUser
                        ? "bg-primary/90 text-primary-foreground rounded-tr-sm"
                        : "bg-card/80 text-foreground rounded-tl-sm glass-dark"
                )}>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

                    {/* Metadata (Agent Name / Timestamp) */}
                    <div className="mt-1 flex items-center justify-between gap-4 opacity-70">
                        <span className="text-[10px] uppercase tracking-wider font-semibold">
                            {isUser ? "You" : message.agentName || "AI Assistant"}
                        </span>
                        <span className="text-[10px] min-h-[1.2em]">
                            {timeString}
                        </span>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
