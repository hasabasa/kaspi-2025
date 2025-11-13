
import { useState, useEffect } from 'react';

interface UseLoadingOptions {
  minDuration?: number;
  initialLoading?: boolean;
}

export const useLoading = (options: UseLoadingOptions = {}) => {
  const { minDuration = 1000, initialLoading = true } = options;
  const [isLoading, setIsLoading] = useState(initialLoading);
  const [startTime] = useState(Date.now());

  const stopLoading = () => {
    const elapsed = Date.now() - startTime;
    const remaining = Math.max(0, minDuration - elapsed);
    
    setTimeout(() => {
      setIsLoading(false);
    }, remaining);
  };

  const startLoading = () => {
    setIsLoading(true);
  };

  return {
    isLoading,
    startLoading,
    stopLoading
  };
};
