"use client";

import { motion } from "framer-motion";
import { User, Bell, Shield, Palette, Zap, Globe } from "lucide-react";

const settingsSections = [
    { icon: User, label: "Profile", description: "Manage your account details" },
    { icon: Bell, label: "Notifications", description: "Configure alert preferences" },
    { icon: Shield, label: "Security", description: "Password and 2FA settings" },
    { icon: Palette, label: "Appearance", description: "Theme and display options" },
    { icon: Zap, label: "Integrations", description: "Connect external services" },
    { icon: Globe, label: "API Keys", description: "Manage API access" },
];

export default function SettingsPage() {
    return (
        <div>
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2">Settings</h1>
                <p className="text-muted-foreground">Manage your platform preferences and integrations.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {settingsSections.map((section, index) => (
                    <motion.button
                        key={section.label}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.08 }}
                        whileHover={{ scale: 1.02, y: -2 }}
                        className="p-6 rounded-2xl border border-white/5 bg-white/5 hover:bg-white/10 transition-all text-left group"
                    >
                        <div className="p-3 rounded-xl bg-white/5 w-fit mb-4 group-hover:bg-primary/10 transition-colors">
                            <section.icon size={24} className="text-muted-foreground group-hover:text-primary transition-colors" />
                        </div>
                        <h3 className="font-semibold text-white mb-1">{section.label}</h3>
                        <p className="text-sm text-muted-foreground">{section.description}</p>
                    </motion.button>
                ))}
            </div>
        </div>
    );
}
