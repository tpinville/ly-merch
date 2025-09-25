import React from "react";
import Papa from "papaparse";
import type { TrendRow } from "../types";

type Props = { onRows: (rows: TrendRow[]) => void; buttonLabel?: string };

function parseBool(v: unknown): boolean {
  if (typeof v === "boolean") return v;
  if (v == null) return false;
  const s = String(v).trim().toLowerCase();
  return ["1", "true", "yes", "y"].includes(s);
}

function normalizeRow(r: Record<string, any>): TrendRow {
  const annual = parseFloat(
    r.annual_growth ?? r["annual growth"] ?? r.growth ?? r.Growth ?? 0
  );
  return {
    trend_name: r.trend_name ?? r.TrendName ?? r.trendName ?? r.trend ?? "",
    image: r.image ?? r.img ?? r.Image ?? "",
    category: r.category ?? r.Category ?? "",
    annual_growth: Number.isFinite(annual) ? annual : 0,
    magnitude: r.magnitude ?? r.Magnitude ?? "",
    new_cluster: parseBool(r.new_cluster ?? r["new cluster"] ?? r.newCluster),
  };
}

export default function CsvUpload({ onRows, buttonLabel = "Upload CSV" }: Props) {
  const inputRef = React.useRef<HTMLInputElement | null>(null);

  const handlePick = () => inputRef.current?.click();

  const handleFile = (file: File) => {
    Papa.parse<Record<string, any>>(file, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim().toLowerCase().replace(/\s+/g, "_"),
      complete: (res) => {
        const rows = (res.data || []).map(normalizeRow);
        onRows?.(rows);
      },
      error: (err) => {
        console.error("CSV parse error", err);
        alert("Failed to parse CSV. Check console for details.");
      },
    });
  };

  const onChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const f = e.currentTarget.files?.[0];
    if (f) handleFile(f);
  };

  return (
    <div style={{ display: "flex", gap: 12 }}>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        onChange={onChange}
        style={{ display: "none" }}
      />
      <button
        type="button"
        onClick={handlePick}
        style={{
          padding: "10px 14px",
          borderRadius: 10,
          border: "1px solid #e5e7eb",
          background: "linear-gradient(180deg,#f4f4f5,#ffffff)",
          cursor: "pointer",
          fontWeight: 600,
        }}
      >
        {buttonLabel}
      </button>
    </div>
  );
}
