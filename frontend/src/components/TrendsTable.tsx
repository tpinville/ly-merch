// frontend/src/components/TrendsTable.tsx
import React from "react";
import type { TrendRow, SortKey, SortDir } from "../types";

type Props = { rows: TrendRow[] };

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
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
        <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <input
            type="checkbox"
            checked={onlyNew}
            onChange={(e) => setOnlyNew(e.currentTarget.checked)}
          />
          Only new clusters
        </label>
      </div>

      <div style={wrapStyle}>
        <table style={tableStyle}>
          <thead>
            <tr>
              <SortableTh onClick={() => setSort("trend_name")} active={sortKey === "trend_name"} dir={sortDir}>
                trend_name
              </SortableTh>
              <Th>image</Th>
              <SortableTh onClick={() => setSort("category")} active={sortKey === "category"} dir={sortDir}>
                category
              </SortableTh>
              <SortableTh onClick={() => setSort("annual_growth")} active={sortKey === "annual_growth"} dir={sortDir}>
                annual growth
              </SortableTh>
              <SortableTh onClick={() => setSort("magnitude")} active={sortKey === "magnitude"} dir={sortDir}>
                magnitude
              </SortableTh>
              <SortableTh onClick={() => setSort("new_cluster")} active={sortKey === "new_cluster"} dir={sortDir}>
                new_cluster
              </SortableTh>
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
                      style={imgStyle}
                      onError={(e) => (e.currentTarget.style.visibility = "hidden")}
                    />
                  ) : (
                    "—"
                  )}
                </Td>
                <Td>{r.category || "—"}</Td>
                <Td>{formatPercent(r.annual_growth)}</Td>
                <Td>{r.magnitude ? <span style={pillStyle}>{r.magnitude}</span> : "—"}</Td>
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
  if (key === "new_cluster") return Number(!!av) - Number(!!bv);
  return String(av ?? "").localeCompare(String(bv ?? ""));
}

const panel: React.CSSProperties = { display: "grid", gap: 12 };
const toolbar: React.CSSProperties = { display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" };
const input: React.CSSProperties = { padding: "10px 12px", borderRadius: 10, border: "1px solid #e5e7eb", flex: 1, minWidth: 240 };
const select: React.CSSProperties = { padding: "10px 12px", borderRadius: 10, border: "1px solid #e5e7eb" };

const wrapStyle: React.CSSProperties = { border: "1px solid #e5e7eb", borderRadius: 14, overflow: "hidden", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" };
const tableStyle: React.CSSProperties = { width: "100%", borderCollapse: "separate", borderSpacing: 0 };
const thtd = { textAlign: "left", padding: "12px 14px", borderBottom: "1px solid #f1f5f9" } as const;
const Th: React.FC<React.PropsWithChildren> = (p) => (
  <th
    style={{
      ...thtd,
      fontSize: 12,
      textTransform: "uppercase",
      letterSpacing: 0.4,
      color: "#6b7280",
      background: "#fafafa",
    }}
    {...p}
  />
);
const Td: React.FC<React.ComponentPropsWithoutRef<"td">> = (p) => <td style={{ ...thtd, verticalAlign: "middle" }} {...p} />;
const rowAlt: React.CSSProperties = { background: "#fcfcfc" };
const pillStyle: React.CSSProperties = { display: "inline-block", padding: "2px 8px", borderRadius: 999, border: "1px solid #e5e7eb", background: "#fff", fontSize: 12 };
const newStyle: React.CSSProperties = { ...pillStyle, background: "#f0fdf4", borderColor: "#bbf7d0" };
const imgStyle: React.CSSProperties = { width: 64, height: 64, objectFit: "cover", borderRadius: 8, border: "1px solid #e5e7eb" };

const SortableTh: React.FC<{ onClick: () => void; active: boolean; dir: SortDir; children: React.ReactNode }> = ({
  onClick,
  active,
  dir,
  children,
}) => (
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

