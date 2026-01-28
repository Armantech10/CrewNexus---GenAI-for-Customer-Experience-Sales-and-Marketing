"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
    title: string;
    value: string;
    trend: string;
    trendUp: boolean;
    icon: LucideIcon;
    color: "blue" | "purple" | "green" | "orange";
    index?: number; // For staggered animation
}

export function StatsCard({ title, value, trend, trendUp, icon: Icon, color, index = 0 }: StatsCardProps) {
    const colorMap = {
        blue: "text-blue-500 bg-blue-500/10 border-blue-500/20",
        purple: "text-purple-500 bg-purple-500/10 border-purple-500/20",
        green: "text-emerald-500 bg-emerald-500/10 border-emerald-500/20",
        orange: "text-orange-500 bg-orange-500/10 border-orange-500/20",
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1, ease: "easeOut" }}
            className="p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-md hover:bg-white/10 transition-colors group"
        >
            <div className="flex justify-between items-start mb-4">
                <div className={cn("p-3 rounded-xl border transition-colors", colorMap[color])}>
                    <Icon size={22} />
                </div>
                <div className={cn(
                    "px-2.5 py-1 rounded-full text-xs font-medium border",
                    trendUp
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : "bg-red-500/10 text-red-400 border-red-500/20"
                )}>
                    {trend}
                </div>
            </div>

            <h3 className="text-muted-foreground text-sm font-medium mb-1">{title}</h3>
            <motion.p
                key={value} // Re-animate on value change
                initial={{ scale: 0.9, opacity: 0.5 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="text-3xl font-bold tracking-tight text-white mb-1"
            >
                {value}
            </motion.p>
        </motion.div>
    );
}
