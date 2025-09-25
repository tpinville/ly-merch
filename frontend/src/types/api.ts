// API Types for Fashion Trends Database

export interface Vertical {
  id: number;
  vertical_id: string;
  name: string;
  geo_zone: string;
  trend_count: number;
  created_at: string;
  updated_at: string;
  trends?: TrendSummary[];
}

export interface TrendSummary {
  id: number;
  trend_id: string;
  name: string;
  description?: string;
  image_hash?: string;
  image_count: number;
  positive_image_count: number;
  negative_image_count: number;
}

export interface Trend {
  id: number;
  trend_id: string;
  name: string;
  description?: string;
  image_hash?: string;
  created_at: string;
  updated_at: string;
  images?: TrendImage[];
}

export interface TrendImage {
  id: number;
  image_type: 'positive' | 'negative';
  md5_hash: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface ApiStats {
  total_verticals: number;
  total_trends: number;
  total_images: number;
  geo_zones: Record<string, number>;
  image_types: Record<string, number>;
}

export interface ImageStats {
  total_images: number;
  by_type: Record<string, number>;
}

// Search/Filter parameters
export interface TrendSearchParams {
  query?: string;
  vertical_id?: number;
  vertical_name?: string;
  geo_zone?: string;
  has_images?: boolean;
  image_type?: string;
  limit?: number;
  offset?: number;
}

export interface VerticalSearchParams {
  query?: string;
  geo_zone?: string;
  limit?: number;
  offset?: number;
}

// API Response wrapper
export interface ApiResponse<T> {
  data: T;
  error?: string;
  loading: boolean;
}