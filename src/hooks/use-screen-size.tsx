
import * as React from "react"

// Enhanced breakpoints system
const BREAKPOINTS = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
  '3xl': 1920,
  '4xl': 2560
}

export type ScreenSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'

export function useScreenSize() {
  const [screenSize, setScreenSize] = React.useState<ScreenSize>('lg')
  const [width, setWidth] = React.useState<number>(0)

  React.useEffect(() => {
    const updateScreenSize = () => {
      const currentWidth = window.innerWidth
      setWidth(currentWidth)
      
      if (currentWidth < BREAKPOINTS.xs) {
        setScreenSize('xs')
      } else if (currentWidth < BREAKPOINTS.sm) {
        setScreenSize('sm')
      } else if (currentWidth < BREAKPOINTS.md) {
        setScreenSize('md')
      } else if (currentWidth < BREAKPOINTS.lg) {
        setScreenSize('lg')
      } else if (currentWidth < BREAKPOINTS.xl) {
        setScreenSize('xl')
      } else if (currentWidth < BREAKPOINTS['2xl']) {
        setScreenSize('2xl')
      } else if (currentWidth < BREAKPOINTS['3xl']) {
        setScreenSize('3xl')
      } else {
        setScreenSize('4xl')
      }
    }

    updateScreenSize()
    window.addEventListener('resize', updateScreenSize)
    return () => window.removeEventListener('resize', updateScreenSize)
  }, [])

  return { 
    screenSize, 
    width,
    isMobile: screenSize === 'xs' || screenSize === 'sm',
    isTablet: screenSize === 'md',
    isDesktop: screenSize === 'lg' || screenSize === 'xl' || screenSize === '2xl' || screenSize === '3xl' || screenSize === '4xl',
    isLargeDesktop: screenSize === 'xl' || screenSize === '2xl' || screenSize === '3xl' || screenSize === '4xl',
    isExtraLargeDesktop: screenSize === '2xl' || screenSize === '3xl' || screenSize === '4xl',
    isUltraWideDesktop: screenSize === '3xl' || screenSize === '4xl'
  }
}

// Utility functions for responsive values
export function getResponsiveValue<T>(
  values: Partial<Record<ScreenSize, T>>,
  screenSize: ScreenSize,
  fallback: T
): T {
  return values[screenSize] ?? values.lg ?? values.md ?? values.sm ?? fallback
}

export function useResponsiveValue<T>(
  values: Partial<Record<ScreenSize, T>>,
  fallback: T
): T {
  const { screenSize } = useScreenSize()
  return getResponsiveValue(values, screenSize, fallback)
}
