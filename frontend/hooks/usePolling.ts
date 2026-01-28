"use client";

import { useEffect, useState, useCallback } from "react";

interface UsePollingOptions<T> {
    fetcher: () => Promise<T>;
    interval?: number; // in ms, default 30000
    enabled?: boolean;
}

export function usePolling<T>({ fetcher, interval = 30000, enabled = true }: UsePollingOptions<T>) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);

    const refetch = useCallback(async () => {
        try {
            const result = await fetcher();
            setData(result);
            setError(null);
        } catch (err) {
            setError(err instanceof Error ? err : new Error("Failed to fetch"));
        } finally {
            setLoading(false);
        }
    }, [fetcher]);

    useEffect(() => {
        if (!enabled) return;

        refetch(); // Initial fetch

        const intervalId = setInterval(refetch, interval);
        return () => clearInterval(intervalId);
    }, [refetch, interval, enabled]);

    return { data, loading, error, refetch };
}
