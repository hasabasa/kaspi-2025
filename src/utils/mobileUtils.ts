// utils/mobileUtils.ts
// Утилиты для мобильной адаптации

export interface DeviceInfo {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  screenWidth: number;
  screenHeight: number;
  devicePixelRatio: number;
  orientation: 'portrait' | 'landscape';
  hasNotch: boolean;
  supportsTouchEvents: boolean;
  supportsHover: boolean;
  preferredInputMethod: 'touch' | 'mouse' | 'hybrid';
}

export function getDeviceInfo(): DeviceInfo {
  if (typeof window === 'undefined') {
    return {
      isMobile: false,
      isTablet: false,
      isDesktop: true,
      deviceType: 'desktop',
      screenWidth: 1024,
      screenHeight: 768,
      devicePixelRatio: 1,
      orientation: 'landscape',
      hasNotch: false,
      supportsTouchEvents: false,
      supportsHover: true,
      preferredInputMethod: 'mouse'
    };
  }

  const width = window.innerWidth;
  const height = window.innerHeight;
  const isMobile = width < 768;
  const isTablet = width >= 768 && width < 1024;
  const isDesktop = width >= 1024;
  const devicePixelRatio = window.devicePixelRatio || 1;
  const orientation = height > width ? 'portrait' : 'landscape';
  
  // Определяем наличие notch (приблизительно)
  const hasNotch = CSS.supports('padding: env(safe-area-inset-top)') && 
                   parseInt(window.getComputedStyle(document.documentElement).getPropertyValue('env(safe-area-inset-top)') || '0') > 0;
  
  // Определяем поддержку touch events
  const supportsTouchEvents = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  // Определяем поддержку hover
  const supportsHover = window.matchMedia('(hover: hover)').matches;
  
  let deviceType: 'mobile' | 'tablet' | 'desktop' = 'desktop';
  if (isMobile) deviceType = 'mobile';
  else if (isTablet) deviceType = 'tablet';
  
  const preferredInputMethod: 'touch' | 'mouse' | 'hybrid' = 
    supportsTouchEvents && !supportsHover ? 'touch' :
    !supportsTouchEvents && supportsHover ? 'mouse' : 'hybrid';

  return {
    isMobile,
    isTablet,
    isDesktop,
    deviceType,
    screenWidth: width,
    screenHeight: height,
    devicePixelRatio,
    orientation,
    hasNotch,
    supportsTouchEvents,
    supportsHover,
    preferredInputMethod
  };
}

// Функции для оптимизации производительности на мобильных устройствах
export function shouldUseVirtualization(itemCount: number, deviceInfo?: DeviceInfo): boolean {
  const device = deviceInfo || getDeviceInfo();
  
  // На мобильных устройствах виртуализация нужна раньше
  if (device.isMobile) {
    return itemCount > 50;
  }
  
  if (device.isTablet) {
    return itemCount > 100;
  }
  
  return itemCount > 200;
}

export function getOptimalBatchSize(deviceInfo?: DeviceInfo): number {
  const device = deviceInfo || getDeviceInfo();
  
  if (device.isMobile) {
    return device.screenWidth <= 375 ? 10 : 20; // iPhone Mini/SE vs standard
  }
  
  if (device.isTablet) {
    return 30;
  }
  
  return 50;
}

export function getOptimalImageSize(deviceInfo?: DeviceInfo): { width: number; height: number } {
  const device = deviceInfo || getDeviceInfo();
  
  const baseSize = {
    mobile: { width: 64, height: 64 },
    tablet: { width: 80, height: 80 },
    desktop: { width: 96, height: 96 }
  };
  
  const size = baseSize[device.deviceType];
  
  // Учитываем device pixel ratio для четкости
  return {
    width: Math.round(size.width * Math.min(device.devicePixelRatio, 2)),
    height: Math.round(size.height * Math.min(device.devicePixelRatio, 2))
  };
}

// Функции для обработки touch событий
export function addTouchRippleEffect(element: HTMLElement): () => void {
  const handleTouchStart = (e: TouchEvent) => {
    const rect = element.getBoundingClientRect();
    const touch = e.touches[0];
    const x = touch.clientX - rect.left;
    const y = touch.clientY - rect.top;
    
    const ripple = document.createElement('div');
    ripple.style.cssText = `
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      pointer-events: none;
      width: 4px;
      height: 4px;
      left: ${x - 2}px;
      top: ${y - 2}px;
      animation: ripple 0.6s ease-out;
      z-index: 1000;
    `;
    
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    setTimeout(() => {
      if (ripple.parentNode) {
        ripple.parentNode.removeChild(ripple);
      }
    }, 600);
  };
  
  element.addEventListener('touchstart', handleTouchStart, { passive: true });
  
  return () => {
    element.removeEventListener('touchstart', handleTouchStart);
  };
}

// Debounce для оптимизации scroll и resize событий
export function debounce<T extends (...args: any[]) => any>(
  func: T, 
  wait: number
): T {
  let timeout: NodeJS.Timeout;
  return ((...args: any[]) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  }) as T;
}

// Throttle для scroll событий
export function throttle<T extends (...args: any[]) => any>(
  func: T, 
  limit: number
): T {
  let inThrottle: boolean;
  return ((...args: any[]) => {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  }) as T;
}

// Функции для адаптивного контента
export function getResponsiveImageSrc(
  baseSrc: string, 
  deviceInfo?: DeviceInfo
): string {
  const device = deviceInfo || getDeviceInfo();
  
  // Если у нас высокая плотность пикселей, загружаем 2x изображение
  if (device.devicePixelRatio >= 2) {
    const extension = baseSrc.split('.').pop();
    const name = baseSrc.replace(`.${extension}`, '');
    return `${name}@2x.${extension}`;
  }
  
  return baseSrc;
}

export function getFontSizeClass(
  baseSize: 'xs' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl',
  deviceInfo?: DeviceInfo
): string {
  const device = deviceInfo || getDeviceInfo();
  
  const mobileSizes = {
    'xs': 'text-xs',
    'sm': 'text-sm', 
    'base': 'text-base',
    'lg': 'text-lg',
    'xl': 'text-xl',
    '2xl': 'text-xl',
    '3xl': 'text-2xl'
  };
  
  const desktopSizes = {
    'xs': 'text-xs',
    'sm': 'text-sm',
    'base': 'text-base', 
    'lg': 'text-lg',
    'xl': 'text-xl',
    '2xl': 'text-2xl',
    '3xl': 'text-3xl'
  };
  
  return device.isMobile ? mobileSizes[baseSize] : desktopSizes[baseSize];
}

// Функция для определения оптимального количества колонок в сетке
export function getOptimalGridCols(
  minColWidth: number = 280,
  deviceInfo?: DeviceInfo
): string {
  const device = deviceInfo || getDeviceInfo();
  
  const availableWidth = device.screenWidth - 48; // учитываем padding
  const cols = Math.max(1, Math.floor(availableWidth / minColWidth));
  
  if (device.isMobile) {
    return cols === 1 ? 'grid-cols-1' : 'grid-cols-2';
  }
  
  if (device.isTablet) {
    return `grid-cols-${Math.min(cols, 3)}`;
  }
  
  return `grid-cols-${Math.min(cols, 4)}`;
}

// Проверка поддержки веб-функций
export function checkFeatureSupport() {
  if (typeof window === 'undefined') {
    return {
      webp: false,
      avif: false,
      intersectionObserver: false,
      resizeObserver: false,
      serviceWorker: false
    };
  }
  
  const canvas = document.createElement('canvas');
  
  return {
    webp: canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0,
    avif: canvas.toDataURL('image/avif').indexOf('data:image/avif') === 0,
    intersectionObserver: 'IntersectionObserver' in window,
    resizeObserver: 'ResizeObserver' in window,
    serviceWorker: 'serviceWorker' in navigator
  };
}

// CSS класс для безопасных зон
export function addRippleAnimation() {
  if (typeof document === 'undefined') return;
  
  const style = document.createElement('style');
  style.textContent = `
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `;
  
  document.head.appendChild(style);
}
