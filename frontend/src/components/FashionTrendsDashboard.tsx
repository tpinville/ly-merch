import React, { useState } from 'react';
import TrendsViewer from './TrendsViewer';
import VerticalsList from './VerticalsList';
import type { Vertical } from '../types/api';

type ViewMode = 'dashboard' | 'trends' | 'verticals';

export default function FashionTrendsDashboard() {
  const [viewMode, setViewMode] = useState<ViewMode>('dashboard');
  const [selectedVertical, setSelectedVertical] = useState<Vertical | null>(null);

  const handleVerticalSelect = (vertical: Vertical) => {
    setSelectedVertical(vertical);
    setViewMode('trends');
  };

  return (
    <div style={styles.container}>
      {/* Navigation */}
      <nav style={styles.nav}>
        <div style={styles.navBrand}>
          <h1 style={styles.brandText}>Fashion Trends</h1>
          <span style={styles.brandSubtext}>Database Explorer</span>
        </div>
        <div style={styles.navItems}>
          <button
            onClick={() => setViewMode('dashboard')}
            style={{
              ...styles.navButton,
              ...(viewMode === 'dashboard' ? styles.navButtonActive : {}),
            }}
          >
            Dashboard
          </button>
          <button
            onClick={() => setViewMode('trends')}
            style={{
              ...styles.navButton,
              ...(viewMode === 'trends' ? styles.navButtonActive : {}),
            }}
          >
            Trends
          </button>
          <button
            onClick={() => setViewMode('verticals')}
            style={{
              ...styles.navButton,
              ...(viewMode === 'verticals' ? styles.navButtonActive : {}),
            }}
          >
            Categories
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main style={styles.main}>
        {viewMode === 'dashboard' && (
          <div style={styles.dashboardLayout}>
            <div style={styles.sidebar}>
              <VerticalsList
                onVerticalSelect={handleVerticalSelect}
                selectedVerticalId={selectedVertical?.id}
              />
            </div>
            <div style={styles.content}>
              <TrendsViewer />
            </div>
          </div>
        )}

        {viewMode === 'trends' && (
          <div style={styles.fullContent}>
            {selectedVertical && (
              <div style={styles.breadcrumb}>
                <button
                  onClick={() => setViewMode('dashboard')}
                  style={styles.breadcrumbButton}
                >
                  ← Back to Dashboard
                </button>
                <span style={styles.breadcrumbText}>
                  Viewing trends in: <strong>{selectedVertical.name}</strong>
                </span>
              </div>
            )}
            <TrendsViewer />
          </div>
        )}

        {viewMode === 'verticals' && (
          <div style={styles.fullContent}>
            <VerticalsList onVerticalSelect={handleVerticalSelect} />
          </div>
        )}
      </main>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
    fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
  },
  nav: {
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
    padding: '16px 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    position: 'sticky' as const,
    top: 0,
    zIndex: 10,
  },
  navBrand: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '12px',
  },
  brandText: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  brandSubtext: {
    fontSize: '14px',
    color: '#6b7280',
    fontWeight: '500',
  },
  navItems: {
    display: 'flex',
    gap: '8px',
  },
  navButton: {
    padding: '10px 16px',
    border: 'none',
    backgroundColor: 'transparent',
    color: '#6b7280',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    transition: 'all 0.2s',
  },
  navButtonActive: {
    backgroundColor: '#3b82f6',
    color: '#ffffff',
  },
  main: {
    padding: '24px',
    maxWidth: '1400px',
    margin: '0 auto',
  },
  dashboardLayout: {
    display: 'grid',
    gridTemplateColumns: '350px 1fr',
    gap: '24px',
    alignItems: 'start',
  },
  sidebar: {
    position: 'sticky' as const,
    top: '100px',
  },
  content: {
    minHeight: '600px',
  },
  fullContent: {
    width: '100%',
  },
  breadcrumb: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '20px',
    padding: '12px 0',
  },
  breadcrumbButton: {
    padding: '8px 12px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#374151',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
  },
  breadcrumbText: {
    fontSize: '14px',
    color: '#6b7280',
  },

  // Responsive styles
  '@media (max-width: 1024px)': {
    dashboardLayout: {
      gridTemplateColumns: '1fr',
      gap: '16px',
    },
    sidebar: {
      position: 'relative' as const,
    },
    main: {
      padding: '16px',
    },
  },
};