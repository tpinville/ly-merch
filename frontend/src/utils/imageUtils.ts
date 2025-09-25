// Utility functions for image handling

const HEURITECH_IMAGE_BASE_URL = 'https://images.heuritech.com/';

/**
 * Generates the full image URL from an image hash
 */
export function getImageUrl(imageHash?: string): string | null {
  if (!imageHash) return null;
  return `${HEURITECH_IMAGE_BASE_URL}${imageHash}`;
}

/**
 * Generates a placeholder image URL for when no image is available
 */
export function getPlaceholderUrl(): string {
  return 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8cmVjdCB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2Y4ZmFmYyIgc3Ryb2tlPSIjZTVlN2ViIiBzdHJva2Utd2lkdGg9IjEiLz4KICA8dGV4dCB4PSIxNTAiIHk9IjEwNSIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjE0IiBmaWxsPSIjNmI3MjgwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5ObyBJbWFnZSBBdmFpbGFibGU8L3RleHQ+Cjwvc3ZnPgo=';
}

/**
 * Preloads an image to check if it's available
 */
export function preloadImage(url: string): Promise<boolean> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
}

/**
 * Generates alt text for trend images
 */
export function getImageAltText(trendName: string, imageType?: 'positive' | 'negative', description?: string): string {
  if (description) {
    return `${imageType ? `${imageType} example` : 'Image'} of ${trendName}: ${description}`;
  }
  return `${imageType ? `${imageType} example` : 'Image'} of ${trendName}`;
}