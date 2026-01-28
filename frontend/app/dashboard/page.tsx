"use client";

import { ActivityChart } from "@/components/dashboard/ActivityChart";
import { StatsCard } from "@/components/dashboard/StatsCard";
import { DollarSign, MessageSquare, TrendingUp, Users } from "lucide-react";
import { useCallback, useState, useEffect } from "react";
import { motion } from "framer-motion";

// Types
interface DashboardSummary {
    revenue: { value: string; trend: string; trendUp: boolean };
    sales_conversations: { value: string; trend: string; trendUp: boolean };
    marketing_reach: { value: string; trend: string; trendUp: boolean };
    active_users: { value: string; trend: string; trendUp: boolean };
}

interface ActivityData {
    name: string;
    sales: number;
    marketing: number;
    support: number;
}

interface Action {
    id: number;
    description: string;
    time: string;
}

const API_BASE = "http://localhost:8000/api/v1/analytics";

export default function DashboardPage() {
    const [summary, setSummary] = useState<DashboardSummary | null>(null);
    const [activity, setActivity] = useState<ActivityData[]>([]);
    const [recentActions, setRecentActions] = useState<Action[]>([]);
    const [loading, setLoading] = useState(true);
    const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

    const fetchData = useCallback(async () => {
        try {
            const [summaryRes, activityRes, actionsRes] = await Promise.all([
                fetch(`${API_BASE}/summary`),
                fetch(`${API_BASE}/activity`),
                fetch(`${API_BASE}/recent-actions`)
            ]);

            if (summaryRes.ok) setSummary(await summaryRes.json());
            if (activityRes.ok) setActivity(await activityRes.json());
            if (actionsRes.ok) setRecentActions(await actionsRes.json());
            setLastUpdated(new Date());
        } catch (error) {
            console.error("Failed to fetch dashboard data", error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, [fetchData]);

    if (loading || !summary) {
        return (
            <div className="animate-pulse space-y-8">
                <div className="h-8 w-48 bg-white/10 rounded"></div>
                <div className="grid grid-cols-4 gap-6">
                    {[1, 2, 3, 4].map(i => <div key={i} className="h-32 bg-white/5 rounded-xl border border-white/5"></div>)}
                </div>
            </div>
        );
    }

    return (
        <div className="animate-in fade-in duration-500">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Overview</h1>
                    <p className="text-muted-foreground">Welcome back. Here&apos;s what&apos;s happening with your agents today.</p>
                </div>
                {lastUpdated && (
                    <motion.div
                        key={lastUpdated.getTime()}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="text-xs text-muted-foreground bg-white/5 px-3 py-1.5 rounded-full border border-white/5"
                    >
                        Updated {lastUpdated.toLocaleTimeString()}
                    </motion.div>
                )}
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatsCard
                    title="Total Revenue"
                    value={summary.revenue.value}
                    trend={summary.revenue.trend}
                    trendUp={summary.revenue.trendUp}
                    icon={DollarSign}
                    color="green"
                    index={0}
                />
                <StatsCard
                    title="Sales Conversations"
                    value={summary.sales_conversations.value}
                    trend={summary.sales_conversations.trend}
                    trendUp={summary.sales_conversations.trendUp}
                    icon={MessageSquare}
                    color="blue"
                    index={1}
                />
                <StatsCard
                    title="Marketing Reach"
                    value={summary.marketing_reach.value}
                    trend={summary.marketing_reach.trend}
                    trendUp={summary.marketing_reach.trendUp}
                    icon={TrendingUp}
                    color="purple"
                    index={2}
                />
                <StatsCard
                    title="Active Users"
                    value={summary.active_users.value}
                    trend={summary.active_users.trend}
                    trendUp={summary.active_users.trendUp}
                    icon={Users}
                    color="orange"
                    index={3}
                />
            </div>

            {/* Charts Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                    {/* We pass the data to the chart component (needs update to accept props) */}
                    <ActivityChart data={activity} />
                </div>
                <div className="h-[350px] rounded-2xl border border-white/5 bg-white/5 backdrop-blur-md p-6">
                    <h3 className="text-lg font-semibold mb-4">Recent Agent Actions</h3>
                    <div className="space-y-4">
                        {recentActions.map((action) => (
                            <div key={action.id} className="flex gap-4 items-start p-3 hover:bg-white/5 rounded-lg transition-colors cursor-pointer group">
                                <div className="w-2 h-2 mt-2 rounded-full bg-blue-500 group-hover:shadow-[0_0_8px_rgba(59,130,246,0.5)] transition-shadow" />
                                <div>
                                    <p className="text-sm text-white">{action.description}</p>
                                    <p className="text-xs text-muted-foreground">{action.time}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
