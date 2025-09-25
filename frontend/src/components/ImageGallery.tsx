import React, { useState } from 'react';
import ImageWithFallback from './ImageWithFallback';
import { getImageAltText } from '../utils/imageUtils';
import type { TrendImage } from '../types/api';

interface ImageGalleryProps {
  images: TrendImage[];
  trendName: string;
  maxVisible?: number;
  showTypes?: boolean;
}

export default function ImageGallery({
  images,
  trendName,
  maxVisible = 6,
  showTypes = true
}: ImageGalleryProps) {
  const [selectedImage, setSelectedImage] = useState<TrendImage | null>(null);
  const [showAll, setShowAll] = useState(false);

  if (!images || images.length === 0) {
    return (
      <div style={styles.emptyState}>
        <span style={styles.emptyText}>No images available</span>
      </div>
    );
  }

  const visibleImages = showAll ? images : images.slice(0, maxVisible);
  const remainingCount = images.length - maxVisible;

  const positiveImages = images.filter(img => img.image_type === 'positive');
  const negativeImages = images.filter(img => img.image_type === 'negative');

  return (
    <div style={styles.container}>
      {/* Image Type Summary */}
      {showTypes && (
        <div style={styles.summary}>
          <div style={styles.summaryItem}>
            <span style={styles.positiveLabel}>✓ Positive Examples</span>
            <span style={styles.count}>{positiveImages.length}</span>
          </div>
          <div style={styles.summaryItem}>
            <span style={styles.negativeLabel}>✗ Negative Examples</span>
            <span style={styles.count}>{negativeImages.length}</span>
          </div>
        </div>
      )}

      {/* Image Grid */}
      <div style={styles.grid}>
        {visibleImages.map((image) => (
          <div
            key={image.id}
            style={{
              ...styles.imageContainer,
              ...(image.image_type === 'positive'
                ? styles.positiveContainer
                : styles.negativeContainer)
            }}
            onClick={() => setSelectedImage(image)}
          >
            <ImageWithFallback
              imageHash={image.md5_hash}
              alt={getImageAltText(trendName, image.image_type, image.description)}
              style={styles.image}
            />
            <div style={styles.imageOverlay}>
              <span style={styles.imageType}>
                {image.image_type === 'positive' ? '✓' : '✗'}
              </span>
            </div>
            {image.description && (
              <div style={styles.imageDescription}>
                {image.description.length > 50
                  ? `${image.description.slice(0, 50)}...`
                  : image.description
                }
              </div>
            )}
          </div>
        ))}

        {/* Show More Button */}
        {!showAll && remainingCount > 0 && (
          <div
            style={styles.showMoreContainer}
            onClick={() => setShowAll(true)}
          >
            <div style={styles.showMoreContent}>
              <span style={styles.showMoreText}>+{remainingCount}</span>
              <span style={styles.showMoreSubtext}>more images</span>
            </div>
          </div>
        )}
      </div>

      {/* Show Less Button */}
      {showAll && images.length > maxVisible && (
        <button
          onClick={() => setShowAll(false)}
          style={styles.showLessButton}
        >
          Show Less
        </button>
      )}

      {/* Image Modal */}
      {selectedImage && (
        <ImageModal
          image={selectedImage}
          trendName={trendName}
          onClose={() => setSelectedImage(null)}
        />
      )}
    </div>
  );
}

interface ImageModalProps {
  image: TrendImage;
  trendName: string;
  onClose: () => void;
}

function ImageModal({ image, trendName, onClose }: ImageModalProps) {
  return (
    <div style={styles.modalOverlay} onClick={onClose}>
      <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div style={styles.modalHeader}>
          <div>
            <h3 style={styles.modalTitle}>{trendName}</h3>
            <span style={{
              ...styles.modalType,
              color: image.image_type === 'positive' ? '#059669' : '#dc2626'
            }}>
              {image.image_type === 'positive' ? '✓ Positive Example' : '✗ Negative Example'}
            </span>
          </div>
          <button onClick={onClose} style={styles.closeButton}>×</button>
        </div>

        <div style={styles.modalImageContainer}>
          <ImageWithFallback
            imageHash={image.md5_hash}
            alt={getImageAltText(trendName, image.image_type, image.description)}
            style={styles.modalImage}
          />
        </div>

        {image.description && (
          <div style={styles.modalDescription}>
            <p style={styles.descriptionText}>{image.description}</p>
          </div>
        )}

        <div style={styles.modalInfo}>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Image ID:</span>
            <span style={styles.infoValue}>{image.md5_hash.slice(0, 8)}...</span>
          </div>
          <div style={styles.infoItem}>
            <span style={styles.infoLabel}>Added:</span>
            <span style={styles.infoValue}>
              {new Date(image.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    marginTop: '16px',
  },
  summary: {
    display: 'flex',
    gap: '16px',
    marginBottom: '12px',
    padding: '12px',
    backgroundColor: '#f8fafc',
    borderRadius: '8px',
    border: '1px solid #e5e7eb',
  },
  summaryItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  positiveLabel: {
    color: '#059669',
    fontSize: '14px',
    fontWeight: '500',
  },
  negativeLabel: {
    color: '#dc2626',
    fontSize: '14px',
    fontWeight: '500',
  },
  count: {
    backgroundColor: '#ffffff',
    padding: '2px 6px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: 'bold',
    minWidth: '20px',
    textAlign: 'center',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(120px, 1fr))',
    gap: '12px',
  },
  imageContainer: {
    position: 'relative',
    aspectRatio: '1',
    borderRadius: '8px',
    overflow: 'hidden',
    cursor: 'pointer',
    border: '2px solid transparent',
    transition: 'transform 0.2s, border-color 0.2s',
  },
  positiveContainer: {
    borderColor: '#d1fae5',
    ':hover': {
      borderColor: '#059669',
      transform: 'scale(1.02)',
    }
  },
  negativeContainer: {
    borderColor: '#fee2e2',
    ':hover': {
      borderColor: '#dc2626',
      transform: 'scale(1.02)',
    }
  },
  image: {
    width: '100%',
    height: '100%',
  },
  imageOverlay: {
    position: 'absolute',
    top: '4px',
    right: '4px',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    borderRadius: '50%',
    width: '24px',
    height: '24px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '12px',
    fontWeight: 'bold',
  },
  imageType: {
    color: 'inherit',
  },
  imageDescription: {
    position: 'absolute',
    bottom: '0',
    left: '0',
    right: '0',
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    color: 'white',
    padding: '4px 6px',
    fontSize: '10px',
    lineHeight: '1.2',
  },
  showMoreContainer: {
    aspectRatio: '1',
    border: '2px dashed #d1d5db',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    backgroundColor: '#f9fafb',
    transition: 'background-color 0.2s',
  },
  showMoreContent: {
    textAlign: 'center',
  },
  showMoreText: {
    display: 'block',
    fontSize: '18px',
    fontWeight: 'bold',
    color: '#6b7280',
    marginBottom: '2px',
  },
  showMoreSubtext: {
    fontSize: '12px',
    color: '#9ca3af',
  },
  showLessButton: {
    marginTop: '12px',
    padding: '8px 16px',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    cursor: 'pointer',
    fontSize: '14px',
    width: '100%',
  },
  emptyState: {
    textAlign: 'center',
    padding: '32px',
    color: '#6b7280',
  },
  emptyText: {
    fontSize: '14px',
    fontStyle: 'italic',
  },

  // Modal styles
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '20px',
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderRadius: '12px',
    maxWidth: '600px',
    maxHeight: '80vh',
    width: '100%',
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  },
  modalHeader: {
    padding: '20px',
    borderBottom: '1px solid #e5e7eb',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
  },
  modalTitle: {
    margin: '0 0 4px 0',
    fontSize: '18px',
    fontWeight: '600',
    color: '#1f2937',
  },
  modalType: {
    fontSize: '14px',
    fontWeight: '500',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '24px',
    cursor: 'pointer',
    color: '#6b7280',
    padding: '0',
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalImageContainer: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
    backgroundColor: '#f8fafc',
    maxHeight: '400px',
  },
  modalImage: {
    maxWidth: '100%',
    maxHeight: '100%',
    objectFit: 'contain',
    borderRadius: '8px',
  },
  modalDescription: {
    padding: '16px 20px',
    borderTop: '1px solid #e5e7eb',
    borderBottom: '1px solid #e5e7eb',
  },
  descriptionText: {
    margin: 0,
    fontSize: '14px',
    color: '#4b5563',
    lineHeight: '1.5',
  },
  modalInfo: {
    padding: '16px 20px',
    display: 'flex',
    gap: '20px',
  },
  infoItem: {
    display: 'flex',
    gap: '8px',
  },
  infoLabel: {
    fontSize: '12px',
    color: '#6b7280',
    fontWeight: '500',
  },
  infoValue: {
    fontSize: '12px',
    color: '#1f2937',
    fontFamily: 'monospace',
  },
};