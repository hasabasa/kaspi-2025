// components/whatsapp/WAHAStatusIndicator.tsx
import { useEffect, useState } from 'react';
import { useWAHA } from '@/hooks/useWAHA';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, Clock, AlertCircle } from 'lucide-react';

interface WAHAStatusIndicatorProps {
  className?: string;
}

export default function WAHAStatusIndicator({ className }: WAHAStatusIndicatorProps) {
  const { status } = useWAHA();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Показываем индикатор только если есть активность
    setIsVisible(status.status !== 'disconnected');
  }, [status.status]);

  if (!isVisible) return null;

  const getStatusIcon = () => {
    switch (status.status) {
      case 'connected':
        return <CheckCircle className="h-3 w-3" />;
      case 'connecting':
        return <Clock className="h-3 w-3" />;
      case 'error':
        return <AlertCircle className="h-3 w-3" />;
      default:
        return <XCircle className="h-3 w-3" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'connected':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'connecting':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = () => {
    switch (status.status) {
      case 'connected':
        return 'WhatsApp';
      case 'connecting':
        return 'Подключение...';
      case 'error':
        return 'Ошибка';
      default:
        return 'Отключено';
    }
  };

  return (
    <Badge 
      variant="outline" 
      className={`flex items-center gap-1 px-2 py-1 text-xs ${getStatusColor()} ${className}`}
      title={status.message}
    >
      {getStatusIcon()}
      <span>{getStatusText()}</span>
    </Badge>
  );
}
