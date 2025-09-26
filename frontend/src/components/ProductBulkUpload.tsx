import React, { useState, useCallback, useRef } from 'react';
import Papa from 'papaparse';

// Product row interface for CSV parsing
interface ProductUploadRow {
  name: string;
  product_type: string;
  brand?: string;
  price?: number;
  currency?: string;
  color?: string;
  size?: string;
  material?: string;
  gender?: string;
  season?: string;
  availability_status?: string;
  description?: string;
  image_url?: string;
  product_url?: string;
  trend_id?: number;
  analyze_image?: boolean;
}

interface UploadResult {
  uploaded_count: number;
  skipped_count: number;
  error_count: number;
  errors?: string[];
  analysis_count?: number;
  analysis_results?: Array<{
    product_id: string;
    image_url: string;
    analysis: any;
  }>;
}

interface ProcessingStats {
  total: number;
  processed: number;
  successful: number;
  errors: number;
  current_batch: number;
  total_batches: number;
}

export default function ProductBulkUpload() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStats, setProcessingStats] = useState<ProcessingStats | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResult | null>(null);
  const [parsedProducts, setParsedProducts] = useState<ProductUploadRow[]>([]);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [statusMessage, setStatusMessage] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Data normalization functions
  const normalizeGender = (value: unknown): string => {
    if (!value) return 'unisex';
    const str = String(value).trim().toLowerCase();
    if (['m', 'male', 'man', 'men'].includes(str)) return 'male';
    if (['f', 'female', 'woman', 'women'].includes(str)) return 'female';
    return 'unisex';
  };

  const normalizeAvailability = (value: unknown): string => {
    if (!value) return 'in_stock';
    const str = String(value).trim().toLowerCase().replace(/\s+/g, '_');
    const validStatuses = ['in_stock', 'out_of_stock', 'discontinued', 'pre_order'];

    if (validStatuses.includes(str)) return str;

    // Map common variations
    if (['available', 'in stock', 'stocked'].includes(String(value).trim().toLowerCase())) return 'in_stock';
    if (['unavailable', 'out of stock', 'sold out'].includes(String(value).trim().toLowerCase())) return 'out_of_stock';
    if (['preorder', 'pre order', 'coming soon'].includes(String(value).trim().toLowerCase())) return 'pre_order';

    return 'in_stock';
  };

  const normalizePrice = (value: unknown): number | undefined => {
    if (value == null || value === '') return undefined;

    // Remove currency symbols and parse
    const cleaned = String(value).replace(/[$£€¥,]/g, '').trim();
    const price = parseFloat(cleaned);

    return Number.isFinite(price) && price >= 0 ? price : undefined;
  };

  // CSV processing
  const processCSVFile = useCallback((file: File) => {
    setStatusMessage('Parsing CSV file...');
    setValidationErrors([]);
    setParsedProducts([]);
    setUploadResult(null);

    Papa.parse<Record<string, any>>(file, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.trim().toLowerCase().replace(/\s+/g, '_'),
      complete: (results) => {
        const products: ProductUploadRow[] = [];
        const errors: string[] = [];

        results.data.forEach((row, index) => {
          try {
            const product: ProductUploadRow = {
              name: String(row.name || row.product_name || row.title || '').trim(),
              product_type: String(row.product_type || row.type || row.category || '').trim().toLowerCase(),
              brand: row.brand || row.manufacturer || '',
              price: normalizePrice(row.price || row.cost),
              currency: String(row.currency || 'USD').toUpperCase(),
              color: row.color || row.colour || '',
              size: String(row.size || '').trim(),
              material: row.material || row.fabric || '',
              gender: normalizeGender(row.gender || row.target),
              season: row.season || '',
              availability_status: normalizeAvailability(row.availability_status || row.status || row.stock),
              description: row.description || row.desc || '',
              image_url: row.image_url || row.image || row.photo || '',
              product_url: row.product_url || row.url || row.link || '',
              trend_id: parseInt(row.trend_id || '1') || 1
            };

            // Validate required fields
            if (!product.name) {
              errors.push(`Row ${index + 2}: Product name is required`);
              return;
            }
            if (!product.product_type) {
              errors.push(`Row ${index + 2}: Product type is required`);
              return;
            }

            products.push(product);
          } catch (error) {
            errors.push(`Row ${index + 2}: ${error instanceof Error ? error.message : 'Parsing error'}`);
          }
        });

        setParsedProducts(products);
        setValidationErrors(errors);

        if (errors.length > 0) {
          setStatusMessage(`Parsed ${products.length} valid products, ${errors.length} errors found`);
        } else {
          setStatusMessage(`Successfully parsed ${products.length} products - ready to upload`);
        }
      },
      error: (error) => {
        setValidationErrors([`CSV parsing failed: ${error.message}`]);
        setStatusMessage('Failed to parse CSV file');
      }
    });
  }, []);

  // File upload handlers
  const handleFileSelect = (file: File) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setValidationErrors(['Please select a CSV file']);
      return;
    }
    processCSVFile(file);
  };

  const handleFileInput = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleDragOver = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);

    const file = event.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  // Batch upload processing
  const uploadProductsBatch = async (products: ProductUploadRow[], batchSize: number = 10) => {
    setIsProcessing(true);
    setUploadProgress(0);

    const totalBatches = Math.ceil(products.length / batchSize);
    let totalUploaded = 0;
    let totalSkipped = 0;
    let totalErrors = 0;
    const allErrors: string[] = [];

    try {
      for (let i = 0; i < totalBatches; i++) {
        const startIndex = i * batchSize;
        const endIndex = Math.min(startIndex + batchSize, products.length);
        const batch = products.slice(startIndex, endIndex);

        setProcessingStats({
          total: products.length,
          processed: startIndex,
          successful: totalUploaded,
          errors: totalErrors,
          current_batch: i + 1,
          total_batches: totalBatches
        });

        setStatusMessage(`Uploading batch ${i + 1} of ${totalBatches} (${batch.length} products)...`);

        try {
          const response = await fetch('http://localhost:8001/api/v1/products/bulk', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ products: batch })
          });

          if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
            throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
          }

          const result = await response.json();
          totalUploaded += result.uploaded_count || 0;
          totalSkipped += result.skipped_count || 0;
          totalErrors += result.error_count || 0;

          if (result.errors && result.errors.length > 0) {
            allErrors.push(...result.errors);
          }

          // Update progress
          const progressPercent = Math.round(((i + 1) / totalBatches) * 100);
          setUploadProgress(progressPercent);

          // Small delay between batches to prevent overwhelming the server
          if (i < totalBatches - 1) {
            await new Promise(resolve => setTimeout(resolve, 500));
          }

        } catch (error) {
          console.error(`Batch ${i + 1} failed:`, error);
          totalErrors += batch.length;
          allErrors.push(`Batch ${i + 1} failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
      }

      // Final results
      const finalResult: UploadResult = {
        uploaded_count: totalUploaded,
        skipped_count: totalSkipped,
        error_count: totalErrors,
        errors: allErrors.length > 0 ? allErrors : undefined
      };

      setUploadResult(finalResult);
      setProcessingStats({
        total: products.length,
        processed: products.length,
        successful: totalUploaded,
        errors: totalErrors,
        current_batch: totalBatches,
        total_batches: totalBatches
      });

      if (totalUploaded > 0) {
        setStatusMessage(`Upload complete! Successfully uploaded ${totalUploaded} products`);
      } else {
        setStatusMessage(`Upload finished with issues. ${totalErrors} errors occurred.`);
      }

    } catch (error) {
      console.error('Upload process failed:', error);
      setStatusMessage(`Upload failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsProcessing(false);
      setUploadProgress(100);
    }
  };

  const startUpload = () => {
    if (parsedProducts.length === 0) {
      setValidationErrors(['No products to upload']);
      return;
    }
    uploadProductsBatch(parsedProducts);
  };

  const resetUpload = () => {
    setParsedProducts([]);
    setValidationErrors([]);
    setUploadResult(null);
    setProcessingStats(null);
    setUploadProgress(0);
    setStatusMessage('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Bulk Product Upload</h1>
        <p style={styles.subtitle}>Upload CSV files to populate the products database</p>
      </div>

      {/* File Upload Area */}
      <div
        style={{
          ...styles.uploadArea,
          ...(isDragOver ? styles.uploadAreaActive : {}),
          ...(parsedProducts.length > 0 ? styles.uploadAreaSuccess : {})
        }}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,text/csv"
          onChange={handleFileInput}
          style={{ display: 'none' }}
          disabled={isProcessing}
        />

        <div style={styles.uploadContent}>
          <div style={styles.uploadIcon}>📁</div>
          <h3 style={styles.uploadTitle}>
            {parsedProducts.length > 0 ? 'CSV File Loaded' : 'Choose CSV File'}
          </h3>
          <p style={styles.uploadText}>
            {parsedProducts.length > 0
              ? `${parsedProducts.length} products ready to upload`
              : 'Drag and drop your CSV file here, or click to browse'
            }
          </p>
          {!isProcessing && (
            <button style={styles.browseButton} type="button">
              {parsedProducts.length > 0 ? 'Choose Different File' : 'Browse Files'}
            </button>
          )}
        </div>
      </div>

      {/* Status Message */}
      {statusMessage && (
        <div style={styles.statusMessage}>
          {statusMessage}
        </div>
      )}

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <div style={styles.errorsSection}>
          <h3 style={styles.errorsTitle}>Validation Errors</h3>
          <div style={styles.errorsList}>
            {validationErrors.slice(0, 10).map((error, index) => (
              <div key={index} style={styles.errorItem}>
                {error}
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

      {/* Processing Progress */}
      {(isProcessing || processingStats) && (
        <div style={styles.progressSection}>
          <h3 style={styles.progressTitle}>Upload Progress</h3>

          {processingStats && (
            <div style={styles.statsGrid}>
              <div style={styles.statItem}>
                <div style={styles.statValue}>{processingStats.processed}</div>
                <div style={styles.statLabel}>Processed</div>
              </div>
              <div style={styles.statItem}>
                <div style={styles.statValue}>{processingStats.successful}</div>
                <div style={styles.statLabel}>Successful</div>
              </div>
              <div style={styles.statItem}>
                <div style={styles.statValue}>{processingStats.errors}</div>
                <div style={styles.statLabel}>Errors</div>
              </div>
              <div style={styles.statItem}>
                <div style={styles.statValue}>{processingStats.current_batch}/{processingStats.total_batches}</div>
                <div style={styles.statLabel}>Batches</div>
              </div>
            </div>
          )}

          <div style={styles.progressBar}>
            <div
              style={{
                ...styles.progressFill,
                width: `${uploadProgress}%`
              }}
            />
          </div>
          <div style={styles.progressText}>{uploadProgress}% Complete</div>
        </div>
      )}

      {/* Upload Results */}
      {uploadResult && (
        <div style={styles.resultsSection}>
          <h3 style={styles.resultsTitle}>Upload Results</h3>
          <div style={styles.resultsGrid}>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{uploadResult.uploaded_count}</div>
              <div style={styles.resultLabel}>Uploaded</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{uploadResult.skipped_count}</div>
              <div style={styles.resultLabel}>Skipped</div>
            </div>
            <div style={styles.resultItem}>
              <div style={styles.resultValue}>{uploadResult.error_count}</div>
              <div style={styles.resultLabel}>Errors</div>
            </div>
          </div>

          {uploadResult.errors && uploadResult.errors.length > 0 && (
            <div style={styles.uploadErrors}>
              <h4 style={styles.uploadErrorsTitle}>Error Details</h4>
              <div style={styles.uploadErrorsList}>
                {uploadResult.errors.slice(0, 5).map((error, index) => (
                  <div key={index} style={styles.uploadErrorItem}>
                    {error}
                  </div>
                ))}
                {uploadResult.errors.length > 5 && (
                  <div style={styles.moreUploadErrors}>
                    ... and {uploadResult.errors.length - 5} more errors
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Action Buttons */}
      <div style={styles.actionButtons}>
        {parsedProducts.length > 0 && !isProcessing && !uploadResult && (
          <button
            onClick={startUpload}
            disabled={validationErrors.length > 0}
            style={{
              ...styles.button,
              ...styles.primaryButton,
              ...(validationErrors.length > 0 ? styles.disabledButton : {})
            }}
          >
            Upload {parsedProducts.length} Products
          </button>
        )}

        {(uploadResult || parsedProducts.length > 0) && !isProcessing && (
          <button
            onClick={resetUpload}
            style={{
              ...styles.button,
              ...styles.secondaryButton
            }}
          >
            Start Over
          </button>
        )}
      </div>

      {/* Help Section */}
      <div style={styles.helpSection}>
        <h3 style={styles.helpTitle}>CSV Format Guide</h3>
        <div style={styles.helpGrid}>
          <div style={styles.helpColumn}>
            <h4 style={styles.helpSubtitle}>Required Columns</h4>
            <ul style={styles.helpList}>
              <li>name - Product name</li>
              <li>product_type - sneakers, sandals, boots, etc.</li>
            </ul>
          </div>
          <div style={styles.helpColumn}>
            <h4 style={styles.helpSubtitle}>Optional Columns</h4>
            <ul style={styles.helpList}>
              <li>brand, price, currency, color, size</li>
              <li>material, season, description</li>
              <li>gender (male/female/unisex)</li>
              <li>availability_status, image_url, product_url</li>
            </ul>
          </div>
        </div>

        <div style={styles.helpTips}>
          <h4 style={styles.helpSubtitle}>Tips for Best Results</h4>
          <ul style={styles.helpList}>
            <li>Use standard column headers (case-insensitive)</li>
            <li>Price values can include currency symbols ($, €, £)</li>
            <li>Status values: available, in stock, out of stock, discontinued</li>
            <li>Files are processed in batches to ensure reliability</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    maxWidth: '800px',
    margin: '0 auto',
    padding: '24px',
    fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial',
  },
  header: {
    textAlign: 'center' as const,
    marginBottom: '32px',
  },
  title: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1f2937',
    margin: '0 0 8px 0',
  },
  subtitle: {
    fontSize: '16px',
    color: '#6b7280',
    margin: 0,
  },
  uploadArea: {
    border: '2px dashed #d1d5db',
    borderRadius: '12px',
    padding: '48px 24px',
    textAlign: 'center' as const,
    cursor: 'pointer',
    transition: 'all 0.2s',
    backgroundColor: '#fafafa',
    marginBottom: '24px',
  },
  uploadAreaActive: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  uploadAreaSuccess: {
    borderColor: '#059669',
    backgroundColor: '#f0fdf4',
  },
  uploadContent: {
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    gap: '16px',
  },
  uploadIcon: {
    fontSize: '48px',
  },
  uploadTitle: {
    fontSize: '20px',
    fontWeight: '600',
    color: '#374151',
    margin: 0,
  },
  uploadText: {
    fontSize: '14px',
    color: '#6b7280',
    margin: 0,
  },
  browseButton: {
    padding: '12px 24px',
    backgroundColor: '#3b82f6',
    color: '#ffffff',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  },
  statusMessage: {
    padding: '16px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #bae6fd',
    borderRadius: '8px',
    color: '#0c4a6e',
    fontSize: '14px',
    marginBottom: '24px',
    textAlign: 'center' as const,
  },
  errorsSection: {
    marginBottom: '24px',
  },
  errorsTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#dc2626',
    margin: '0 0 12px 0',
  },
  errorsList: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '16px',
    maxHeight: '200px',
    overflowY: 'auto' as const,
  },
  errorItem: {
    fontSize: '14px',
    color: '#dc2626',
    marginBottom: '8px',
  },
  moreErrors: {
    fontSize: '13px',
    color: '#9ca3af',
    fontStyle: 'italic',
    textAlign: 'center' as const,
  },
  progressSection: {
    marginBottom: '24px',
    padding: '20px',
    backgroundColor: '#f8fafc',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
  },
  progressTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 16px 0',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '16px',
    marginBottom: '20px',
  },
  statItem: {
    textAlign: 'center' as const,
  },
  statValue: {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#3b82f6',
  },
  statLabel: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'uppercase' as const,
    fontWeight: '500',
  },
  progressBar: {
    width: '100%',
    height: '8px',
    backgroundColor: '#e5e7eb',
    borderRadius: '4px',
    overflow: 'hidden',
    marginBottom: '8px',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#3b82f6',
    transition: 'width 0.3s ease',
  },
  progressText: {
    textAlign: 'center' as const,
    fontSize: '14px',
    color: '#6b7280',
  },
  resultsSection: {
    marginBottom: '24px',
    padding: '20px',
    backgroundColor: '#f0fdf4',
    borderRadius: '12px',
    border: '1px solid #bbf7d0',
  },
  resultsTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#059669',
    margin: '0 0 16px 0',
  },
  resultsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
    gap: '16px',
    marginBottom: '16px',
  },
  resultItem: {
    textAlign: 'center' as const,
  },
  resultValue: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#059669',
  },
  resultLabel: {
    fontSize: '12px',
    color: '#065f46',
    textTransform: 'uppercase' as const,
    fontWeight: '500',
  },
  uploadErrors: {
    marginTop: '16px',
  },
  uploadErrorsTitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#dc2626',
    margin: '0 0 8px 0',
  },
  uploadErrorsList: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '6px',
    padding: '12px',
    maxHeight: '150px',
    overflowY: 'auto' as const,
  },
  uploadErrorItem: {
    fontSize: '12px',
    color: '#dc2626',
    marginBottom: '6px',
  },
  moreUploadErrors: {
    fontSize: '11px',
    color: '#9ca3af',
    fontStyle: 'italic',
    textAlign: 'center' as const,
  },
  actionButtons: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    marginBottom: '32px',
  },
  button: {
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s',
    border: 'none',
  },
  primaryButton: {
    backgroundColor: '#059669',
    color: '#ffffff',
  },
  secondaryButton: {
    backgroundColor: '#f3f4f6',
    color: '#374151',
    border: '1px solid #d1d5db',
  },
  disabledButton: {
    backgroundColor: '#e5e7eb',
    color: '#9ca3af',
    cursor: 'not-allowed',
  },
  helpSection: {
    padding: '24px',
    backgroundColor: '#f8fafc',
    borderRadius: '12px',
    border: '1px solid #e2e8f0',
  },
  helpTitle: {
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 16px 0',
  },
  helpGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '20px',
    marginBottom: '20px',
  },
  helpColumn: {
    // No specific styles needed
  },
  helpSubtitle: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#374151',
    margin: '0 0 8px 0',
  },
  helpList: {
    fontSize: '13px',
    color: '#6b7280',
    paddingLeft: '16px',
    margin: 0,
  },
  helpTips: {
    borderTop: '1px solid #e2e8f0',
    paddingTop: '16px',
  },
};