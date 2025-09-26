import React, { useState } from 'react';
import { useCategories } from '../services/api';
import type { Category } from '../types/api';

interface CategoriesListProps {
  onCategorySelect?: (category: Category) => void;
  selectedCategoryId?: number;
}

export default function CategoriesList({ onCategorySelect, selectedCategoryId }: CategoriesListProps) {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: categories, loading, error } = useCategories({
    query: searchQuery || undefined,
    limit: 50
  });

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  if (loading) {
    return <div style={styles.loading}>Loading categories...</div>;
  }

  if (error) {
    return <div style={styles.error}>Error: {error}</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h3 style={styles.title}>Product Categories</h3>
        <div style={styles.filters}>
          <input
            type="text"
            placeholder="Search categories..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            style={styles.searchInput}
          />
        </div>
      </div>

      <div style={styles.categoriesGrid}>
        {categories && categories.length > 0 ? (
          categories.map((category) => (
            <CategoryCard
              key={category.id}
              category={category}
              isSelected={selectedCategoryId === category.id}
              onClick={() => onCategorySelect?.(category)}
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

interface CategoryCardProps {
  category: Category;
  isSelected: boolean;
  onClick: () => void;
}

function CategoryCard({ category, isSelected, onClick }: CategoryCardProps) {
  return (
    <div
      style={{
        ...styles.categoryCard,
        ...(isSelected ? styles.categoryCardSelected : {}),
      }}
      onClick={onClick}
    >
      <div style={styles.categoryHeader}>
        <h4 style={styles.categoryName}>
          {category.name.charAt(0).toUpperCase() + category.name.slice(1)}
        </h4>
        <div style={styles.verticalCount}>
          <span style={styles.count}>{category.vertical_count}</span>
          <span style={styles.countLabel}>verticals</span>
        </div>
      </div>
      {category.description && (
        <p style={styles.categoryDescription}>
          {category.description}
        </p>
      )}
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
  categoriesGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '16px',
    padding: '20px',
  },
  categoryCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    padding: '20px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    backgroundColor: '#ffffff',
    ':hover': {
      backgroundColor: '#f8fafc',
      borderColor: '#3b82f6',
    },
  },
  categoryCardSelected: {
    backgroundColor: '#eff6ff',
    borderColor: '#3b82f6',
    borderWidth: '2px',
  },
  categoryHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: '12px',
  },
  categoryName: {
    margin: '0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
  },
  verticalCount: {
    textAlign: 'center' as const,
  },
  count: {
    display: 'block',
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#3b82f6',
    lineHeight: '1',
  },
  countLabel: {
    display: 'block',
    fontSize: '12px',
    color: '#6b7280',
    marginTop: '2px',
  },
  categoryDescription: {
    margin: '0',
    fontSize: '14px',
    color: '#6b7280',
    lineHeight: '1.5',
  },
  noResults: {
    gridColumn: '1 / -1',
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