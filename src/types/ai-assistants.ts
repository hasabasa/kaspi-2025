// Типы для AI-ассистентов (Бухгалтер и Юрист)

export interface AIQuestion {
  question: string;
  context?: {
    business_type?: string; // ИП, ТОО
    revenue?: number;
    tax_regime?: string; // УСН, ОСНО, ПНС
    kaspi_status?: string;
  };
}

export interface AIAnswer {
  answer: string;
  sources?: Array<{
    text: string;
    source: string;
    relevance?: number;
  }>;
  confidence?: number;
  timestamp?: string;
  model?: string;
}

export interface TaxCalculation {
  revenue: number;
  expenses: number;
  tax_regime: string;
  business_type: string;
}

export interface TaxCalculationResult {
  calculation: {
    total_tax: number;
    income_tax?: number;
    vat?: number;
    social_tax?: number;
    breakdown: Record<string, number>;
  };
  explanation: string;
  tax_regime: string;
  business_type: string;
}

export interface DisputeRequest {
  dispute_type: 'return' | 'exchange' | 'complaint' | 'kaspi_violation' | 'other';
  situation: {
    description: string;
    order_id?: string;
    product_id?: string;
    customer_claim?: string;
  };
  context?: {
    business_type?: string;
    kaspi_status?: string;
  };
}

export interface DisputeResolution {
  analysis: string;
  recommendations: string[];
  legal_basis: Array<{
    text: string;
    source: string;
    article?: string;
  }>;
  dispute_type: string;
  confidence?: number;
  timestamp?: string;
}

export interface ChatFile {
  id: string;
  name: string;
  type: string;
  size: number;
  url?: string; // URL для отображения (для изображений)
  data?: string; // Base64 для отправки на сервер
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: AIAnswer['sources'];
  confidence?: number;
  files?: ChatFile[]; // Прикрепленные файлы
}

