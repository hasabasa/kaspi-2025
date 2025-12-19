// Компонент для загрузки файлов

import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Paperclip, X, Image as ImageIcon, FileText } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ChatFile } from '@/types/ai-assistants';

interface FileUploadButtonProps {
  onFilesSelected: (files: ChatFile[]) => void;
  maxFiles?: number;
  maxSize?: number; // в байтах
  acceptedTypes?: string[];
  disabled?: boolean;
}

export function FileUploadButton({
  onFilesSelected,
  maxFiles = 5,
  maxSize = 10 * 1024 * 1024, // 10MB по умолчанию
  acceptedTypes = ['image/*', 'application/pdf', '.doc', '.docx', '.xls', '.xlsx'],
  disabled = false,
}: FileUploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFiles, setSelectedFiles] = useState<ChatFile[]>([]);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    // Проверка количества файлов
    if (selectedFiles.length + files.length > maxFiles) {
      alert(`Можно загрузить максимум ${maxFiles} файлов`);
      return;
    }

    // Проверка размера и типа
    const validFiles: ChatFile[] = [];
    
    for (const file of files) {
      if (file.size > maxSize) {
        alert(`Файл ${file.name} слишком большой. Максимальный размер: ${(maxSize / 1024 / 1024).toFixed(0)}MB`);
        continue;
      }

      // Конвертируем файл в base64
      try {
        const base64 = await fileToBase64(file);
        const chatFile: ChatFile = {
          id: Date.now().toString() + Math.random().toString(36),
          name: file.name,
          type: file.type,
          size: file.size,
          data: base64,
          url: file.type.startsWith('image/') ? base64 : undefined,
        };
        validFiles.push(chatFile);
      } catch (error) {
        console.error('Ошибка обработки файла:', error);
        alert(`Ошибка при обработке файла ${file.name}`);
      }
    }

    if (validFiles.length > 0) {
      const newFiles = [...selectedFiles, ...validFiles];
      setSelectedFiles(newFiles);
      onFilesSelected(newFiles);
    }

    // Сбрасываем input для возможности повторной загрузки того же файла
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (fileId: string) => {
    const newFiles = selectedFiles.filter((f) => f.id !== fileId);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) {
      return <ImageIcon className="h-4 w-4" />;
    }
    return <FileText className="h-4 w-4" />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept={acceptedTypes.join(',')}
          onChange={handleFileSelect}
          className="hidden"
          disabled={disabled}
        />
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || selectedFiles.length >= maxFiles}
          className="h-8"
        >
          <Paperclip className="h-4 w-4 mr-1" />
          Прикрепить файл
        </Button>
        {selectedFiles.length > 0 && (
          <span className="text-xs text-muted-foreground">
            {selectedFiles.length} / {maxFiles}
          </span>
        )}
      </div>

      {selectedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {selectedFiles.map((file) => (
            <div
              key={file.id}
              className={cn(
                'flex items-center gap-2 px-2 py-1 rounded-md bg-muted text-sm',
                'border border-border'
              )}
            >
              {getFileIcon(file.type)}
              <span className="max-w-[150px] truncate" title={file.name}>
                {file.name}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatFileSize(file.size)}
              </span>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => removeFile(file.id)}
                className="h-5 w-5 p-0"
                disabled={disabled}
              >
                <X className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {selectedFiles.length > 0 && selectedFiles.some((f) => f.type.startsWith('image/')) && (
        <div className="grid grid-cols-2 gap-2">
          {selectedFiles
            .filter((f) => f.url && f.type.startsWith('image/'))
            .map((file) => (
              <div key={file.id} className="relative">
                <img
                  src={file.url}
                  alt={file.name}
                  className="w-full h-24 object-cover rounded-md border"
                />
              </div>
            ))}
        </div>
      )}
    </div>
  );
}

// Вспомогательная функция для конвертации файла в base64
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        resolve(reader.result);
      } else {
        reject(new Error('Ошибка чтения файла'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

