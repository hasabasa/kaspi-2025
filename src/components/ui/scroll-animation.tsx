
import React from 'react';
import { useScrollAnimation } from '@/hooks/useScrollAnimation';
import { cn } from '@/lib/utils';

interface ScrollAnimationProps {
  children: React.ReactNode;
  className?: string;
  animation?: 'fade' | 'slide-up' | 'scale' | 'slide-left' | 'slide-right';
  delay?: number;
  duration?: number;
}

const ScrollAnimation: React.FC<ScrollAnimationProps> = ({
  children,
  className,
  animation = 'fade',
  delay = 0,
  duration = 0.8,
}) => {
  const [ref, isVisible] = useScrollAnimation();

  const getAnimationClasses = () => {
    const baseClasses = 'transition-all ease-out';
    const delayStyle = delay > 0 ? { transitionDelay: `${delay}ms` } : {};
    const durationStyle = { transitionDuration: `${duration}s` };

    switch (animation) {
      case 'slide-up':
        return {
          className: cn(
            baseClasses,
            !isVisible ? 'opacity-0 translate-y-8' : 'opacity-100 translate-y-0',
            className
          ),
          style: { ...delayStyle, ...durationStyle }
        };
      case 'scale':
        return {
          className: cn(
            baseClasses,
            !isVisible ? 'opacity-0 scale-95' : 'opacity-100 scale-100',
            className
          ),
          style: { ...delayStyle, ...durationStyle }
        };
      case 'slide-left':
        return {
          className: cn(
            baseClasses,
            !isVisible ? 'opacity-0 -translate-x-8' : 'opacity-100 translate-x-0',
            className
          ),
          style: { ...delayStyle, ...durationStyle }
        };
      case 'slide-right':
        return {
          className: cn(
            baseClasses,
            !isVisible ? 'opacity-0 translate-x-8' : 'opacity-100 translate-x-0',
            className
          ),
          style: { ...delayStyle, ...durationStyle }
        };
      default:
        return {
          className: cn(
            baseClasses,
            !isVisible ? 'opacity-0' : 'opacity-100',
            className
          ),
          style: { ...delayStyle, ...durationStyle }
        };
    }
  };

  const { className: animationClassName, style } = getAnimationClasses();

  return (
    <div ref={ref} className={animationClassName} style={style}>
      {children}
    </div>
  );
};

export default ScrollAnimation;
