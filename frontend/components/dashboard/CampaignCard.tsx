"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { Calendar, Eye, Heart, MessageCircle, MoreVertical } from "lucide-react";

interface Campaign {
    id: string;
    name: string;
    status: "draft" | "scheduled" | "active" | "paused" | "completed";
    platform: "instagram" | "twitter" | "linkedin" | "email";
    scheduledDate?: string;
    metrics?: {
        impressions: number;
        likes: number;
        comments: number;
    };
}

interface CampaignCardProps {
    campaign: Campaign;
    index?: number;
}

const statusColors = {
    draft: "bg-gray-500/10 text-gray-400 border-gray-500/20",
    scheduled: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    active: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    paused: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
    completed: "bg-purple-500/10 text-purple-400 border-purple-500/20",
};

const platformIcons = {
    instagram: "📸",
    twitter: "🐦",
    linkedin: "💼",
    email: "📧",
};

export function CampaignCard({ campaign, index = 0 }: CampaignCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.08 }}
            className="p-5 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-md hover:bg-white/10 transition-all group cursor-pointer"
        >
            <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">{platformIcons[campaign.platform]}</span>
                    <div>
                        <h3 className="font-semibold text-white group-hover:text-primary transition-colors">
                            {campaign.name}
                        </h3>
                        <p className="text-xs text-muted-foreground capitalize">{campaign.platform}</p>
                    </div>
                </div>
                <button className="p-2 rounded-lg hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100">
                    <MoreVertical size={16} className="text-muted-foreground" />
                </button>
            </div>

            <div className="flex items-center gap-2 mb-4">
                <span className={cn("px-2.5 py-1 rounded-full text-xs font-medium border capitalize", statusColors[campaign.status])}>
                    {campaign.status}
                </span>
                {campaign.scheduledDate && (
                    <span className="flex items-center gap-1 text-xs text-muted-foreground">
                        <Calendar size={12} />
                        {campaign.scheduledDate}
                    </span>
                )}
            </div>

            {campaign.metrics && (
                <div className="flex items-center gap-4 pt-4 border-t border-white/5">
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                        <Eye size={14} />
                        <span>{campaign.metrics.impressions.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                        <Heart size={14} />
                        <span>{campaign.metrics.likes.toLocaleString()}</span>
                    </div>
                    <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
                        <MessageCircle size={14} />
                        <span>{campaign.metrics.comments.toLocaleString()}</span>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
