/**
 * API Client - Centralized API calls for the Unified GenAI Platform
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface ChatRequest {
    message: string;
    session_id: string;
    user_id?: string;
    stream?: boolean;
}

export interface ChatResponse {
    response: string;
    intent: string;
    sentiment: string;
    action_taken: string;
    agent_used: string;
    confidence: number;
}

export interface Campaign {
    id: string;
    name: string;
    description?: string;
    status: "draft" | "scheduled" | "active" | "paused" | "completed";
    platform: "instagram" | "twitter" | "linkedin" | "email";
    scheduled_date?: string;
    target_audience?: string;
    content?: string;
    created_at: string;
    metrics: {
        impressions: number;
        likes: number;
        comments: number;
        clicks: number;
        conversions: number;
    };
}

export interface CampaignCreate {
    name: string;
    description?: string;
    platform: "instagram" | "twitter" | "linkedin" | "email";
    scheduled_date?: string;
    target_audience?: string;
    content?: string;
}

export interface DashboardSummary {
    revenue: { value: string; trend: string; trendUp: boolean };
    sales_conversations: { value: string; trend: string; trendUp: boolean };
    marketing_reach: { value: string; trend: string; trendUp: boolean };
    active_users: { value: string; trend: string; trendUp: boolean };
}

// Error handling
class APIError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = "APIError";
    }
}

async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.text();
        throw new APIError(response.status, error || response.statusText);
    }
    return response.json();
}

// API Client
export const apiClient = {
    // Chat
    async sendMessage(request: ChatRequest): Promise<ChatResponse> {
        const response = await fetch(`${API_BASE}/api/v1/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request),
        });
        return handleResponse<ChatResponse>(response);
    },

    // Campaigns
    async getCampaigns(status?: string, platform?: string): Promise<Campaign[]> {
        const params = new URLSearchParams();
        if (status) params.append("status", status);
        if (platform) params.append("platform", platform);

        const url = `${API_BASE}/api/v1/marketing/campaigns${params.toString() ? `?${params}` : ""}`;
        const response = await fetch(url);
        return handleResponse<Campaign[]>(response);
    },

    async getCampaign(id: string): Promise<Campaign> {
        const response = await fetch(`${API_BASE}/api/v1/marketing/campaigns/${id}`);
        return handleResponse<Campaign>(response);
    },

    async createCampaign(campaign: CampaignCreate): Promise<Campaign> {
        const response = await fetch(`${API_BASE}/api/v1/marketing/campaigns`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(campaign),
        });
        return handleResponse<Campaign>(response);
    },

    async updateCampaign(id: string, updates: Partial<Campaign>): Promise<Campaign> {
        const response = await fetch(`${API_BASE}/api/v1/marketing/campaigns/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(updates),
        });
        return handleResponse<Campaign>(response);
    },

    async deleteCampaign(id: string): Promise<void> {
        const response = await fetch(`${API_BASE}/api/v1/marketing/campaigns/${id}`, {
            method: "DELETE",
        });
        if (!response.ok) {
            throw new APIError(response.status, "Failed to delete campaign");
        }
    },

    async generateCampaignContent(id: string): Promise<{ content: string; campaign: Campaign }> {
        const response = await fetch(`${API_BASE}/api/v1/marketing/campaigns/${id}/generate-content`, {
            method: "POST",
        });
        return handleResponse(response);
    },

    // Analytics
    async getDashboardSummary(): Promise<DashboardSummary> {
        const response = await fetch(`${API_BASE}/api/v1/analytics/summary`);
        return handleResponse<DashboardSummary>(response);
    },

    async getActivity(): Promise<{ name: string; sales: number; marketing: number; support: number }[]> {
        const response = await fetch(`${API_BASE}/api/v1/analytics/activity`);
        return handleResponse(response);
    },

    async getRecentActions(): Promise<{ id: number; description: string; time: string }[]> {
        const response = await fetch(`${API_BASE}/api/v1/analytics/recent-actions`);
        return handleResponse(response);
    },

    // Health
    async checkHealth(): Promise<{ status: string }> {
        const response = await fetch(`${API_BASE}/health`);
        return handleResponse(response);
    },
};
