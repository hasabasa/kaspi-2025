// components/whatsapp/TemplateForm.tsx
/**
 * Форма для создания и редактирования шаблонов WhatsApp сообщений
 */

import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Eye, EyeOff, Save, X } from 'lucide-react';
import { TemplateVariables } from './TemplateVariables';
import { wahaService, TemplatePreview } from '@/services/wahaService';
import { WhatsAppTemplate } from '@/services/wahaService';

interface TemplateFormProps {
  template?: WhatsAppTemplate;
  onSave: (template: { template_name: string; template_text: string; is_active?: boolean }) => Promise<void>;
  onCancel: () => void;
  loading?: boolean;
}

export const TemplateForm: React.FC<TemplateFormProps> = ({
  template,
  onSave,
  onCancel,
  loading = false
}) => {
  const [templateName, setTemplateName] = useState(template?.template_name || '');
  const [templateText, setTemplateText] = useState(template?.template_text || '');
  const [isActive, setIsActive] = useState(template?.is_active ?? true);
  const [showPreview, setShowPreview] = useState(false);
  const [preview, setPreview] = useState<TemplatePreview | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const isEditing = !!template;

  // Загружаем предварительный просмотр при изменении текста
  useEffect(() => {
    if (templateText.trim()) {
      loadPreview();
    } else {
      setPreview(null);
    }
  }, [templateText]);

  const loadPreview = async () => {
    if (!templateText.trim()) return;

    setPreviewLoading(true);
    setError(null);

    try {
      const previewData = await wahaService.previewTemplate(templateText);
      setPreview(previewData);
    } catch (err) {
      console.error('Ошибка загрузки предварительного просмотра:', err);
      setError('Ошибка загрузки предварительного просмотра');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleVariableInsert = (variable: string) => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const newText = templateText.substring(0, start) + variable + templateText.substring(end);
    
    setTemplateText(newText);

    // Устанавливаем курсор после вставленной переменной
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(start + variable.length, start + variable.length);
    }, 0);
  };

  const handleSave = async () => {
    if (!templateName.trim()) {
      setError('Название шаблона не может быть пустым');
      return;
    }

    if (!templateText.trim()) {
      setError('Текст шаблона не может быть пустым');
      return;
    }

    setError(null);

    try {
      await onSave({
        template_name: templateName.trim(),
        template_text: templateText.trim(),
        is_active: isActive
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка сохранения шаблона');
    }
  };

  const handleCancel = () => {
    setTemplateName('');
    setTemplateText('');
    setIsActive(true);
    setError(null);
    setPreview(null);
    onCancel();
  };

  return (
    <div className="space-y-6">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">
          {isEditing ? 'Редактировать шаблон' : 'Создать новый шаблон'}
        </h3>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowPreview(!showPreview)}
            disabled={!templateText.trim()}
          >
            {showPreview ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            {showPreview ? 'Скрыть' : 'Показать'} предпросмотр
          </Button>
        </div>
      </div>

      {/* Ошибки */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Левая часть - Форма */}
        <div className="lg:col-span-2 space-y-4">
          {/* Название шаблона */}
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-2">
                <Label htmlFor="template-name">Название шаблона</Label>
                <Input
                  id="template-name"
                  value={templateName}
                  onChange={(e) => setTemplateName(e.target.value)}
                  placeholder="Например: Уведомление о готовности заказа"
                  disabled={loading}
                />
              </div>
            </CardContent>
          </Card>

          {/* Текст шаблона */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm">Текст сообщения</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                ref={textareaRef}
                value={templateText}
                onChange={(e) => setTemplateText(e.target.value)}
                placeholder="Введите текст сообщения. Используйте переменные из правой панели."
                className="min-h-[200px] font-mono text-sm"
                disabled={loading}
              />
              <div className="mt-2 text-xs text-gray-500">
                Символов: {templateText.length}
              </div>
            </CardContent>
          </Card>

          {/* Настройки */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <Label htmlFor="is-active">Активный шаблон</Label>
                  <p className="text-xs text-gray-500">
                    Активные шаблоны используются для отправки уведомлений
                  </p>
                </div>
                <Switch
                  id="is-active"
                  checked={isActive}
                  onCheckedChange={setIsActive}
                  disabled={loading}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Правая часть - Переменные и предпросмотр */}
        <div className="space-y-4">
          {/* Переменные */}
          <TemplateVariables
            onVariableInsert={handleVariableInsert}
            className="h-fit"
          />

          {/* Предварительный просмотр */}
          {showPreview && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Предварительный просмотр</CardTitle>
              </CardHeader>
              <CardContent>
                {previewLoading ? (
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded animate-pulse" />
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
                    <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
                  </div>
                ) : preview ? (
                  <div className="space-y-3">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <div className="text-xs text-gray-500 mb-2">Пример сообщения:</div>
                      <div className="whitespace-pre-wrap text-sm">
                        {preview.preview_text}
                      </div>
                    </div>
                    
                    <Separator />
                    
                    <div className="space-y-2">
                      <div className="text-xs font-medium text-gray-700">Используемые переменные:</div>
                      <div className="flex flex-wrap gap-1">
                        {Object.keys(preview.sample_data).map((key) => (
                          <Badge key={key} variant="secondary" className="text-xs">
                            {`{${key}}`}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-4 text-gray-500 text-sm">
                    Введите текст шаблона для предварительного просмотра
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Кнопки действий */}
      <div className="flex justify-end gap-3">
        <Button
          variant="outline"
          onClick={handleCancel}
          disabled={loading}
        >
          <X className="h-4 w-4 mr-2" />
          Отмена
        </Button>
        <Button
          onClick={handleSave}
          disabled={loading || !templateName.trim() || !templateText.trim()}
        >
          <Save className="h-4 w-4 mr-2" />
          {loading ? 'Сохранение...' : (isEditing ? 'Сохранить изменения' : 'Создать шаблон')}
        </Button>
      </div>
    </div>
  );
};
