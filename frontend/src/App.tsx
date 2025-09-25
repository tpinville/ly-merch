import React, { useState } from "react";
import FashionTrendsDashboard from "./components/FashionTrendsDashboard";
import CsvUpload from "./components/CsvUpload";
import TrendsTable from "./components/TrendsTable";
import type { TrendRow } from "./types";

type AppMode = 'fashion-db' | 'csv-uploader';

const sampleRows: TrendRow[] = [
  { trend_name: "Ballet flats", image: "https://images.unsplash.com/photo-1519744792095-2f2205e87b6f", category: "Footwear", annual_growth: 0.18, magnitude: "Medium", new_cluster: true },
  { trend_name: "Cargo maxi skirts", image: "https://images.unsplash.com/photo-1584003564911-1f277c1fba2e", category: "Apparel", annual_growth: 0.27, magnitude: "High", new_cluster: true },
  { trend_name: "Samba sneakers", image: "https://images.unsplash.com/photo-1582582494700-1e3a6c49cb03", category: "Footwear", annual_growth: 0.12, magnitude: "High", new_cluster: false }
];


export default function App() {
  const [mode, setMode] = useState<AppMode>('fashion-db');
  const [rows, setRows] = React.useState<TrendRow[]>(sampleRows);


  const downloadTemplate = () => {
    const header = ["trend_name", "image", "category", "annual_growth", "magnitude", "new_cluster"];
    const csv = [header.join(","),
      ...rows.map((r) => [r.trend_name, r.image, r.category, r.annual_growth, r.magnitude, r.new_cluster].join(",")),
    ].join("\n");


    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "trends_template.csv"; document.body.appendChild(a); a.click(); a.remove();
    URL.revokeObjectURL(url);
  };


  if (mode === 'fashion-db') {
    return (
      <div style={{ position: 'relative' }}>
        <button
          onClick={() => setMode('csv-uploader')}
          style={{
            position: 'fixed' as const,
            top: '16px',
            right: '16px',
            zIndex: 1000,
            ...btnSecondary
          }}
        >
          Switch to CSV Uploader
        </button>
        <FashionTrendsDashboard />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 1100, margin: "32px auto", padding: "0 16px", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <h1 style={{ fontSize: 24, margin: 0 }}>Trends Uploader</h1>
          <button onClick={() => setMode('fashion-db')} style={btnSecondary}>
            View Fashion Database
          </button>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={downloadTemplate} style={btnSecondary}>Download CSV template</button>
          <CsvUpload onRows={setRows} />
        </div>
      </header>

      <TrendsTable rows={rows} />
    </div>
  );
}


const btnSecondary: React.CSSProperties = {
  padding: "10px 14px",
  borderRadius: 10,
  border: "1px solid #e5e7eb",
  background: "linear-gradient(180deg,#f8fafc,#ffffff)",
  cursor: "pointer",
  fontWeight: 600,
  fontSize: '14px',
  color: '#374151',
};

