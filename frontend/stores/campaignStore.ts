/**
 * Campaign Store - Zustand state management for marketing campaigns
 */
import { create } from "zustand";
import { apiClient, Campaign, CampaignCreate } from "@/lib/api-client";

interface CampaignState {
    campaigns: Campaign[];
    isLoading: boolean;
    error: string | null;
    selectedCampaign: Campaign | null;

    // Actions
    fetchCampaigns: (status?: string, platform?: string) => Promise<void>;
    getCampaign: (id: string) => Promise<void>;
    createCampaign: (campaign: CampaignCreate) => Promise<Campaign | null>;
    updateCampaign: (id: string, updates: Partial<Campaign>) => Promise<void>;
    deleteCampaign: (id: string) => Promise<void>;
    generateContent: (id: string) => Promise<string | null>;
    clearError: () => void;
    setSelectedCampaign: (campaign: Campaign | null) => void;
}

export const useCampaignStore = create<CampaignState>((set) => ({
    campaigns: [],
    isLoading: false,
    error: null,
    selectedCampaign: null,

    fetchCampaigns: async (status?: string, platform?: string) => {
        set({ isLoading: true, error: null });
        try {
            const campaigns = await apiClient.getCampaigns(status, platform);
            set({ campaigns, isLoading: false });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to fetch campaigns",
                isLoading: false,
            });
        }
    },

    getCampaign: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
            const campaign = await apiClient.getCampaign(id);
            set({ selectedCampaign: campaign, isLoading: false });
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to fetch campaign",
                isLoading: false,
            });
        }
    },

    createCampaign: async (campaignData: CampaignCreate) => {
        set({ isLoading: true, error: null });
        try {
            const newCampaign = await apiClient.createCampaign(campaignData);
            set((state) => ({
                campaigns: [...state.campaigns, newCampaign],
                isLoading: false,
            }));
            return newCampaign;
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to create campaign",
                isLoading: false,
            });
            return null;
        }
    },

    updateCampaign: async (id: string, updates: Partial<Campaign>) => {
        set({ isLoading: true, error: null });
        try {
            const updated = await apiClient.updateCampaign(id, updates);
            set((state) => ({
                campaigns: state.campaigns.map((c) => (c.id === id ? updated : c)),
                selectedCampaign: state.selectedCampaign?.id === id ? updated : state.selectedCampaign,
                isLoading: false,
            }));
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to update campaign",
                isLoading: false,
            });
        }
    },

    deleteCampaign: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
            await apiClient.deleteCampaign(id);
            set((state) => ({
                campaigns: state.campaigns.filter((c) => c.id !== id),
                selectedCampaign: state.selectedCampaign?.id === id ? null : state.selectedCampaign,
                isLoading: false,
            }));
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to delete campaign",
                isLoading: false,
            });
        }
    },

    generateContent: async (id: string) => {
        set({ isLoading: true, error: null });
        try {
            const result = await apiClient.generateCampaignContent(id);
            // Update the campaign with the generated content
            set((state) => ({
                campaigns: state.campaigns.map((c) => (c.id === id ? result.campaign : c)),
                selectedCampaign: state.selectedCampaign?.id === id ? result.campaign : state.selectedCampaign,
                isLoading: false,
            }));
            return result.content;
        } catch (error) {
            set({
                error: error instanceof Error ? error.message : "Failed to generate content",
                isLoading: false,
            });
            return null;
        }
    },

    clearError: () => set({ error: null }),

    setSelectedCampaign: (campaign: Campaign | null) => set({ selectedCampaign: campaign }),
}));
