"use client";

import { motion } from "framer-motion";
import { ArrowUpRight, Phone, Mail, Calendar, MoreVertical } from "lucide-react";
import { ChatInterface } from "@/components/chat/ChatInterface";

// Mock leads data
const mockLeads = [
    { id: "1", name: "Sarah Chen", company: "TechCorp", status: "hot", value: "$45,000", lastContact: "2 hours ago" },
    { id: "2", name: "Michael Ross", company: "DataFlow Inc", status: "warm", value: "$28,000", lastContact: "1 day ago" },
    { id: "3", name: "Emily Watson", company: "CloudNine", status: "hot", value: "$62,000", lastContact: "30 mins ago" },
    { id: "4", name: "James Miller", company: "StartupXYZ", status: "cold", value: "$15,000", lastContact: "5 days ago" },
];

const statusColors = {
    hot: "bg-red-500/10 text-red-400 border-red-500/20",
    warm: "bg-orange-500/10 text-orange-400 border-orange-500/20",
    cold: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export default function SalesPage() {
    return (
        <div>
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Sales & Leads</h1>
                    <p className="text-muted-foreground">Track and manage your sales pipeline with AI assistance.</p>
                </div>
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-colors"
                >
                    <ArrowUpRight size={18} />
                    Add Lead
                </motion.button>
            </div>

            {/* Main Layout Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Stats & Leads (Takes 2/3 width) */}
                <div className="lg:col-span-2 space-y-8">
                    {/* Pipeline Stats */}
                    <div className="grid grid-cols-4 gap-4">
                        {[
                            { label: "Total Leads", value: "156", trend: "+12 this week" },
                            { label: "Hot Leads", value: "23", trend: "Ready to close" },
                            { label: "Conversion Rate", value: "34%", trend: "+5% vs last month" },
                            { label: "Avg Deal Size", value: "$38K", trend: "Healthy pipeline" },
                        ].map((stat, i) => (
                            <motion.div
                                key={stat.label}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="p-4 rounded-xl border border-white/5 bg-white/5"
                            >
                                <p className="text-2xl font-bold text-white mb-1">{stat.value}</p>
                                <p className="text-sm text-muted-foreground">{stat.label}</p>
                                <p className="text-xs text-emerald-400 mt-2">{stat.trend}</p>
                            </motion.div>
                        ))}
                    </div>

                    {/* Leads Table */}
                    <div className="rounded-2xl border border-white/5 bg-white/5 overflow-hidden">
                        <div className="p-4 border-b border-white/5">
                            <h2 className="font-semibold">Recent Leads</h2>
                        </div>
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-sm text-muted-foreground border-b border-white/5">
                                    <th className="p-4 font-medium">Contact</th>
                                    <th className="p-4 font-medium">Status</th>
                                    <th className="p-4 font-medium">Value</th>
                                    <th className="p-4 font-medium">Last Contact</th>
                                    <th className="p-4 font-medium">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {mockLeads.map((lead, index) => (
                                    <motion.tr
                                        key={lead.id}
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: index * 0.05 }}
                                        className="border-b border-white/5 hover:bg-white/5 transition-colors"
                                    >
                                        <td className="p-4">
                                            <div>
                                                <p className="font-medium text-white">{lead.name}</p>
                                                <p className="text-sm text-muted-foreground">{lead.company}</p>
                                            </div>
                                        </td>
                                        <td className="p-4">
                                            <span className={`px-2.5 py-1 rounded-full text-xs font-medium border capitalize ${statusColors[lead.status as keyof typeof statusColors]}`}>
                                                {lead.status}
                                            </span>
                                        </td>
                                        <td className="p-4 font-medium text-white">{lead.value}</td>
                                        <td className="p-4 text-sm text-muted-foreground">{lead.lastContact}</td>
                                        <td className="p-4">
                                            <div className="flex items-center gap-2">
                                                <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
                                                    <Phone size={16} className="text-muted-foreground" />
                                                </button>
                                                <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
                                                    <Mail size={16} className="text-muted-foreground" />
                                                </button>
                                                <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
                                                    <Calendar size={16} className="text-muted-foreground" />
                                                </button>
                                                <button className="p-2 rounded-lg hover:bg-white/10 transition-colors">
                                                    <MoreVertical size={16} className="text-muted-foreground" />
                                                </button>
                                            </div>
                                        </td>
                                    </motion.tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Right Column: AI Sales Agent */}
                <div className="lg:col-span-1">
                    <div className="sticky top-8">
                        <div className="mb-4">
                            <h2 className="text-lg font-semibold flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                AI Sales Assistant
                            </h2>
                            <p className="text-sm text-muted-foreground">Ask about any lead or deal status.</p>
                        </div>
                        <ChatInterface
                            initialMessage="Hello! I'm your Sales Agent. How can I help you close more deals today?"
                            agentName="Sales Agent"
                        />
                    </div>
                </div>
            </div>
        </div>
    );
}
