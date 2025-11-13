// components/ui/Logo.tsx
import React from 'react';
import { cn } from '@/lib/utils';

interface LogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const Logo = ({ className, size = 'md', showText = true }: LogoProps) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  const textSizeClasses = {
    sm: 'text-sm',
    md: 'text-lg',
    lg: 'text-2xl'
  };

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className={cn(sizeClasses[size], 'flex-shrink-0')}>
        <svg 
          width="100%" 
          height="100%" 
          viewBox="0 0 343 387" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-sm"
        >
          <g filter="url(#filter0_d_1_125)">
            <path d="M170.93 161.788V321.634L32.5 241.711V81.8652L170.93 161.788Z" fill="#A2A2A2" stroke="black"/>
            <path d="M168.68 2.16504C170.381 1.18261 172.478 1.18272 174.18 2.16504L309.86 80.5L171.43 160.423L32.999 80.5L168.68 2.16504Z" fill="#E1E0E0" stroke="black"/>
            <path d="M309.93 241.711L171.5 321.634V161.788L309.93 81.8652V241.711Z" fill="#646363" stroke="black"/>
          </g>
          <defs>
            <filter id="filter0_d_1_125" x="0" y="0.928223" width="342.86" height="385.572" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB">
              <feFlood floodOpacity="0" result="BackgroundImageFix"/>
              <feColorMatrix in="SourceAlpha" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 127 0" result="hardAlpha"/>
              <feOffset dy="32"/>
              <feGaussianBlur stdDeviation="16"/>
              <feComposite in2="hardAlpha" operator="out"/>
              <feColorMatrix type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.25 0"/>
              <feBlend mode="normal" in2="BackgroundImageFix" result="effect1_dropShadow_1_125"/>
              <feBlend mode="normal" in="SourceGraphic" in2="effect1_dropShadow_1_125" result="shape"/>
            </filter>
          </defs>
        </svg>
      </div>
      {showText && (
        <span className={cn(
          'font-bold text-foreground',
          textSizeClasses[size]
        )}>
          Cube Development
        </span>
      )}
    </div>
  );
};

export default Logo;
