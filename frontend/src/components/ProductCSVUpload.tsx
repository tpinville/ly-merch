import React, { useState } from "react";
import Papa from "papaparse";

// Product row interface for CSV parsing
export interface ProductRow {
  product_id?: string;
  name: string;
  product_type: string;
  description?: string;
  brand?: string;
  price?: number;
  currency?: string;
  color?: string;
  size?: string;
  material?: string;
  gender?: string;
  season?: string;
  availability_status?: string;
  image_url?: string;
  product_url?: string;
  trend_id?: number;
}

interface ProductCSVUploadProps {
  onRowsParsed?: (rows: ProductRow[]) => void;
  onUploadComplete?: (uploadedCount: number) => void;
  onError?: (error: string) => void;
  buttonLabel?: string;
  selectedTrendId?: number;
}

// Helper functions for data normalization
function normalizeGender(value: unknown): string {
  if (!value) return 'unisex';
  const str = String(value).trim().toLowerCase();
  if (['m', 'male', 'man', 'men'].includes(str)) return 'male';
  if (['f', 'female', 'woman', 'women'].includes(str)) return 'female';
  return 'unisex';
}

function normalizeAvailabilityStatus(value: unknown): string {
  if (!value) return 'in_stock';
  const str = String(value).trim().toLowerCase().replace(/\s+/g, '_');
  const validStatuses = ['in_stock', 'out_of_stock', 'discontinued', 'pre_order'];
  if (validStatuses.includes(str)) return str;

  // Map common variations
  if (['available', 'in stock', 'available'].includes(String(value).trim().toLowerCase())) return 'in_stock';
  if (['unavailable', 'out of stock', 'sold out'].includes(String(value).trim().toLowerCase())) return 'out_of_stock';
  if (['preorder', 'pre order', 'coming soon'].includes(String(value).trim().toLowerCase())) return 'pre_order';

  return 'in_stock';
}

function normalizePrice(value: unknown): number | undefined {
  if (value == null || value === '') return undefined;

  // Remove currency symbols and parse
  const cleaned = String(value).replace(/[$£€¥,]/g, '').trim();
  const price = parseFloat(cleaned);

  return Number.isFinite(price) && price >= 0 ? price : undefined;
}

function normalizeProductRow(r: Record<string, any>, defaultTrendId?: number): ProductRow {
  return {
    product_id: r.product_id ?? r.productId ?? r.id ?? r.sku ?? '',
    name: String(r.name ?? r.product_name ?? r.productName ?? r.title ?? '').trim(),
    product_type: String(r.product_type ?? r.productType ?? r.type ?? r.category ?? '').trim().toLowerCase(),
    description: r.description ?? r.desc ?? r.details ?? '',
    brand: r.brand ?? r.manufacturer ?? r.make ?? '',
    price: normalizePrice(r.price ?? r.cost ?? r.amount),
    currency: String(r.currency ?? r.curr ?? 'USD').toUpperCase(),
    color: r.color ?? r.colour ?? r.col ?? '',
    size: String(r.size ?? r.sz ?? '').trim(),
    material: r.material ?? r.fabric ?? r.materials ?? '',
    gender: normalizeGender(r.gender ?? r.sex ?? r.target),
    season: r.season ?? r.seasons ?? '',
    availability_status: normalizeAvailabilityStatus(r.availability_status ?? r.availability ?? r.status ?? r.stock),
    image_url: r.image_url ?? r.imageUrl ?? r.image ?? r.photo ?? r.picture ?? '',
    product_url: r.product_url ?? r.productUrl ?? r.url ?? r.link ?? '',
    trend_id: parseInt(r.trend_id ?? r.trendId ?? defaultTrendId ?? '') || defaultTrendId
  };
}

function validateProductRow(row: ProductRow): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  if (!row.name) errors.push('Product name is required');
  if (!row.product_type) errors.push('Product type is required');
  if (row.price !== undefined && (row.price < 0 || !Number.isFinite(row.price))) {
    errors.push('Price must be a valid positive number');
  }
  if (!['male', 'female', 'unisex'].includes(row.gender || '')) {
    errors.push('Gender must be male, female, or unisex');
  }
  if (!['in_stock', 'out_of_stock', 'discontinued', 'pre_order'].includes(row.availability_status || '')) {
    errors.push('Availability status must be one of: in_stock, out_of_stock, discontinued, pre_order');
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

export default function ProductCSVUpload({
  onRowsParsed,
  onUploadComplete,
  onError,
  buttonLabel = "Upload Product CSV",
  selectedTrendId
}: ProductCSVUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [parsedRows, setParsedRows] = useState<ProductRow[]>([]);
  const [validationErrors, setValidationErrors] = useState<Array<{row: number; errors: string[]}>>([]);
  const inputRef = React.useRef<HTMLInputElement | null>(null);

  const handlePickFile = () => {
    inputRef.current?.click();
  };

  const handleFileUpload = (file: File) => {
    setIsUploading(true);
    setUploadStatus('Parsing CSV file...');
    setValidationErrors([]);

    Papa.parse<Record<string, any>>(file, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim().toLowerCase().replace(/\s+/g, '_'),
      complete: (results) => {
        try {
          const rows = (results.data || []).map(r => normalizeProductRow(r, selectedTrendId));

          // Validate all rows
          const errors: Array<{row: number; errors: string[]}> = [];
          const validRows: ProductRow[] = [];

          rows.forEach((row, index) => {
            const validation = validateProductRow(row);
            if (!validation.isValid) {
              errors.push({ row: index + 1, errors: validation.errors });
            } else {
              validRows.push(row);
            }
          });

          setParsedRows(validRows);
          setValidationErrors(errors);

          if (errors.length > 0) {
            setUploadStatus(`Parsed ${validRows.length} valid products, ${errors.length} rows have errors`);
            onError?.(`${errors.length} rows have validation errors. Please fix them before uploading.`);
          } else {
            setUploadStatus(`Successfully parsed ${validRows.length} products`);
            onRowsParsed?.(validRows);
          }

        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Unknown parsing error';
          setUploadStatus('Failed to parse CSV file');
          onError?.(errorMessage);
          console.error('CSV parsing error:', error);
        } finally {
          setIsUploading(false);
        }
      },
      error: (error) => {
        const errorMessage = typeof error === 'string' ? error : error.message || 'CSV parsing failed';
        setUploadStatus('Failed to parse CSV file');
        onError?.(errorMessage);
        setIsUploading(false);
        console.error('Papa Parse error:', error);
      }
    });
  };

  const handleBulkUpload = async () => {
    if (parsedRows.length === 0) {
      onError?.('No valid products to upload');
      return;
    }

    setIsUploading(true);
    setUploadStatus(`Uploading ${parsedRows.length} products...`);

    try {
      const response = await fetch('http://localhost:8001/api/v1/products/bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ products: parsedRows })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      const uploadedCount = result.uploaded_count || parsedRows.length;

      setUploadStatus(`Successfully uploaded ${uploadedCount} products`);
      onUploadComplete?.(uploadedCount);

      // Clear the form
      setParsedRows([]);
      setValidationErrors([]);
      if (inputRef.current) {
        inputRef.current.value = '';
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      setUploadStatus('Upload failed');
      onError?.(errorMessage);
      console.error('Bulk upload error:', error);
    } finally {
      setIsUploading(false);
    }
  };

  const onChange: React.ChangeEventHandler<HTMLInputElement> = (e) => {
    const file = e.currentTarget.files?.[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const clearResults = () => {
    setParsedRows([]);
    setValidationErrors([]);
    setUploadStatus('');
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.uploadSection}>
        <input
          ref={inputRef}
          type="file"
          accept=".csv,text/csv"
          onChange={onChange}
          style={{ display: "none" }}
        />

        <div style={styles.buttonGroup}>
          <button
            type="button"
            onClick={handlePickFile}
            disabled={isUploading}
            style={{
              ...styles.button,
              ...(isUploading ? styles.buttonDisabled : styles.buttonPrimary)
            }}
          >
            {isUploading ? 'Processing...' : buttonLabel}
          </button>

          {parsedRows.length > 0 && (
            <>
              <button
                type="button"
                onClick={handleBulkUpload}
                disabled={isUploading || validationErrors.length > 0}
                style={{
                  ...styles.button,
                  ...(isUploading || validationErrors.length > 0 ? styles.buttonDisabled : styles.buttonSuccess)
                }}
              >
                {isUploading ? 'Uploading...' : `Upload ${parsedRows.length} Products`}
              </button>

              <button
                type="button"
                onClick={clearResults}
                disabled={isUploading}
                style={{
                  ...styles.button,
                  ...styles.buttonSecondary
                }}
              >
                Clear
              </button>
            </>
          )}
        </div>
      </div>

      {uploadStatus && (
        <div style={styles.statusMessage}>
          {uploadStatus}
        </div>
      )}

      {validationErrors.length > 0 && (
        <div style={styles.errorsSection}>
          <h4 style={styles.errorsTitle}>Validation Errors ({validationErrors.length} rows)</h4>
          <div style={styles.errorsList}>
            {validationErrors.slice(0, 10).map(({ row, errors }) => (
              <div key={row} style={styles.errorItem}>
                <strong>Row {row}:</strong>
                <ul style={styles.errorDetails}>
                  {errors.map((error, i) => (
                    <li key={i}>{error}</li>
                  ))}
                </ul>
              </div>
            ))}
            {validationErrors.length > 10 && (
              <div style={styles.moreErrors}>
                ... and {validationErrors.length - 10} more errors
              </div>
            )}
          </div>
        </div>
      )}

      {parsedRows.length > 0 && validationErrors.length === 0 && (
        <div style={styles.previewSection}>
          <h4 style={styles.previewTitle}>Preview ({parsedRows.length} products ready to upload)</h4>
          <div style={styles.previewTable}>
            <div style={styles.tableHeader}>
              <span>Name</span>
              <span>Type</span>
              <span>Brand</span>
              <span>Price</span>
              <span>Status</span>
            </div>
            {parsedRows.slice(0, 5).map((product, index) => (
              <div key={index} style={styles.tableRow}>
                <span title={product.name}>{product.name}</span>
                <span>{product.product_type}</span>
                <span>{product.brand || 'N/A'}</span>
                <span>{product.price ? `${product.currency} ${product.price}` : 'N/A'}</span>
                <span>{product.availability_status}</span>
              </div>
            ))}
            {parsedRows.length > 5 && (
              <div style={styles.moreRows}>
                ... and {parsedRows.length - 5} more products
              </div>
            )}
          </div>
        </div>
      )}

      <div style={styles.helpSection}>
        <h4 style={styles.helpTitle}>CSV Format Requirements</h4>
        <div style={styles.helpContent}>
          <div style={styles.helpColumn}>
            <strong>Required columns:</strong>
            <ul>
              <li>name (product name)</li>
              <li>product_type (sneakers, boots, etc.)</li>
            </ul>
          </div>
          <div style={styles.helpColumn}>
            <strong>Optional columns:</strong>
            <ul>
              <li>brand, description, price, currency</li>
              <li>color, size, material, season</li>
              <li>gender (male/female/unisex)</li>
              <li>availability_status (in_stock/out_of_stock/discontinued/pre_order)</li>
              <li>image_url, product_url</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    padding: '24px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e5e7eb',
  },
  uploadSection: {
    marginBottom: '20px',
  },
  buttonGroup: {
    display: 'flex',
    gap: '12px',
    flexWrap: 'wrap' as const,
  },
  button: {
    padding: '12px 20px',
    borderRadius: '8px',
    border: 'none',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '600',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  buttonPrimary: {
    backgroundColor: '#3b82f6',
    color: '#ffffff',
  },
  buttonSuccess: {
    backgroundColor: '#059669',
    color: '#ffffff',
  },
  buttonSecondary: {
    backgroundColor: '#f3f4f6',
    color: '#374151',
    border: '1px solid #d1d5db',
  },
  buttonDisabled: {
    backgroundColor: '#f3f4f6',
    color: '#9ca3af',
    cursor: 'not-allowed',
  },
  statusMessage: {
    padding: '12px 16px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #bae6fd',
    borderRadius: '8px',
    color: '#0c4a6e',
    fontSize: '14px',
    marginBottom: '20px',
  },
  errorsSection: {
    marginBottom: '20px',
  },
  errorsTitle: {
    color: '#dc2626',
    fontSize: '16px',
    fontWeight: 'bold',
    margin: '0 0 12px 0',
  },
  errorsList: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '16px',
    maxHeight: '300px',
    overflowY: 'auto' as const,
  },
  errorItem: {
    marginBottom: '12px',
    color: '#dc2626',
    fontSize: '14px',
  },
  errorDetails: {
    margin: '4px 0 0 16px',
    fontSize: '13px',
  },
  moreErrors: {
    fontStyle: 'italic',
    color: '#6b7280',
    fontSize: '13px',
    textAlign: 'center' as const,
    marginTop: '12px',
  },
  previewSection: {
    marginBottom: '20px',
  },
  previewTitle: {
    color: '#059669',
    fontSize: '16px',
    fontWeight: 'bold',
    margin: '0 0 12px 0',
  },
  previewTable: {
    border: '1px solid #d1d5db',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  tableHeader: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
    padding: '12px 16px',
    backgroundColor: '#f9fafb',
    borderBottom: '1px solid #e5e7eb',
    fontSize: '13px',
    fontWeight: 'bold',
    color: '#374151',
  },
  tableRow: {
    display: 'grid',
    gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
    padding: '12px 16px',
    borderBottom: '1px solid #f3f4f6',
    fontSize: '13px',
    color: '#6b7280',
  },
  moreRows: {
    padding: '12px 16px',
    textAlign: 'center' as const,
    fontStyle: 'italic',
    color: '#6b7280',
    fontSize: '13px',
    backgroundColor: '#f9fafb',
  },
  helpSection: {
    backgroundColor: '#f8fafc',
    border: '1px solid #e2e8f0',
    borderRadius: '8px',
    padding: '16px',
  },
  helpTitle: {
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#334155',
    margin: '0 0 12px 0',
  },
  helpContent: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '16px',
  },
  helpColumn: {
    fontSize: '13px',
    color: '#64748b',
  },
};