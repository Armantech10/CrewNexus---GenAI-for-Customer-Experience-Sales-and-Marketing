"use client";

import { useState, useEffect } from "react";
import { Message } from "@/types/chat";
import { MessageList } from "./MessageList";
import { MessageInput } from "./MessageInput";
import { nanoid } from "nanoid";

interface ChatInterfaceProps {
    initialMessage?: string;
    agentName?: string;
    welcomeMessage?: string;
    endpoint?: string;
    onResponse?: (response: any) => void;
}

export function ChatInterface({
    initialMessage,
    welcomeMessage,
    agentName = "Unified Agent",
    endpoint = "/api/v1/chat",
    onResponse
}: ChatInterfaceProps) {
    const [mounted, setMounted] = useState(false);
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "welcome-1",
            role: "assistant",
            content: welcomeMessage || initialMessage || "Hello! How can I help you?",
            timestamp: new Date(),
            agentName: agentName
        }
    ]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        setMounted(true);
    }, []);

    if (!mounted) return null;

    const sendMessage = async (content: string) => {
        // 1. Add user message
        const userMsg: Message = {
            id: nanoid(),
            role: "user",
            content,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, userMsg]);
        setIsLoading(true);

        try {
            // 2. Call API (Dynamic Endpoint)
            // Handle both relative (starts with /) and absolute URLs logic simply
            const apiUrl = endpoint.startsWith("http") ? endpoint : `http://localhost:8000/api/v1${endpoint.replace("/api/v1", "")}`;

            const response = await fetch(apiUrl, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: content,
                    session_id: "demo-session",
                    user_id: "demo-user"
                })
            });

            if (!response.ok) throw new Error("API call failed");

            const data = await response.json();

            // Callback for external handling (e.g. updating terminal)
            if (onResponse) onResponse(data);

            const aiMsg: Message = {
                id: nanoid(),
                role: "assistant",
                content: data.response,
                timestamp: new Date(),
                agentName: data.agent_used || agentName,
                intent: data.intent,
                sentiment: data.sentiment
            };

            setMessages((prev) => [...prev, aiMsg]);
        } catch (error) {
            console.error("Failed to send message", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[600px] w-full bg-background relative overflow-hidden rounded-2xl border border-white/10 shadow-2xl">
            {/* Background Gradients */}
            <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-primary/5 rounded-full blur-[100px] pointer-events-none" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-secondary/5 rounded-full blur-[100px] pointer-events-none" />

            {/* Header */}
            <header className="h-14 border-b border-white/10 bg-background/50 backdrop-blur-md flex items-center px-6 z-10 justify-between">
                <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_10px_#22c55e]" />
                    <span className="font-semibold text-sm tracking-wide">CrewNexus</span>
                </div>
            </header>

            {/* Messages */}
            <MessageList messages={messages} isLoading={isLoading} />

            {/* Input */}
            <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>
    );
}
