
import React from 'react';

interface LoadingTextProps {
  text?: string;
}

const LoadingText: React.FC<LoadingTextProps> = ({ 
  text = "Загрузка..." 
}) => {
  if (!text) return null;
  
  return (
    <div className="mt-8 text-lg font-medium text-gray-700">
      {text}
    </div>
  );
};

export default LoadingText;
