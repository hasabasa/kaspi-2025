import React from 'react';
import { Button } from '@/components/ui/button';

interface ConnectStoreButtonProps {
  onConnect?: () => void;
  disabled?: boolean;
}

const ConnectStoreButton: React.FC<ConnectStoreButtonProps> = ({ onConnect, disabled }) => {
  return (
    <Button variant="outline" size="sm" onClick={onConnect} disabled={disabled}>
      Подключить магазин
    </Button>
  );
};

export default ConnectStoreButton;
