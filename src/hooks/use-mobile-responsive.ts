
import { useScreenSize } from './use-screen-size';

export function useMobileResponsive() {
  const { screenSize, width } = useScreenSize();

  const isIPhone = width >= 375 && width <= 430;
  const isIPhoneMini = width <= 375;
  const isIPhoneStandard = width > 375 && width <= 414;
  const isIPhoneProMax = width > 414 && width <= 430;
  
  const isMobilePortrait = width < 768;
  const isMobileLandscape = width >= 568 && width < 768;

  return {
    screenSize,
    width,
    isIPhone,
    isIPhoneMini,
    isIPhoneStandard,
    isIPhoneProMax,
    isMobilePortrait,
    isMobileLandscape,
    isMobile: screenSize === 'xs' || screenSize === 'sm',
    isTablet: screenSize === 'md',
    isDesktop: screenSize === 'lg' || screenSize === 'xl' || screenSize === '2xl',
    
    // Helper functions for responsive values
    getMobileSpacing: () => isIPhoneMini ? 'p-3' : 'p-4',
    getMobileFontSize: () => isIPhoneMini ? 'text-sm' : 'text-base',
    getTouchTargetSize: () => 'min-h-touch-target min-w-touch-target',
  };
}
