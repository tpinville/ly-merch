// ------------------------------- src/types.ts --------------------------------
export type Magnitude = "Low" | "Medium" | "High" | string;


export interface TrendRow {
trend_name: string;
image: string;
category: string;
annual_growth: number; // 0.18 = 18%
magnitude: Magnitude;
new_cluster: boolean;
}


export type SortKey = keyof TrendRow;
export type SortDir = "asc" | "desc";
