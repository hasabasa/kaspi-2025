// components/whatsapp/TemplateVariables.tsx
/**
 * Компонент для отображения доступных переменных шаблона
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Copy, Check } from 'lucide-react';
import { wahaService, AvailableVariables } from '@/services/wahaService';

interface TemplateVariablesProps {
  onVariableInsert: (variable: string) => void;
  className?: string;
}

export const TemplateVariables: React.FC<TemplateVariablesProps> = ({
  onVariableInsert,
  className = ''
}) => {
  const [variables, setVariables] = useState<AvailableVariables>({});
  const [loading, setLoading] = useState(true);
  const [copiedVariable, setCopiedVariable] = useState<string | null>(null);

  useEffect(() => {
    loadVariables();
  }, []);

  const loadVariables = async () => {
    try {
      const vars = await wahaService.getAvailableVariables();
      setVariables(vars);
    } catch (error) {
      console.error('Ошибка загрузки переменных:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVariableClick = (variable: string) => {
    onVariableInsert(variable);
  };

  const handleCopyVariable = async (variable: string) => {
    try {
      await navigator.clipboard.writeText(variable);
      setCopiedVariable(variable);
      setTimeout(() => setCopiedVariable(null), 2000);
    } catch (error) {
      console.error('Ошибка копирования:', error);
    }
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Доступные переменные</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-8 bg-gray-200 rounded animate-pulse" />
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-sm font-medium">Доступные переменные</CardTitle>
        <p className="text-xs text-gray-500">
          Нажмите на переменную для вставки в шаблон
        </p>
      </CardHeader>
      <CardContent className="space-y-2">
        {Object.entries(variables).map(([variable, description]) => (
          <div
            key={variable}
            className="group p-2 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => handleVariableClick(variable)}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <Badge variant="outline" className="text-xs font-mono">
                    {variable}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleCopyVariable(variable);
                    }}
                  >
                    {copiedVariable === variable ? (
                      <Check className="h-3 w-3 text-green-600" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <p className="text-xs text-gray-600 mt-1 truncate">
                  {description}
                </p>
              </div>
            </div>
          </div>
        ))}
        
        {Object.keys(variables).length === 0 && (
          <div className="text-center py-4 text-gray-500 text-sm">
            Переменные не найдены
          </div>
        )}
      </CardContent>
    </Card>
  );
};
