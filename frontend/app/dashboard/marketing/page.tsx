"use client";

import { CampaignCard } from "@/components/dashboard/CampaignCard";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Sparkles, Loader2, X, AlertCircle } from "lucide-react";
import { useState, useEffect } from "react";
import { useCampaignStore } from "@/stores/campaignStore";

export default function MarketingPage() {
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [formData, setFormData] = useState({
        name: "",
        platform: "instagram" as "instagram" | "twitter" | "linkedin" | "email",
        description: "",
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { campaigns, isLoading, error, fetchCampaigns, createCampaign, clearError } = useCampaignStore();

    // Fetch campaigns on mount
    useEffect(() => {
        fetchCampaigns();
    }, [fetchCampaigns]);

    const handleCreate = async () => {
        if (!formData.name.trim()) return;

        setIsSubmitting(true);
        const result = await createCampaign({
            name: formData.name,
            platform: formData.platform,
            description: formData.description || undefined,
        });

        if (result) {
            setShowCreateModal(false);
            setFormData({ name: "", platform: "instagram", description: "" });
        }
        setIsSubmitting(false);
    };

    // Transform campaigns for CampaignCard component
    const transformedCampaigns = campaigns.map(c => ({
        id: c.id,
        name: c.name,
        status: c.status,
        platform: c.platform,
        scheduledDate: c.scheduled_date,
        metrics: c.metrics ? {
            impressions: c.metrics.impressions,
            likes: c.metrics.likes,
            comments: c.metrics.comments
        } : undefined
    }));

    return (
        <div suppressHydrationWarning>
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Marketing Campaigns</h1>
                    <p className="text-muted-foreground">Manage your AI-powered marketing campaigns across platforms.</p>
                </div>
                <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center gap-2 px-4 py-2.5 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20"
                >
                    <Plus size={18} />
                    New Campaign
                </motion.button>
            </div>

            {/* Error Banner */}
            <AnimatePresence>
                {error && (
                    <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="mb-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-center justify-between"
                    >
                        <div className="flex items-center gap-3">
                            <AlertCircle className="text-red-400" size={20} />
                            <span className="text-red-400">{error}</span>
                        </div>
                        <button onClick={clearError} className="text-red-400 hover:text-red-300">
                            <X size={18} />
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Quick Actions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <motion.button
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="p-4 rounded-xl border border-white/5 bg-gradient-to-br from-purple-500/10 to-blue-500/10 hover:from-purple-500/20 hover:to-blue-500/20 transition-all text-left group"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <Sparkles size={20} className="text-purple-400" />
                        <span className="font-medium text-white">AI Campaign Generator</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Let AI create a full campaign strategy for you</p>
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-all text-left"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-lg">📊</span>
                        <span className="font-medium text-white">View Analytics</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Deep dive into campaign performance</p>
                </motion.button>

                <motion.button
                    whileHover={{ scale: 1.02, y: -2 }}
                    className="p-4 rounded-xl border border-white/5 bg-white/5 hover:bg-white/10 transition-all text-left"
                >
                    <div className="flex items-center gap-3 mb-2">
                        <span className="text-lg">📅</span>
                        <span className="font-medium text-white">Content Calendar</span>
                    </div>
                    <p className="text-sm text-muted-foreground">Schedule and plan your posts</p>
                </motion.button>
            </div>

            {/* Campaign Grid */}
            <div className="mb-6">
                <h2 className="text-lg font-semibold mb-4">Your Campaigns</h2>

                {isLoading && campaigns.length === 0 ? (
                    <div className="flex items-center justify-center py-12">
                        <Loader2 className="animate-spin text-primary" size={32} />
                    </div>
                ) : campaigns.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                        <p className="mb-2">No campaigns yet</p>
                        <p className="text-sm">Click &quot;New Campaign&quot; to get started</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {transformedCampaigns.map((campaign, index) => (
                            <CampaignCard key={campaign.id} campaign={campaign} index={index} />
                        ))}
                    </div>
                )}
            </div>

            {/* Create Modal */}
            <AnimatePresence>
                {showCreateModal && (
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ opacity: 0, scale: 0.95 }}
                            className="bg-background border border-white/10 rounded-2xl p-6 w-full max-w-lg mx-4 shadow-2xl"
                        >
                            <h2 className="text-xl font-bold mb-4">Create New Campaign</h2>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-muted-foreground mb-1 block">Campaign Name</label>
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={e => setFormData({ ...formData, name: e.target.value })}
                                        placeholder="e.g., Spring Product Launch"
                                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50"
                                    />
                                </div>
                                <div>
                                    <label className="text-sm text-muted-foreground mb-1 block">Platform</label>
                                    <select
                                        value={formData.platform}
                                        onChange={e => setFormData({ ...formData, platform: e.target.value as typeof formData.platform })}
                                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50"
                                    >
                                        <option value="instagram">📸 Instagram</option>
                                        <option value="twitter">🐦 Twitter</option>
                                        <option value="linkedin">💼 LinkedIn</option>
                                        <option value="email">📧 Email</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="text-sm text-muted-foreground mb-1 block">Description</label>
                                    <textarea
                                        value={formData.description}
                                        onChange={e => setFormData({ ...formData, description: e.target.value })}
                                        placeholder="What's this campaign about?"
                                        rows={3}
                                        className="w-full px-4 py-2.5 bg-white/5 border border-white/10 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 resize-none"
                                    />
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    disabled={isSubmitting}
                                    className="px-4 py-2 text-muted-foreground hover:text-white transition-colors disabled:opacity-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreate}
                                    disabled={isSubmitting || !formData.name.trim()}
                                    className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-2"
                                >
                                    {isSubmitting && <Loader2 className="animate-spin" size={16} />}
                                    Create Campaign
                                </button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
}
