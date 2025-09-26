// API Service for Fashion Trends Database

import type {
  Category,
  Vertical,
  Trend,
  TrendSummary,
  TrendImage,
  ApiStats,
  ImageStats,
  TrendSearchParams,
  VerticalSearchParams
} from '../types/api';

const API_BASE_URL = 'http://localhost:8001/api/v1';

class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
  try {
    const url = new URL(`${API_BASE_URL}${endpoint}`);

    // Add query parameters
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          url.searchParams.append(key, String(value));
        }
      });
    }

    const response = await fetch(url.toString());

    if (!response.ok) {
      throw new ApiError(
        `HTTP error! status: ${response.status}`,
        response.status
      );
    }

    const data = await response.json();
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export const fashionApi = {
  // Health & Stats
  async getHealth() {
    return fetchApi<{ status: string; api_version: string; database: any }>('/health');
  },

  async getStats(): Promise<ApiStats> {
    return fetchApi<ApiStats>('/stats');
  },

  // Verticals
  async getVerticals(params?: VerticalSearchParams): Promise<Vertical[]> {
    return fetchApi<Vertical[]>('/verticals/', params);
  },

  async getVertical(id: number, includeTrends = false): Promise<Vertical> {
    return fetchApi<Vertical>(`/verticals/${id}`, { include_trends: includeTrends });
  },

  async getGeoZones(): Promise<string[]> {
    return fetchApi<string[]>('/verticals/search/geo-zones');
  },

  // Categories
  async getCategories(params?: { query?: string; limit?: number; offset?: number }): Promise<Category[]> {
    return fetchApi<Category[]>('/categories/', params);
  },

  async getCategory(id: number): Promise<Category> {
    return fetchApi<Category>(`/categories/${id}`);
  },

  // Trends
  async getTrends(params?: TrendSearchParams): Promise<TrendSummary[]> {
    return fetchApi<TrendSummary[]>('/trends/', params);
  },

  async getTrend(id: number, includeImages = false): Promise<Trend> {
    return fetchApi<Trend>(`/trends/${id}`, { include_images: includeImages });
  },

  async searchTrendsFulltext(query: string, limit = 10) {
    return fetchApi<Array<{ id: number; trend_id: string; name: string; description: string }>>('/trends/search/fulltext', { q: query, limit });
  },

  // Images
  async getImages(params?: { trend_id?: number; image_type?: string; limit?: number; offset?: number }): Promise<TrendImage[]> {
    return fetchApi<TrendImage[]>('/images/', params);
  },

  async getImage(id: number): Promise<TrendImage> {
    return fetchApi<TrendImage>(`/images/${id}`);
  },

  async getImageStats(): Promise<ImageStats> {
    return fetchApi<ImageStats>('/images/stats/summary');
  }
};

// React hooks for API calls
import { useState, useEffect } from 'react';
import type { ApiResponse } from '../types/api';

export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
): ApiResponse<T | null> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | undefined>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(undefined);
        const result = await apiCall();
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'An error occurred');
          setData(null);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchData();

    return () => {
      cancelled = true;
    };
  }, dependencies);

  return { data, error, loading };
}

// Specific hooks for common operations
export function useVerticals(params?: VerticalSearchParams) {
  return useApi(() => fashionApi.getVerticals(params), [JSON.stringify(params)]);
}

export function useTrends(params?: TrendSearchParams) {
  return useApi(() => fashionApi.getTrends(params), [JSON.stringify(params)]);
}

export function useStats() {
  return useApi(() => fashionApi.getStats(), []);
}

export function useTrend(id: number, includeImages = false) {
  return useApi(() => fashionApi.getTrend(id, includeImages), [id, includeImages]);
}

export function useVertical(id: number, includeTrends = false) {
  return useApi(() => fashionApi.getVertical(id, includeTrends), [id, includeTrends]);
}

export function useCategories(params?: { query?: string; limit?: number; offset?: number }) {
  return useApi(() => fashionApi.getCategories(params), [JSON.stringify(params)]);
}

export function useCategory(id: number) {
  return useApi(() => fashionApi.getCategory(id), [id]);
}