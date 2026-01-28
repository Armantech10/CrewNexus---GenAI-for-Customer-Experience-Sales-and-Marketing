"use client";

import { motion } from "framer-motion";
import { Search, Filter, CheckCircle2, Clock, AlertCircle, MessageSquare } from "lucide-react";
import { ChatInterface } from "@/components/chat/ChatInterface";

// Mock tickets
const mockTickets = [
    { id: "T-1234", subject: "Login issues on mobile app", customer: "john@example.com", priority: "high", status: "open", created: "2h ago" },
    { id: "T-1235", subject: "Billing question about subscription", customer: "sarah@techcorp.io", priority: "medium", status: "in_progress", created: "5h ago" },
    { id: "T-1236", subject: "Feature request: Dark mode", customer: "mike@startup.co", priority: "low", status: "resolved", created: "1d ago" },
    { id: "T-1237", subject: "API rate limit exceeded", customer: "dev@enterprise.com", priority: "high", status: "open", created: "30m ago" },
];

const priorityColors = {
    high: "bg-red-500/10 text-red-400",
    medium: "bg-orange-500/10 text-orange-400",
    low: "bg-blue-500/10 text-blue-400",
};

const statusIcons = {
    open: <AlertCircle size={14} className="text-red-400" />,
    in_progress: <Clock size={14} className="text-orange-400" />,
    resolved: <CheckCircle2 size={14} className="text-emerald-400" />,
};

export default function SupportPage() {
    return (
        <div>
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Support Tickets</h1>
                    <p className="text-muted-foreground">AI-assisted customer support management.</p>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-4 gap-4 mb-8">
                {[
                    { icon: <AlertCircle className="text-red-400" />, label: "Open", value: "12" },
                    { icon: <Clock className="text-orange-400" />, label: "In Progress", value: "8" },
                    { icon: <CheckCircle2 className="text-emerald-400" />, label: "Resolved Today", value: "24" },
                    { icon: <MessageSquare className="text-blue-400" />, label: "Avg Response", value: "2.4h" },
                ].map((stat, i) => (
                    <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-4 rounded-xl border border-white/5 bg-white/5 flex items-center gap-4"
                    >
                        <div className="p-3 rounded-xl bg-white/5">{stat.icon}</div>
                        <div>
                            <p className="text-2xl font-bold text-white">{stat.value}</p>
                            <p className="text-sm text-muted-foreground">{stat.label}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Search & Filter */}
            <div className="flex gap-4 mb-6">
                <div className="flex-1 relative">
                    <Search size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <input
                        type="text"
                        placeholder="Search tickets..."
                        className="w-full pl-12 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50"
                    />
                </div>
                <button className="flex items-center gap-2 px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl hover:bg-white/10 transition-colors">
                    <Filter size={18} />
                    Filter
                </button>
            </div>

            {/* Tickets List */}
            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Tickets List */}
                <div className="lg:col-span-2 space-y-3">
                    <h2 className="text-lg font-semibold mb-4">Active Tickets</h2>
                    {mockTickets.map((ticket, index) => (
                        <motion.div
                            key={ticket.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.08 }}
                            className="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-colors cursor-pointer group"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex items-start gap-4">
                                    <div className="mt-1">
                                        {statusIcons[ticket.status as keyof typeof statusIcons]}
                                    </div>
                                    <div>
                                        <div className="flex items-center gap-2 mb-1">
                                            <span className="text-xs text-muted-foreground font-mono">{ticket.id}</span>
                                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${priorityColors[ticket.priority as keyof typeof priorityColors]}`}>
                                                {ticket.priority}
                                            </span>
                                        </div>
                                        <h3 className="font-medium text-white group-hover:text-primary transition-colors">
                                            {ticket.subject}
                                        </h3>
                                        <p className="text-sm text-muted-foreground mt-1">{ticket.customer}</p>
                                    </div>
                                </div>
                                <span className="text-xs text-muted-foreground">{ticket.created}</span>
                            </div>
                        </motion.div>
                    ))}
                </div>

                {/* AI Support Agent */}
                <div className="lg:col-span-1">
                    <div className="sticky top-8">
                        <div className="mb-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                                Support Genie
                            </h2>
                            <p className="text-sm text-muted-foreground">I can answer questions from the knowledge base.</p>
                        </div>
                        <ChatInterface
                            initialMessage="Hello! I'm SupportGenie. How can I assist you with your technical issues today?"
                            agentName="Support Genie"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
