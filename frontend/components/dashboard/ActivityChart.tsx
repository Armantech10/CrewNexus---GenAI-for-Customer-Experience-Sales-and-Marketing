"use client";

import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

interface ActivityData {
    name: string;
    sales: number;
    marketing: number;
}

export function ActivityChart({ data }: { data?: ActivityData[] }) {
    // Fallback to empty array if no data is provided initially
    const chartData = data || [];

    return (
        <div className="w-full h-[350px] p-6 rounded-2xl border border-white/5 bg-white/5 backdrop-blur-md">
            <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                <span className="w-1 h-5 bg-primary rounded-full"></span>
                Weekly Agent Activity
            </h3>

            <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                    data={chartData}
                    margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                >
                    <defs>
                        <linearGradient id="colorSales" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                        </linearGradient>
                        <linearGradient id="colorMarketing" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis
                        dataKey="name"
                        stroke="#666"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                    />
                    <YAxis
                        stroke="#666"
                        fontSize={12}
                        tickLine={false}
                        axisLine={false}
                    />
                    <Tooltip
                        contentStyle={{ backgroundColor: "#111", borderColor: "#333", borderRadius: "12px" }}
                        itemStyle={{ color: "#fff" }}
                    />
                    <Area
                        type="monotone"
                        dataKey="sales"
                        stroke="#8b5cf6"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#colorSales)"
                        name="Sales Conversations"
                    />
                    <Area
                        type="monotone"
                        dataKey="marketing"
                        stroke="#3b82f6"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#colorMarketing)"
                        name="Marketing Tasks"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
