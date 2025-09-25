import React, { useState } from 'react';
import { useTrends, useVerticals, useStats, fashionApi, useTrend } from '../services/api';
import type { TrendSearchParams, TrendSummary, Vertical } from '../types/api';
import ImageWithFallback from './ImageWithFallback';
import ImageGallery from './ImageGallery';
import { getImageAltText } from '../utils/imageUtils';

interface TrendsViewerProps {
  className?: string;
}

export default function TrendsViewer({ className }: TrendsViewerProps) {
  const [searchParams, setSearchParams] = useState<TrendSearchParams>({
    limit: 20,
    offset: 0
  });
  const [selectedVertical, setSelectedVertical] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');

  const { data: trends, loading: trendsLoading, error: trendsError } = useTrends(searchParams);
  const { data: verticals, loading: verticalsLoading } = useVerticals({ limit: 100 });
  const { data: stats } = useStats();

  const handleSearch = () => {
    setSearchParams(prev => ({
      ...prev,
      query: searchQuery || undefined,
      vertical_name: selectedVertical || undefined,
      offset: 0 // Reset to first page
    }));
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setSelectedVertical('');
    setSearchParams({ limit: 20, offset: 0 });
  };

  const handlePageChange = (newOffset: number) => {
    setSearchParams(prev => ({ ...prev, offset: newOffset }));
  };

  if (trendsLoading) {
    return <LoadingSpinner />;
  }

  if (trendsError) {
    return <ErrorMessage error={trendsError} />;
  }

  return (
    <div className={`trends-viewer ${className || ''}`}>
      {/* Header with Stats */}
      <div style={styles.header}>
        <h2 style={styles.title}>Fashion Trends Database</h2>
        {stats && (
          <div style={styles.stats}>
            <StatCard label="Verticals" value={stats.total_verticals} />
            <StatCard label="Trends" value={stats.total_trends} />
            <StatCard label="Images" value={stats.total_images} />
          </div>
        )}
      </div>

      {/* Search and Filters */}
      <div style={styles.filterSection}>
        <div style={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search trends by name or description..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            style={styles.searchInput}
          />
          <button onClick={handleSearch} style={styles.searchButton}>
            Search
          </button>
        </div>

        <div style={styles.filtersContainer}>
          <select
            value={selectedVertical}
            onChange={(e) => setSelectedVertical(e.target.value)}
            style={styles.select}
          >
            <option value="">All Categories</option>
            {verticals?.map((vertical) => (
              <option key={vertical.id} value={vertical.name}>
                {vertical.name} ({vertical.trend_count})
              </option>
            ))}
          </select>

          <button onClick={handleClearFilters} style={styles.clearButton}>
            Clear Filters
          </button>
        </div>
      </div>

      {/* Trends Grid */}
      <div style={styles.trendsGrid}>
        {trends && trends.length > 0 ? (
          trends.map((trend) => (
            <TrendCard key={trend.id} trend={trend} />
          ))
        ) : (
          <div style={styles.noResults}>
            <p>No trends found. Try adjusting your search criteria.</p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {trends && trends.length >= (searchParams.limit || 20) && (
        <div style={styles.pagination}>
          <button
            onClick={() => handlePageChange(Math.max(0, (searchParams.offset || 0) - (searchParams.limit || 20)))}
            disabled={(searchParams.offset || 0) === 0}
            style={styles.pageButton}
          >
            Previous
          </button>
          <span style={styles.pageInfo}>
            Showing {(searchParams.offset || 0) + 1} - {(searchParams.offset || 0) + trends.length}
          </span>
          <button
            onClick={() => handlePageChange((searchParams.offset || 0) + (searchParams.limit || 20))}
            style={styles.pageButton}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

interface TrendCardProps {
  trend: TrendSummary;
}

function TrendCard({ trend }: TrendCardProps) {
  const [expanded, setExpanded] = useState(false);
  const { data: detailedTrend, loading: detailLoading } = useTrend(
    trend.id,
    expanded // Only fetch detailed data when expanded
  );

  const handleExpand = async () => {
    setExpanded(!expanded);
  };

  // Strip HTML tags from description for preview
  const getDescriptionText = (html?: string) => {
    if (!html) return 'No description available';
    const div = document.createElement('div');
    div.innerHTML = html;
    return div.textContent || div.innerText || '';
  };

  return (
    <div style={styles.trendCard}>
      <div style={styles.cardLayout}>
        {/* Main Trend Image */}
        <div style={styles.imageSection}>
          <ImageWithFallback
            imageHash={trend.image_hash}
            alt={getImageAltText(trend.name)}
            style={styles.mainImage}
          />
          {trend.image_count > 0 && (
            <div style={styles.imageCountBadge}>
              📸 {trend.image_count}
            </div>
          )}
        </div>

        {/* Content Section */}
        <div style={styles.contentSection}>
          <div style={styles.trendHeader}>
            <h3 style={styles.trendName}>{trend.name}</h3>
            <div style={styles.trendMeta}>
              <span style={styles.trendId}>ID: {trend.trend_id.slice(0, 8)}...</span>
              <div style={styles.imageStats}>
                {trend.positive_image_count > 0 && (
                  <span style={styles.positiveCount}>
                    ✓{trend.positive_image_count}
                  </span>
                )}
                {trend.negative_image_count > 0 && (
                  <span style={styles.negativeCount}>
                    ✗{trend.negative_image_count}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div style={styles.trendContent}>
            <p style={styles.trendDescription}>
              {expanded
                ? getDescriptionText(trend.description)
                : `${getDescriptionText(trend.description).slice(0, 120)}${getDescriptionText(trend.description).length > 120 ? '...' : ''}`
              }
            </p>

            {(getDescriptionText(trend.description).length > 120 || trend.image_count > 0) && (
              <button
                onClick={handleExpand}
                style={styles.expandButton}
              >
                {expanded ? 'Show Less' : `Show More${trend.image_count > 0 ? ` (+${trend.image_count} images)` : ''}`}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {expanded && (
        <div style={styles.expandedContent}>
          {detailLoading ? (
            <div style={styles.loadingImages}>
              <div style={styles.miniSpinner}></div>
              <span>Loading images...</span>
            </div>
          ) : (
            detailedTrend?.images && detailedTrend.images.length > 0 && (
              <ImageGallery
                images={detailedTrend.images}
                trendName={trend.name}
                maxVisible={6}
              />
            )
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div style={styles.statCard}>
      <div style={styles.statValue}>{value.toLocaleString()}</div>
      <div style={styles.statLabel}>{label}</div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <div style={styles.loading}>
      <div style={styles.spinner}></div>
      <p>Loading trends...</p>
    </div>
  );
}

function ErrorMessage({ error }: { error: string }) {
  return (
    <div style={styles.error}>
      <h3>Error Loading Data</h3>
      <p>{error}</p>
      <p>Please make sure the API server is running on http://localhost:8001</p>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  header: {
    marginBottom: '24px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    marginBottom: '16px',
    color: '#1f2937',
  },
  stats: {
    display: 'flex',
    gap: '16px',
    marginBottom: '16px',
  },
  statCard: {
    backgroundColor: '#f8fafc',
    padding: '16px',
    borderRadius: '8px',
    textAlign: 'center',
    border: '1px solid #e5e7eb',
    minWidth: '100px',
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: '4px',
  },
  statLabel: {
    fontSize: '14px',
    color: '#6b7280',
    textTransform: 'uppercase' as const,
    letterSpacing: '0.5px',
  },
  filterSection: {
    backgroundColor: '#ffffff',
    padding: '20px',
    borderRadius: '12px',
    border: '1px solid #e5e7eb',
    marginBottom: '24px',
  },
  searchContainer: {
    display: 'flex',
    gap: '12px',
    marginBottom: '16px',
  },
  searchInput: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '16px',
  },
  searchButton: {
    padding: '12px 24px',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '600',
    cursor: 'pointer',
  },
  filtersContainer: {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
  },
  select: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    minWidth: '200px',
  },
  clearButton: {
    padding: '8px 16px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
  },
  trendsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
    gap: '20px',
    marginBottom: '24px',
  },
  trendCard: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    overflow: 'hidden',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    transition: 'box-shadow 0.2s, transform 0.2s',
  },
  cardLayout: {
    display: 'flex',
    gap: '16px',
    padding: '16px',
  },
  imageSection: {
    position: 'relative',
    minWidth: '120px',
    width: '120px',
  },
  mainImage: {
    width: '120px',
    height: '120px',
    borderRadius: '8px',
    objectFit: 'cover',
  },
  imageCountBadge: {
    position: 'absolute',
    bottom: '4px',
    right: '4px',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    color: 'white',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '10px',
    fontWeight: '600',
  },
  contentSection: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
  },
  trendHeader: {
    marginBottom: '8px',
  },
  trendName: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 6px 0',
    lineHeight: '1.2',
  },
  trendMeta: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    fontSize: '12px',
    color: '#6b7280',
  },
  trendId: {
    fontFamily: 'monospace',
    backgroundColor: '#f3f4f6',
    padding: '2px 6px',
    borderRadius: '4px',
  },
  imageStats: {
    display: 'flex',
    gap: '8px',
  },
  imageCount: {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  positiveCount: {
    color: '#059669',
    fontWeight: '600',
    backgroundColor: '#d1fae5',
    padding: '1px 4px',
    borderRadius: '3px',
    fontSize: '11px',
  },
  negativeCount: {
    color: '#dc2626',
    fontWeight: '600',
    backgroundColor: '#fee2e2',
    padding: '1px 4px',
    borderRadius: '3px',
    fontSize: '11px',
  },
  trendContent: {
    lineHeight: '1.5',
    flex: 1,
  },
  trendDescription: {
    fontSize: '13px',
    color: '#4b5563',
    margin: '0 0 8px 0',
    lineHeight: '1.4',
  },
  expandButton: {
    fontSize: '12px',
    color: '#3b82f6',
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    textDecoration: 'underline',
    padding: '4px 0',
    fontWeight: '500',
  },
  expandedContent: {
    borderTop: '1px solid #f3f4f6',
    padding: '16px',
    backgroundColor: '#fafbfc',
  },
  loadingImages: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    justifyContent: 'center',
    padding: '20px',
    color: '#6b7280',
  },
  miniSpinner: {
    width: '16px',
    height: '16px',
    border: '2px solid #f3f4f6',
    borderTop: '2px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  noResults: {
    gridColumn: '1 / -1',
    textAlign: 'center' as const,
    padding: '40px',
    color: '#6b7280',
  },
  pagination: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '16px',
    paddingTop: '20px',
    borderTop: '1px solid #e5e7eb',
  },
  pageButton: {
    padding: '8px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: '#ffffff',
    cursor: 'pointer',
    fontSize: '14px',
  },
  pageInfo: {
    fontSize: '14px',
    color: '#6b7280',
  },
  loading: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    padding: '60px',
    color: '#6b7280',
  },
  spinner: {
    width: '40px',
    height: '40px',
    border: '3px solid #f3f4f6',
    borderTop: '3px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    marginBottom: '16px',
  },
  error: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '20px',
    textAlign: 'center' as const,
    color: '#dc2626',
  },
};