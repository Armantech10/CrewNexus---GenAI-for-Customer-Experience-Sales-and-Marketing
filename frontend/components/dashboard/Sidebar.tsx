"use client";

import { cn } from "@/lib/utils";
import { LayoutDashboard, MessageSquare, PieChart, Users, Settings, LifeBuoy, Code } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
    { icon: LayoutDashboard, label: "Overview", href: "/dashboard" },
    { icon: MessageSquare, label: "Chat", href: "/" },
    { icon: PieChart, label: "Sales & Leads", href: "/dashboard/sales" },
    { icon: Users, label: "Marketing Campaigns", href: "/dashboard/marketing" },
    { icon: LifeBuoy, label: "Support Tickets", href: "/dashboard/support" },
    { icon: Code, label: "Engineer Agent", href: "/dashboard/engineer" },
    { icon: Settings, label: "Settings", href: "/dashboard/settings" },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <div className="w-64 h-screen flex flex-col border-r border-white/10 bg-black/20 backdrop-blur-xl p-4">
            <div className="mb-8 px-2 flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center font-bold text-white">
                    C
                </div>
                <span className="font-bold text-lg tracking-tight">CrewNexus</span>
            </div>

            <nav className="flex-1 space-y-1">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={cn(
                                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group text-sm font-medium",
                                isActive
                                    ? "bg-primary/10 text-primary border border-primary/20 shadow-[0_0_15px_rgba(var(--primary),0.1)]"
                                    : "text-muted-foreground hover:text-white hover:bg-white/5"
                            )}
                        >
                            <item.icon size={18} className={cn("transition-colors", isActive ? "text-primary" : "text-gray-400 group-hover:text-white")} />
                            {item.label}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 rounded-2xl bg-gradient-to-br from-white/5 to-white/0 border border-white/5 mt-auto">
                <p className="text-xs text-muted-foreground mb-2">System Status</p>
                <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    All Systems Operational
                </div>
            </div>
        </div>
    );
}
