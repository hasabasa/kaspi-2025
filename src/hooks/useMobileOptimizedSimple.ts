// hooks/useMobileOptimizedSimple.ts
// Упрощенная версия мобильного хука без сложной логики

import { useState, useEffect } from 'react';

export interface SimpleMobileConfig {
  width: number;
  height: number;
  
  // Device categories
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  
  // Specific device types
  isSmallPhone: boolean;
  isMediumPhone: boolean;
  isLargePhone: boolean;
  
  // Orientation
  isPortrait: boolean;
  isLandscape: boolean;
  
  // Touch-friendly sizes
  touchTargetSize: string;
  touchSpacing: string;
  
  // Responsive values
  containerPadding: string;
  cardSpacing: string;
  
  // Grid configurations
  gridCols: {
    cards: string;
    metrics: string;
    products: string;
  };
  
  // Utility functions
  getSpacing: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl') => string;
  getTextSize: (size: 'xs' | 'sm' | 'base' | 'lg' | 'xl') => string;
}

export function useMobileOptimizedSimple(): SimpleMobileConfig {
  const [dimensions, setDimensions] = useState(() => {
    if (typeof window === 'undefined') {
      return { width: 1024, height: 768 };
    }
    return {
      width: window.innerWidth,
      height: window.innerHeight,
    };
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;
    
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  const { width, height } = dimensions;
  
  // Device categorization
  const isMobile = width < 768;
  const isTablet = width >= 768 && width < 1024;
  const isDesktop = width >= 1024;
  
  // Specific device types
  const isSmallPhone = width <= 375;
  const isMediumPhone = width > 375 && width <= 414;
  const isLargePhone = width > 414 && width < 768;
  
  // Orientation
  const isPortrait = height > width;
  const isLandscape = width > height;
  
  // Touch-friendly configurations
  const touchTargetSize = 'min-h-[44px] min-w-[44px]';
  const touchSpacing = isSmallPhone ? 'gap-2' : 'gap-3';
  
  // Responsive spacing
  const containerPadding = isSmallPhone ? 'p-3' : isMobile ? 'p-4' : 'p-6';
  const cardSpacing = isSmallPhone ? 'space-y-3' : isMobile ? 'space-y-4' : 'space-y-6';
  
  // Grid configurations
  const gridCols = {
    cards: isSmallPhone ? 'grid-cols-1' : isMobile ? 'grid-cols-1' : 'grid-cols-2 lg:grid-cols-3',
    metrics: isSmallPhone ? 'grid-cols-1' : isMobile ? 'grid-cols-2' : 'grid-cols-4',
    products: isSmallPhone ? 'grid-cols-1' : isMobile ? 'grid-cols-1' : 'grid-cols-2 lg:grid-cols-3',
  };
  
  // Utility functions
  const getSpacing = (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'): string => {
    const spacing = {
      xs: isSmallPhone ? 'gap-1' : 'gap-2',
      sm: isSmallPhone ? 'gap-2' : 'gap-3',
      md: isSmallPhone ? 'gap-3' : 'gap-4',
      lg: isSmallPhone ? 'gap-4' : 'gap-6',
      xl: isSmallPhone ? 'gap-6' : 'gap-8',
    };
    return spacing[size];
  };
  
  const getTextSize = (size: 'xs' | 'sm' | 'base' | 'lg' | 'xl'): string => {
    const sizes = {
      xs: isSmallPhone ? 'text-xs' : 'text-sm',
      sm: isSmallPhone ? 'text-sm' : 'text-base',
      base: isSmallPhone ? 'text-base' : 'text-lg',
      lg: isSmallPhone ? 'text-lg' : 'text-xl',
      xl: isSmallPhone ? 'text-xl' : 'text-2xl',
    };
    return sizes[size];
  };
  
  return {
    width,
    height,
    
    // Device categories
    isMobile,
    isTablet,
    isDesktop,
    
    // Specific device types
    isSmallPhone,
    isMediumPhone,
    isLargePhone,
    
    // Orientation
    isPortrait,
    isLandscape,
    
    // Touch-friendly sizes
    touchTargetSize,
    touchSpacing,
    
    // Responsive values
    containerPadding,
    cardSpacing,
    
    // Grid configurations
    gridCols,
    
    // Utility functions
    getSpacing,
    getTextSize,
  };
}
