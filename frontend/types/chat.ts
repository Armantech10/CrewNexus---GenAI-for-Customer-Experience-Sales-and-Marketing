export type Role = "user" | "assistant" | "system";

export type Message = {
    id: string;
    role: Role;
    content: string;
    timestamp: Date;
    intent?: string;
    sentiment?: string;
    agentName?: string;
};

export type ChatSession = {
    id: string;
    title: string;
    lastMessage: Message;
    updatedAt: Date;
};
