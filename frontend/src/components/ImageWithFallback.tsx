import React, { useState, useEffect } from 'react';
import { getImageUrl, getPlaceholderUrl, preloadImage } from '../utils/imageUtils';

interface ImageWithFallbackProps {
  imageHash?: string;
  alt: string;
  style?: React.CSSProperties;
  className?: string;
  onLoad?: () => void;
  onError?: () => void;
  showPlaceholder?: boolean;
}

export default function ImageWithFallback({
  imageHash,
  alt,
  style,
  className,
  onLoad,
  onError,
  showPlaceholder = true
}: ImageWithFallbackProps) {
  const [imageState, setImageState] = useState<'loading' | 'loaded' | 'error' | 'no-image'>('loading');
  const [currentSrc, setCurrentSrc] = useState<string>('');

  useEffect(() => {
    if (!imageHash) {
      setImageState('no-image');
      setCurrentSrc(showPlaceholder ? getPlaceholderUrl() : '');
      return;
    }

    const imageUrl = getImageUrl(imageHash);
    if (!imageUrl) {
      setImageState('no-image');
      setCurrentSrc(showPlaceholder ? getPlaceholderUrl() : '');
      return;
    }

    setImageState('loading');

    preloadImage(imageUrl).then((isLoaded) => {
      if (isLoaded) {
        setImageState('loaded');
        setCurrentSrc(imageUrl);
        onLoad?.();
      } else {
        setImageState('error');
        setCurrentSrc(showPlaceholder ? getPlaceholderUrl() : '');
        onError?.();
      }
    });
  }, [imageHash, showPlaceholder, onLoad, onError]);

  if (!currentSrc && !showPlaceholder) {
    return null;
  }

  return (
    <div style={{ position: 'relative', ...style }} className={className}>
      {imageState === 'loading' && (
        <div style={styles.loadingContainer}>
          <div style={styles.spinner}></div>
          <span style={styles.loadingText}>Loading image...</span>
        </div>
      )}

      {currentSrc && (
        <img
          src={currentSrc}
          alt={alt}
          style={{
            ...styles.image,
            opacity: imageState === 'loading' ? 0.3 : 1,
          }}
          onLoad={() => {
            if (imageState === 'loaded') {
              onLoad?.();
            }
          }}
          onError={() => {
            if (imageState === 'loaded') {
              setImageState('error');
              setCurrentSrc(showPlaceholder ? getPlaceholderUrl() : '');
              onError?.();
            }
          }}
        />
      )}

      {imageState === 'error' && showPlaceholder && (
        <div style={styles.errorOverlay}>
          <span style={styles.errorText}>Image unavailable</span>
        </div>
      )}
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  image: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    transition: 'opacity 0.3s ease',
  },
  loadingContainer: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '8px',
  },
  spinner: {
    width: '24px',
    height: '24px',
    border: '2px solid #f3f4f6',
    borderTop: '2px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  loadingText: {
    fontSize: '12px',
    color: '#6b7280',
  },
  errorOverlay: {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    textAlign: 'center',
  },
  errorText: {
    fontSize: '12px',
    color: '#ef4444',
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    padding: '4px 8px',
    borderRadius: '4px',
  },
};