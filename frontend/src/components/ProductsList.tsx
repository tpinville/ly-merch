import React, { useState, useEffect } from 'react';
import type { ProductSummary, ProductSearchParams } from '../types/api';
import ProductCSVUpload from './ProductCSVUpload';

interface ProductsListProps {
  selectedTrendId?: number;
  selectedCategoryId?: number;
  onProductSelect?: (product: ProductSummary) => void;
}

export default function ProductsList({
  selectedTrendId,
  selectedCategoryId,
  onProductSelect
}: ProductsListProps) {
  const [products, setProducts] = useState<ProductSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [showUpload, setShowUpload] = useState(false);
  const [filters, setFilters] = useState({
    product_type: '',
    brand: '',
    gender: '',
    availability_status: '',
    min_price: '',
    max_price: ''
  });

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);

      const params: ProductSearchParams = {
        limit: 50
      };

      if (searchQuery) params.query = searchQuery;
      if (selectedTrendId) params.trend_id = selectedTrendId;
      if (selectedCategoryId) params.category_id = selectedCategoryId;
      if (filters.product_type) params.product_type = filters.product_type;
      if (filters.brand) params.brand = filters.brand;
      if (filters.gender) params.gender = filters.gender;
      if (filters.availability_status) params.availability_status = filters.availability_status;
      if (filters.min_price) params.min_price = parseFloat(filters.min_price);
      if (filters.max_price) params.max_price = parseFloat(filters.max_price);

      const queryString = new URLSearchParams(
        Object.entries(params)
          .filter(([_, value]) => value !== undefined && value !== null && value !== '')
          .map(([key, value]) => [key, value.toString()])
      ).toString();

      const response = await fetch(`/api/v1/products${queryString ? `?${queryString}` : ''}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch products: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      setProducts(data);
    } catch (err) {
      console.error('Error fetching products:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch products');
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [selectedTrendId, selectedCategoryId, searchQuery, filters]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({
      product_type: '',
      brand: '',
      gender: '',
      availability_status: '',
      min_price: '',
      max_price: ''
    });
    setSearchQuery('');
  };

  const handleUploadComplete = (uploadedCount: number) => {
    // Refresh the products list after successful upload
    fetchProducts();
    setShowUpload(false);
    // You could show a success message here if needed
  };

  const handleUploadError = (errorMessage: string) => {
    setError(`Upload failed: ${errorMessage}`);
  };

  const formatPrice = (price?: number, currency: string = 'USD') => {
    if (price === undefined || price === null) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(price);
  };

  const getAvailabilityBadge = (status: string) => {
    const statusColors = {
      'in_stock': { bg: '#dcfce7', text: '#166534' },
      'out_of_stock': { bg: '#fee2e2', text: '#dc2626' },
      'discontinued': { bg: '#f3f4f6', text: '#6b7280' },
      'pre_order': { bg: '#fef3c7', text: '#92400e' }
    };

    const colors = statusColors[status as keyof typeof statusColors] || statusColors.in_stock;

    return (
      <span style={{
        ...styles.badge,
        backgroundColor: colors.bg,
        color: colors.text
      }}>
        {status.replace('_', ' ')}
      </span>
    );
  };

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading products...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.error}>
          <h3>Error loading products</h3>
          <p>{error}</p>
          <button onClick={fetchProducts} style={styles.retryButton}>
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.title}>Products ({products.length})</h2>

        <div style={styles.headerActions}>
          <div style={styles.searchBar}>
            <input
              type="text"
              placeholder="Search products..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={styles.searchInput}
            />
          </div>

          <button
            onClick={() => setShowUpload(!showUpload)}
            style={{
              ...styles.uploadButton,
              ...(showUpload ? styles.uploadButtonActive : {})
            }}
          >
            {showUpload ? 'Hide Upload' : 'Upload CSV'}
          </button>
        </div>
      </div>

      {showUpload && (
        <div style={styles.uploadSection}>
          <ProductCSVUpload
            onUploadComplete={handleUploadComplete}
            onError={handleUploadError}
            selectedTrendId={selectedTrendId}
            buttonLabel="Choose Products CSV"
          />
        </div>
      )}

      <div style={styles.filters}>
        <div style={styles.filterRow}>
          <select
            value={filters.product_type}
            onChange={(e) => handleFilterChange('product_type', e.target.value)}
            style={styles.filterSelect}
          >
            <option value="">All Types</option>
            <option value="sneakers">Sneakers</option>
            <option value="sandals">Sandals</option>
            <option value="boots">Boots</option>
            <option value="heels">Heels</option>
            <option value="flats">Flats</option>
            <option value="dress_shoes">Dress Shoes</option>
          </select>

          <input
            type="text"
            placeholder="Brand"
            value={filters.brand}
            onChange={(e) => handleFilterChange('brand', e.target.value)}
            style={styles.filterInput}
          />

          <select
            value={filters.gender}
            onChange={(e) => handleFilterChange('gender', e.target.value)}
            style={styles.filterSelect}
          >
            <option value="">All Genders</option>
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="unisex">Unisex</option>
          </select>

          <select
            value={filters.availability_status}
            onChange={(e) => handleFilterChange('availability_status', e.target.value)}
            style={styles.filterSelect}
          >
            <option value="">All Status</option>
            <option value="in_stock">In Stock</option>
            <option value="out_of_stock">Out of Stock</option>
            <option value="discontinued">Discontinued</option>
            <option value="pre_order">Pre Order</option>
          </select>
        </div>

        <div style={styles.filterRow}>
          <input
            type="number"
            placeholder="Min Price"
            value={filters.min_price}
            onChange={(e) => handleFilterChange('min_price', e.target.value)}
            style={styles.filterInput}
          />
          <input
            type="number"
            placeholder="Max Price"
            value={filters.max_price}
            onChange={(e) => handleFilterChange('max_price', e.target.value)}
            style={styles.filterInput}
          />

          <button onClick={clearFilters} style={styles.clearButton}>
            Clear Filters
          </button>
        </div>
      </div>

      {products.length === 0 ? (
        <div style={styles.emptyState}>
          <h3>No products found</h3>
          <p>Try adjusting your search or filters</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {products.map((product) => (
            <div
              key={product.id}
              style={styles.productCard}
              onClick={() => onProductSelect?.(product)}
            >
              {product.image_url && (
                <div style={styles.imageContainer}>
                  <img
                    src={product.image_url}
                    alt={product.name}
                    style={styles.productImage}
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                </div>
              )}

              <div style={styles.productInfo}>
                <h3 style={styles.productName}>{product.name}</h3>
                <div style={styles.productMeta}>
                  <span style={styles.productType}>{product.product_type}</span>
                  {product.brand && <span style={styles.brand}>{product.brand}</span>}
                </div>

                <div style={styles.priceRow}>
                  <span style={styles.price}>
                    {formatPrice(product.price, product.currency)}
                  </span>
                  {getAvailabilityBadge(product.availability_status)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '20px',
    gap: '20px',
    flexWrap: 'wrap' as const,
  },
  title: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: 0,
  },
  headerActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    flex: 1,
    justifyContent: 'flex-end',
  },
  searchBar: {
    flex: 1,
    maxWidth: '300px',
  },
  searchInput: {
    width: '100%',
    padding: '10px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '14px',
  },
  filters: {
    marginBottom: '20px',
    padding: '16px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
  },
  filterRow: {
    display: 'flex',
    gap: '12px',
    marginBottom: '12px',
    flexWrap: 'wrap' as const,
  },
  filterSelect: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: '#ffffff',
    minWidth: '120px',
  },
  filterInput: {
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    minWidth: '100px',
  },
  clearButton: {
    padding: '8px 16px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    color: '#374151',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px',
  },
  productCard: {
    border: '1px solid #e5e7eb',
    borderRadius: '12px',
    overflow: 'hidden',
    backgroundColor: '#ffffff',
    cursor: 'pointer',
    transition: 'all 0.2s',
    ':hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
    },
  },
  imageContainer: {
    height: '200px',
    backgroundColor: '#f3f4f6',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  productImage: {
    width: '100%',
    height: '100%',
    objectFit: 'cover' as const,
  },
  productInfo: {
    padding: '16px',
  },
  productName: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 8px 0',
    lineHeight: '1.4',
  },
  productMeta: {
    display: 'flex',
    gap: '8px',
    marginBottom: '12px',
    flexWrap: 'wrap' as const,
  },
  productType: {
    fontSize: '12px',
    color: '#6b7280',
    backgroundColor: '#f3f4f6',
    padding: '2px 8px',
    borderRadius: '4px',
    textTransform: 'capitalize' as const,
  },
  brand: {
    fontSize: '12px',
    color: '#3b82f6',
    fontWeight: '500',
  },
  priceRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  price: {
    fontSize: '16px',
    fontWeight: 'bold',
    color: '#059669',
  },
  badge: {
    fontSize: '11px',
    fontWeight: '500',
    padding: '2px 8px',
    borderRadius: '12px',
    textTransform: 'capitalize' as const,
  },
  loading: {
    textAlign: 'center' as const,
    padding: '60px 20px',
    color: '#6b7280',
    fontSize: '16px',
  },
  error: {
    textAlign: 'center' as const,
    padding: '40px 20px',
    color: '#dc2626',
  },
  retryButton: {
    marginTop: '10px',
    padding: '8px 16px',
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
  },
  emptyState: {
    textAlign: 'center' as const,
    padding: '60px 20px',
    color: '#6b7280',
  },
  uploadButton: {
    padding: '10px 16px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap' as const,
  },
  uploadButtonActive: {
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    borderColor: '#3b82f6',
  },
  uploadSection: {
    marginBottom: '24px',
    padding: '20px',
    backgroundColor: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
  },
};