// hooks/useMobileOptimized.ts
import { useState, useEffect } from 'react';

interface MobileBreakpoints {
  xs: number;  // 320px - очень маленькие телефоны
  sm: number;  // 375px - iPhone Mini, SE
  md: number;  // 414px - стандартные телефоны
  lg: number;  // 768px - планшеты в портретной ориентации
  xl: number;  // 1024px - планшеты в альбомной ориентации
}

const MOBILE_BREAKPOINTS: MobileBreakpoints = {
  xs: 320,
  sm: 375,
  md: 414,
  lg: 768,
  xl: 1024,
};

export interface MobileOptimizedConfig {
  width: number;
  height: number;
  
  // Device categories
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  
  // Specific device types
  isSmallPhone: boolean;      // <= 375px (iPhone Mini, SE)
  isMediumPhone: boolean;     // 376-414px (стандартные iPhone)
  isLargePhone: boolean;      // 415-767px (iPhone Pro Max, Android XL)
  isSmallTablet: boolean;     // 768-1024px (iPad mini)
  isLargeTablet: boolean;     // 1025px+ (iPad Pro)
  
  // Orientation
  isPortrait: boolean;
  isLandscape: boolean;
  
  // Touch-friendly sizes
  touchTargetSize: string;    // Минимальный размер для touch
  touchSpacing: string;       // Отступы между touch элементами
  
  // Responsive values
  containerPadding: string;
  cardSpacing: string;
  fontSize: {
    xs: string;
    sm: string;
    base: string;
    lg: string;
    xl: string;
  };
  
  // Layout helpers
  sidebarBehavior: 'overlay' | 'push' | 'static';
  gridCols: {
    cards: string;
    metrics: string;
    products: string;
  };
  
  // Performance settings
  shouldVirtualize: boolean;  // Виртуализация для больших списков
  itemsPerPage: number;       // Элементов на страницу
  
  // Utility functions
  getSpacing: (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl') => string;
  getResponsiveCols: (xs: number, sm: number, md: number, lg: number, xl: number) => string;
  getTextSize: (size: 'xs' | 'sm' | 'base' | 'lg' | 'xl') => string;
}

export function useMobileOptimized(): MobileOptimizedConfig {
  const [dimensions, setDimensions] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 1024,
    height: typeof window !== 'undefined' ? window.innerHeight : 768,
  });

  useEffect(() => {
    const updateDimensions = () => {
      setDimensions({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', updateDimensions);
    window.addEventListener('orientationchange', updateDimensions);

    return () => {
      window.removeEventListener('resize', updateDimensions);
      window.removeEventListener('orientationchange', updateDimensions);
    };
  }, []);

  const { width, height } = dimensions;
  
  // Device categorization
  const isMobile = width < MOBILE_BREAKPOINTS.lg;
  const isTablet = width >= MOBILE_BREAKPOINTS.lg && width < 1280;
  const isDesktop = width >= 1280;
  
  // Specific device types
  const isSmallPhone = width <= MOBILE_BREAKPOINTS.sm;
  const isMediumPhone = width > MOBILE_BREAKPOINTS.sm && width <= MOBILE_BREAKPOINTS.md;
  const isLargePhone = width > MOBILE_BREAKPOINTS.md && width < MOBILE_BREAKPOINTS.lg;
  const isSmallTablet = width >= MOBILE_BREAKPOINTS.lg && width <= MOBILE_BREAKPOINTS.xl;
  const isLargeTablet = width > MOBILE_BREAKPOINTS.xl;
  
  // Orientation
  const isPortrait = height > width;
  const isLandscape = width > height;
  
  // Touch-friendly configurations
  const touchTargetSize = isSmallPhone ? 'min-h-[44px] min-w-[44px]' : 'min-h-[48px] min-w-[48px]';
  const touchSpacing = isSmallPhone ? 'gap-2' : 'gap-3';
  
  // Responsive spacing
  const containerPadding = (() => {
    if (isSmallPhone) return 'p-3';
    if (isMediumPhone) return 'p-4';
    if (isLargePhone) return 'p-4';
    if (isTablet) return 'p-6';
    return 'p-8';
  })();
  
  const cardSpacing = (() => {
    if (isSmallPhone) return 'space-y-3';
    if (isMobile) return 'space-y-4';
    if (isTablet) return 'space-y-6';
    return 'space-y-8';
  })();
  
  // Font sizes based on device
  const fontSize = {
    xs: isSmallPhone ? 'text-xs' : 'text-sm',
    sm: isSmallPhone ? 'text-sm' : 'text-base',
    base: isSmallPhone ? 'text-base' : 'text-lg',
    lg: isSmallPhone ? 'text-lg' : 'text-xl',
    xl: isSmallPhone ? 'text-xl' : 'text-2xl',
  };
  
  // Sidebar behavior
  const sidebarBehavior: 'overlay' | 'push' | 'static' = (() => {
    if (isMobile) return 'overlay';
    if (isTablet) return 'push';
    return 'static';
  })();
  
  // Grid configurations
  const gridCols = {
    cards: (() => {
      if (isSmallPhone) return 'grid-cols-1';
      if (isMediumPhone) return 'grid-cols-1';
      if (isLargePhone) return 'grid-cols-2';
      if (isSmallTablet) return 'grid-cols-2 lg:grid-cols-3';
      return 'grid-cols-2 md:grid-cols-3 lg:grid-cols-4';
    })(),
    
    metrics: (() => {
      if (isSmallPhone) return 'grid-cols-1';
      if (isMediumPhone) return 'grid-cols-2';
      if (isLargePhone) return 'grid-cols-2';
      if (isTablet) return 'grid-cols-3 lg:grid-cols-4';
      return 'grid-cols-4';
    })(),
    
    products: (() => {
      if (isSmallPhone) return 'grid-cols-1';
      if (isMediumPhone) return 'grid-cols-1';
      if (isLargePhone && isLandscape) return 'grid-cols-2';
      if (isTablet) return 'grid-cols-2 lg:grid-cols-3';
      return 'grid-cols-3 xl:grid-cols-4';
    })(),
  };
  
  // Performance optimizations
  const shouldVirtualize = isMobile && height < 800; // Виртуализация на маленьких экранах
  const itemsPerPage = (() => {
    if (isSmallPhone) return 10;
    if (isMobile) return 20;
    if (isTablet) return 30;
    return 50;
  })();
  
  // Utility functions
  const getSpacing = (size: 'xs' | 'sm' | 'md' | 'lg' | 'xl'): string => {
    const spacingMap = {
      xs: isSmallPhone ? 'gap-1' : 'gap-2',
      sm: isSmallPhone ? 'gap-2' : 'gap-3',
      md: isSmallPhone ? 'gap-3' : 'gap-4',
      lg: isSmallPhone ? 'gap-4' : 'gap-6',
      xl: isSmallPhone ? 'gap-6' : 'gap-8',
    };
    return spacingMap[size];
  };
  
  const getResponsiveCols = (xs: number, sm: number, md: number, lg: number, xl: number): string => {
    const cols = [];
    
    if (xs) cols.push(`grid-cols-${xs}`);
    if (sm && width >= MOBILE_BREAKPOINTS.sm) cols.push(`sm:grid-cols-${sm}`);
    if (md && width >= MOBILE_BREAKPOINTS.md) cols.push(`md:grid-cols-${md}`);
    if (lg && width >= MOBILE_BREAKPOINTS.lg) cols.push(`lg:grid-cols-${lg}`);
    if (xl && width >= MOBILE_BREAKPOINTS.xl) cols.push(`xl:grid-cols-${xl}`);
    
    return cols.join(' ');
  };
  
  const getTextSize = (size: 'xs' | 'sm' | 'base' | 'lg' | 'xl'): string => {
    return fontSize[size];
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
    isSmallTablet,
    isLargeTablet,
    
    // Orientation
    isPortrait,
    isLandscape,
    
    // Touch-friendly sizes
    touchTargetSize,
    touchSpacing,
    
    // Responsive values
    containerPadding,
    cardSpacing,
    fontSize,
    
    // Layout helpers
    sidebarBehavior,
    gridCols,
    
    // Performance settings
    shouldVirtualize,
    itemsPerPage,
    
    // Utility functions
    getSpacing,
    getResponsiveCols,
    getTextSize,
  };
}
