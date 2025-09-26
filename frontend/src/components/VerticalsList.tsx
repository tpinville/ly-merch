import React, { useState } from 'react';
import { useVerticals, useCategories } from '../services/api';
import type { Vertical } from '../types/api';

interface VerticalsListProps {
  onVerticalSelect?: (vertical: Vertical) => void;
  selectedVerticalId?: number;
  selectedCategoryId?: number;
}

export default function VerticalsList({ onVerticalSelect, selectedVerticalId, selectedCategoryId: propCategoryId }: VerticalsListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGeoZone, setSelectedGeoZone] = useState('');
  const [selectedCategoryId, setSelectedCategoryId] = useState<number | undefined>(propCategoryId);

  const { data: categories } = useCategories({ limit: 100 });

  const effectiveCategoryId = propCategoryId || selectedCategoryId;

  const { data: verticals, loading, error } = useVerticals({
    query: searchQuery || undefined,
    geo_zone: selectedGeoZone || undefined,
    category_id: effectiveCategoryId,
    limit: 50
  });

  // Get unique geo zones
  const geoZones = Array.from(new Set(verticals?.map(v => v.geo_zone) || []));

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  if (loading) {
    return <div style={styles.loading}>Loading verticals...</div>;
  }

  if (error) {
    return <div style={styles.error}>Error: {error}</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Fashion Verticals</h3>
        <div style={styles.filters}>
          <input
            type="text"
            placeholder="Search verticals..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            style={styles.searchInput}
          />
          <select
            value={effectiveCategoryId || ''}
            onChange={(e) => setSelectedCategoryId(e.target.value ? parseInt(e.target.value) : undefined)}
            style={styles.select}
          >
            <option value="">All Categories</option>
            {categories?.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
              </option>
            ))}
          </select>
          <select
            value={selectedGeoZone}
            onChange={(e) => setSelectedGeoZone(e.target.value)}
            style={styles.select}
          >
            <option value="">All Regions</option>
            {geoZones.map((zone) => (
              <option key={zone} value={zone}>
                {zone.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div style={styles.verticalsList}>
        {verticals && verticals.length > 0 ? (
          verticals.map((vertical) => (
            <VerticalCard
              key={vertical.id}
              vertical={vertical}
              isSelected={selectedVerticalId === vertical.id}
              onClick={() => onVerticalSelect?.(vertical)}
            />
          ))
        ) : (
          <div style={styles.noResults}>
            No categories found matching your criteria.
          </div>
        )}
      </div>
    </div>
  );
}

interface VerticalCardProps {
  vertical: Vertical;
  isSelected: boolean;
  onClick: () => void;
}

function VerticalCard({ vertical, isSelected, onClick }: VerticalCardProps) {
  return (
    <div
      style={{
        ...styles.verticalCard,
        ...(isSelected ? styles.verticalCardSelected : {}),
      }}
      onClick={onClick}
    >
      <div style={styles.verticalInfo}>
        <div style={styles.categoryBadge}>
          {vertical.category_name || 'Unknown Category'}
        </div>
        <h4 style={styles.verticalName}>{vertical.name}</h4>
        <div style={styles.verticalMeta}>
          <span style={styles.verticalId}>
            {vertical.vertical_id.split(':').slice(-1)[0]}
          </span>
          <span style={styles.geoZone}>{vertical.geo_zone.toUpperCase()}</span>
        </div>
      </div>
      <div style={styles.trendCount}>
        <span style={styles.count}>{vertical.trend_count}</span>
        <span style={styles.countLabel}>trends</span>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    overflow: 'hidden',
  },
  header: {
    padding: '20px',
    borderBottom: '1px solid #e5e7eb',
    backgroundColor: '#f8fafc',
  },
  title: {
    margin: '0 0 16px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
  },
  filters: {
    display: 'flex',
    gap: '12px',
  },
  searchInput: {
    flex: 1,
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
  },
  select: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    minWidth: '120px',
  },
  verticalsList: {
    maxHeight: '500px',
    overflowY: 'auto' as const,
  },
  verticalCard: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 20px',
    borderBottom: '1px solid #f3f4f6',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    ':hover': {
      backgroundColor: '#f8fafc',
    },
  },
  verticalCardSelected: {
    backgroundColor: '#eff6ff',
    borderLeft: '4px solid #3b82f6',
  },
  verticalInfo: {
    flex: 1,
  },
  categoryBadge: {
    display: 'inline-block',
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    fontSize: '11px',
    fontWeight: '600',
    padding: '2px 8px',
    borderRadius: '12px',
    marginBottom: '6px',
    textTransform: 'capitalize' as const,
  },
  verticalName: {
    margin: '0 0 4px 0',
    fontSize: '16px',
    fontWeight: '500',
    color: '#1f2937',
  },
  verticalMeta: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
    fontSize: '12px',
    color: '#6b7280',
  },
  verticalId: {
    fontFamily: 'monospace',
    backgroundColor: '#f3f4f6',
    padding: '2px 6px',
    borderRadius: '4px',
  },
  geoZone: {
    backgroundColor: '#e0e7ff',
    color: '#3730a3',
    padding: '2px 6px',
    borderRadius: '4px',
    fontWeight: '600',
  },
  trendCount: {
    textAlign: 'center' as const,
    marginLeft: '16px',
  },
  count: {
    display: 'block',
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1f2937',
    lineHeight: '1',
  },
  countLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '2px',
  },
  noResults: {
    padding: '40px 20px',
    textAlign: 'center' as const,
    color: '#6b7280',
    fontStyle: 'italic' as const,
  },
  loading: {
    padding: '40px 20px',
    textAlign: 'center' as const,
    color: '#6b7280',
  },
  error: {
    padding: '20px',
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    color: '#dc2626',
    textAlign: 'center' as const,
  },
};