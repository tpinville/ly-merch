// =====================================================================
// React + TypeScript: CSV Upload + Sort/Filter Table (Vite)
// Files below are meant to live under /frontend/src (except tsconfig.json)
// =====================================================================

// ------------------------------- tsconfig.json -------------------------------
// Put this file at the project root (same level as package.json)
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "baseUrl": "."
  },
  "include": ["src"]
}

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

// -------------------------- src/components/CsvUpload.tsx ---------------------
import React from "react";
import Papa from "papaparse";
import type { TrendRow } from "../types";

interface CsvUploadProps {
  onRows: (rows: TrendRow[]) => void;
  buttonLabel?: string;
}

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

export default function CsvUpload({ onRows, buttonLabel = "Upload CSV" }: CsvUploadProps) {
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
    <div style={uploaderWrap}>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,text/csv"
        onChange={onChange}
        style={{ display: "none" }}
      />
      <button type="button" onClick={handlePick} style={buttonStyle}>
        {buttonLabel}
      </button>
    </div>
  );
}

const uploaderWrap: React.CSSProperties = { display: "flex", gap: 12 };
const buttonStyle: React.CSSProperties = {
  padding: "10px 14px",
  borderRadius: 10,
  border: "1px solid #e5e7eb",
  background: "linear-gradient(180deg,#f4f4f5,#ffffff)",
  cursor: "pointer",
  fontWeight: 600,
};

// ----------------------- src/components/TrendsTable.tsx ----------------------
import React from "react";
import type { TrendRow, SortKey, SortDir } from "../types";

interface Props {
  rows: TrendRow[];
}

export default function TrendsTable({ rows }: Props) {
  const [sortKey, setSortKey] = React.useState<SortKey>("trend_name");
  const [sortDir, setSortDir] = React.useState<SortDir>("asc");
  const [q, setQ] = React.useState("");
  const [cat, setCat] = React.useState<string>("All");
  const [onlyNew, setOnlyNew] = React.useState(false);

  const categories = React.useMemo(() => {
    const set = new Set<string>(rows.map((r) => r.category).filter(Boolean));
    return ["All", ...Array.from(set).sort()];
  }, [rows]);

  const filtered = React.useMemo(() => {
    const needle = q.trim().toLowerCase();
    return rows.filter((r) => {
      if (onlyNew && !r.new_cluster) return false;
      if (cat !== "All" && r.category !== cat) return false;
      if (!needle) return true;
      return (
        r.trend_name.toLowerCase().includes(needle) ||
        r.category.toLowerCase().includes(needle) ||
        String(r.magnitude).toLowerCase().includes(needle)
      );
    });
  }, [rows, q, cat, onlyNew]);

  const sorted = React.useMemo(() => {
    const copy = [...filtered];
    const dir = sortDir === "asc" ? 1 : -1;
    copy.sort((a, b) => compare(a, b, sortKey) * dir);
    return copy;
  }, [filtered, sortKey, sortDir]);

  const setSort = (key: SortKey) => {
    if (key === sortKey) setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div style={panel}>
      <div style={toolbar}>
        <input
          placeholder="Search trends, category, magnitude…"
          value={q}
          onChange={(e) => setQ(e.currentTarget.value)}
          style={input}
        />
        <select value={cat} onChange={(e) => setCat(e.currentTarget.value)} style={select}>
          {categories.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input type="checkbox" checked={onlyNew} onChange={(e) => setOnlyNew(e.currentTarget.checked)} />
          Only new clusters
        </label>
      </div>

      <div style={wrapStyle}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <SortableTh onClick={() => setSort("trend_name")} active={sortKey === "trend_name"} dir={sortDir}>trend_name</SortableTh>
              <Th>image</Th>
              <SortableTh onClick={() => setSort("category")} active={sortKey === "category"} dir={sortDir}>category</SortableTh>
              <SortableTh onClick={() => setSort("annual_growth")} active={sortKey === "annual_growth"} dir={sortDir}>annual growth</SortableTh>
              <SortableTh onClick={() => setSort("magnitude")} active={sortKey === "magnitude"} dir={sortDir}>magnitude</SortableTh>
              <SortableTh onClick={() => setSort("new_cluster")} active={sortKey === "new_cluster"} dir={sortDir}>new_cluster</SortableTh>
            </tr>
          </thead>
          <tbody>
            {sorted.map((r, i) => (
              <tr key={i} style={i % 2 ? rowAlt : undefined}>
                <Td style={{ fontWeight: 600 }}>{r.trend_name || "—"}</Td>
                <Td>
                  {r.image ? (
                    <img
                      src={r.image}
                      alt=""
                      style={{ width: 64, height: 64, objectFit: "cover", borderRadius: 8, border: "1px solid #e5e7eb" }}
                      onError={(e) => (e.currentTarget.style.visibility = "hidden")}
                    />
                  ) : (
                    "—"
                  )}
                </Td>
                <Td>{r.category || "—"}</Td>
                <Td>{formatPercent(r.annual_growth)}</Td>
                <Td>
                  {r.magnitude ? (
                    <span style={pillStyle}>{r.magnitude}</span>
                  ) : (
                    "—"
                  )}
                </Td>
                <Td>{r.new_cluster ? <span style={newStyle}>new</span> : "—"}</Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function compare(a: TrendRow, b: TrendRow, key: SortKey): number {
  const av = a[key] as any;
  const bv = b[key] as any;
  if (key === "annual_growth") return (av ?? 0) - (bv ?? 0);
  if (key === "new_cluster") return (Number(!!av) - Number(!!bv));
  return String(av ?? "").localeCompare(String(bv ?? ""));
}

const panel: React.CSSProperties = { display: "grid", gap: 12 };
const toolbar: React.CSSProperties = { display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" };
const input: React.CSSProperties = { padding: "10px 12px", borderRadius: 10, border: "1px solid #e5e7eb", flex: 1, minWidth: 240 };
const select: React.CSSProperties = { padding: "10px 12px", borderRadius: 10, border: "1px solid #e5e7eb" };

const wrapStyle: React.CSSProperties = {
  border: "1px solid #e5e7eb",
  borderRadius: 14,
  overflow: "hidden",
  boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
};
const tableStyle: React.CSSProperties = { width: "100%", borderCollapse: "separate", borderSpacing: 0 };
const thtd = { textAlign: "left", padding: "12px 14px", borderBottom: "1px solid #f1f5f9" } as const;
const Th: React.FC<React.PropsWithChildren> = (p) => (
  <th style={{ ...thtd, fontSize: 12, textTransform: "uppercase", letterSpacing: 0.4, color: "#6b7280", background: "#fafafa" }} {...p} />
);
const Td: React.FC<React.ComponentPropsWithoutRef<'td'>> = (p) => <td style={{ ...thtd, verticalAlign: "middle" }} {...p} />;
const rowAlt: React.CSSProperties = { background: "#fcfcfc" };
const pillStyle: React.CSSProperties = { display: "inline-block", padding: "2px 8px", borderRadius: 999, border: "1px solid #e5e7eb", background: "#fff", fontSize: 12 };
const newStyle: React.CSSProperties = { ...pillStyle, background: "#f0fdf4", borderColor: "#bbf7d0" };

const SortableTh: React.FC<{ onClick: () => void; active: boolean; dir: SortDir; children: React.ReactNode }> = ({ onClick, active, dir, children }) => (
  <Th>
    <button onClick={onClick} style={{ all: "unset", cursor: "pointer" }}>
      <span style={{ fontWeight: active ? 700 : 500 }}>{children}</span>
      {active && <span style={{ marginLeft: 6 }}>{dir === "asc" ? "▲" : "▼"}</span>}
    </button>
  </Th>
);

function formatPercent(v: number): string {
  if (typeof v !== "number" || Number.isNaN(v)) return "—";
  const sign = v > 0 ? "+" : v < 0 ? "" : "";
  return `${sign}${(v * 100).toFixed(1)}%`;
}

// -------------------------------- src/App.tsx --------------------------------
import React from "react";
import CsvUpload from "./components/CsvUpload";
import TrendsTable from "./components/TrendsTable";
import type { TrendRow } from "./types";

const sampleRows: TrendRow[] = [
  { trend_name: "Ballet flats", image: "https://images.unsplash.com/photo-1519744792095-2f2205e87b6f", category: "Footwear", annual_growth: 0.18, magnitude: "Medium", new_cluster: true },
  { trend_name: "Cargo maxi skirts", image: "https://images.unsplash.com/photo-1584003564911-1f277c1fba2e", category: "Apparel", annual_growth: 0.27, magnitude: "High", new_cluster: true },
  { trend_name: "Samba sneakers", image: "https://images.unsplash.com/photo-1582582494700-1e3a6c49cb03", category: "Footwear", annual_growth: 0.12, magnitude: "High", new_cluster: false }
];

export default function App() {
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

  return (
    <div style={{ maxWidth: 1100, margin: "32px auto", padding: "0 16px", fontFamily: "system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial" }}>
      <header style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <h1 style={{ fontSize: 24, margin: 0 }}>Trends Uploader</h1>
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
};

// ------------------------------- src/main.tsx --------------------------------
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const root = document.getElementById("root")!;
createRoot(root).render(<App />);

