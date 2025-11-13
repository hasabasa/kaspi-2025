import React, { useState } from 'react';
import { Image } from 'lucide-react';

interface SafeImageProps {
  src: string;
  alt: string;
  className?: string;
  fallbackText?: string;
}

export const SafeImage: React.FC<SafeImageProps> = ({ 
  src, 
  alt, 
  className = "w-full h-full object-cover",
  fallbackText = "No Image"
}) => {
  const [hasError, setHasError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  const handleError = () => {
    setHasError(true);
    setIsLoading(false);
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  // Если URL содержит resources.kaspi.kz, сразу показываем placeholder
  if (src.includes('resources.kaspi.kz') || hasError) {
    return (
      <div className={`${className} bg-muted flex items-center justify-center`}>
        <div className="text-center text-muted-foreground">
          <Image className="h-6 w-6 mx-auto mb-1" />
          <span className="text-xs">{fallbackText}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {isLoading && (
        <div className={`${className} bg-muted flex items-center justify-center`}>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
        </div>
      )}
      <img 
        src={src} 
        alt={alt}
        className={`${className} ${isLoading ? 'opacity-0' : 'opacity-100'}`}
        onError={handleError}
        onLoad={handleLoad}
      />
    </div>
  );
};
