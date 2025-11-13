
export interface Position {
  top: number;
  left: number;
  placement: 'left' | 'right' | 'center';
}

export interface PositionCalculatorOptions {
  triggerElement: HTMLElement;
  popoverWidth?: number;
  popoverHeight?: number;
  offset?: number;
  preferredPlacement?: 'left' | 'right';
}

export class PositionCalculator {
  static calculate({
    triggerElement,
    popoverWidth = 400,
    popoverHeight = 500,
    offset = 16,
    preferredPlacement = 'right'
  }: PositionCalculatorOptions): Position {
    const triggerRect = triggerElement.getBoundingClientRect();
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;
    
    let left: number;
    let top = triggerRect.top;
    let placement: 'left' | 'right' | 'center';
    
    // Пытаемся разместить согласно предпочтению
    if (preferredPlacement === 'right') {
      left = triggerRect.right + offset;
      placement = 'right';
      
      // Проверяем, помещается ли справа
      if (left + popoverWidth > viewportWidth - 20) {
        // Пробуем слева
        left = triggerRect.left - popoverWidth - offset;
        placement = 'left';
        
        // Если и слева не помещается
        if (left < 20) {
          left = (viewportWidth - popoverWidth) / 2;
          placement = 'center';
        }
      }
    } else {
      // preferredPlacement === 'left'
      left = triggerRect.left - popoverWidth - offset;
      placement = 'left';
      
      // Проверяем, помещается ли слева
      if (left < 20) {
        // Пробуем справа
        left = triggerRect.right + offset;
        placement = 'right';
        
        // Если и справа не помещается
        if (left + popoverWidth > viewportWidth - 20) {
          left = (viewportWidth - popoverWidth) / 2;
          placement = 'center';
        }
      }
    }
    
    // Проверяем вертикальное положение
    if (top + popoverHeight > viewportHeight - 20) {
      top = viewportHeight - popoverHeight - 20;
    }
    
    if (top < 20) {
      top = 20;
    }
    
    return { top, left, placement };
  }
}

// Хук для использования в React компонентах
export const usePositionCalculator = (
  triggerElement: HTMLElement | null,
  options: Omit<PositionCalculatorOptions, 'triggerElement'> = {}
) => {
  if (!triggerElement) {
    return { top: 0, left: 0, placement: 'right' as const };
  }
  
  return PositionCalculator.calculate({
    triggerElement,
    ...options
  });
};
