# AI-бухгалтер и AI-юрист для платформы Kaspi

## 📋 Обзор

Документация по реализации двух специализированных AI-ассистентов для платформы Kaspi Demper:
- **AI-бухгалтер** - решение вопросов с налогами и расчетами в Республике Казахстан
- **AI-юрист** - помощь в решении спорных ситуаций и защита прав продавцов

---

## 🎯 Цели и задачи

### AI-бухгалтер
- Расчет налогов для продавцов Kaspi
- Консультации по налогообложению в РК
- Помощь с отчетностью
- Специфика работы с маркетплейсом Kaspi.kz

### AI-юрист
- Решение спорных ситуаций с покупателями
- Защита прав продавцов на Kaspi
- Консультации по законодательству РК
- Помощь с договорами и правилами маркетплейса

---

## 🛠 Технологический стек

### AI-модели

#### Основные варианты:

**1. OpenAI GPT-4 Turbo** (рекомендуется)
- **Модель**: `gpt-4-turbo-preview` или `gpt-4o`
- **Преимущества**:
  - Уже используется в проекте (AI-продажник)
  - Высокое качество ответов
  - Поддержка RAG (Retrieval-Augmented Generation)
  - Хорошая работа с документами
- **Стоимость**: ~$0.01-0.03 за 1K токенов
- **Использование**: Основная модель для обоих ассистентов

**2. Anthropic Claude 3.5 Sonnet** (резерв)
- **Модель**: `claude-3-5-sonnet-20241022`
- **Преимущества**:
  - Длинный контекст (200K токенов)
  - Отличная работа с длинными документами
  - Хорошая аналитика юридических текстов
- **Стоимость**: ~$0.003-0.015 за 1K токенов
- **Использование**: Для сложных юридических вопросов и анализа договоров

**3. Локальные модели** (опционально)
- **Ollama + Llama 3.1 70B**
- **Преимущества**: Приватность, нет платы за токены
- **Недостатки**: Требует GPU, ниже качество
- **Использование**: Для тестирования или приватных данных

#### Рекомендация:
- **Основной**: OpenAI GPT-4 Turbo
- **Резерв**: Claude 3.5 Sonnet для сложных юридических вопросов

---

### Векторные базы данных (RAG)

**Supabase Vector (pgvector)** - рекомендуется
- **Преимущества**:
  - Уже используется в проекте
  - Не требует дополнительных сервисов
  - Интеграция с существующей БД
  - Бесплатный тариф достаточен для начала
- **Использование**: Хранение эмбеддингов законов и нормативов

**Pinecone** (альтернатива)
- **Преимущества**: Простота, быстрый поиск
- **Недостатки**: Дополнительный сервис, платный тариф
- **Использование**: Если нужна более продвинутая векторная БД

**ChromaDB** (локально)
- **Преимущества**: Бесплатно, локально
- **Недостатки**: Требует инфраструктуры
- **Использование**: Для локальной разработки

---

### Python библиотеки

```python
# Для работы с AI
openai>=1.0.0              # OpenAI API
anthropic>=0.18.0          # Claude API (опционально)

# Для работы с документами и RAG
langchain>=0.1.0           # RAG и цепочки
langchain-openai          # OpenAI интеграция
langchain-community       # Дополнительные интеграции

# Для работы с документами
pypdf2                     # Парсинг PDF
beautifulsoup4             # Парсинг HTML
python-docx               # Парсинг Word документов

# Для работы с данными
pandas                     # Уже есть в проекте
numpy                      # Математические операции
```

---

## 📚 Источники данных

### Для AI-бухгалтера

#### 1. Налоговый кодекс РК
- **Источник**: https://adilet.zan.kz/rus/docs/K1000001_
- **Формат**: PDF/HTML
- **Метод получения**: Парсинг с сайта Adilet
- **Частота обновления**: Еженедельно
- **Приоритет**: Высокий

#### 2. Нормативные акты Министерства финансов РК
- **Источник**: https://www.gov.kz/memleket/entities/mf
- **Формат**: HTML/PDF
- **Метод получения**: Парсинг новостей и разъяснений
- **Частота обновления**: Ежедневно
- **Приоритет**: Высокий

#### 3. Разъяснения Налогового комитета МФ РК
- **Источник**: Официальные разъяснения НК МФ РК
- **Формат**: Структурированные FAQ
- **Метод получения**: Парсинг с официального сайта
- **Частота обновления**: При публикации новых разъяснений
- **Приоритет**: Средний

#### 4. Специфика для Kaspi
- **Правила налогообложения электронной коммерции**
  - НДС для маркетплейсов
  - Налоги с продаж через Kaspi
  - Отчетность для ИП и ТОО
- **Источник**: Официальные документы Kaspi + законодательство РК
- **Приоритет**: Критический

---

### Для AI-юриста

#### 1. Гражданский кодекс РК
- **Источник**: https://adilet.zan.kz/rus/docs/K990000001_
- **Формат**: PDF/HTML
- **Метод получения**: Парсинг с сайта Adilet
- **Частота обновления**: Еженедельно
- **Приоритет**: Высокий

#### 2. Закон "О защите прав потребителей"
- **Источник**: https://adilet.zan.kz/rus/docs/Z990000189_
- **Формат**: PDF/HTML
- **Метод получения**: Парсинг с сайта Adilet
- **Частота обновления**: При изменениях
- **Приоритет**: Высокий

#### 3. Закон "О торговле"
- **Источник**: https://adilet.zan.kz/rus/docs/Z990000189_
- **Формат**: PDF/HTML
- **Метод получения**: Парсинг с сайта Adilet
- **Частота обновления**: При изменениях
- **Приоритет**: Высокий

#### 4. Правила работы на Kaspi.kz
- **Источник**: Официальные документы Kaspi
- **Формат**: HTML/PDF
- **Метод получения**: Парсинг с сайта Kaspi
- **Частота обновления**: При обновлениях правил
- **Приоритет**: Критический

#### 5. Типичные спорные ситуации
- **Возвраты и обмены**
- **Споры с покупателями**
- **Нарушения правил маркетплейса**
- **Защита прав продавца**
- **Источник**: Анализ реальных кейсов + FAQ Kaspi
- **Приоритет**: Высокий

---

## 🏗 Архитектура системы

### Структура модулей

```
unified-backend/
├── services/
│   ├── ai_accountant.py          # AI-бухгалтер (основной модуль)
│   ├── ai_lawyer.py              # AI-юрист (основной модуль)
│   ├── knowledge_base.py         # Управление базами знаний
│   └── document_parser.py        # Парсинг документов
│
├── knowledge_bases/
│   ├── accountant/               # База знаний бухгалтера
│   │   ├── tax_code.json         # Налоговый кодекс (структурированный)
│   │   ├── kaspi_tax_rules.json  # Правила налогообложения Kaspi
│   │   ├── tax_faq.json          # FAQ по налогам
│   │   └── tax_calculations.json # Примеры расчетов
│   │
│   └── lawyer/                   # База знаний юриста
│       ├── civil_code.json       # Гражданский кодекс
│       ├── consumer_rights.json  # Закон о защите прав потребителей
│       ├── kaspi_rules.json      # Правила Kaspi
│       ├── dispute_cases.json    # Примеры спорных ситуаций
│       └── legal_faq.json       # FAQ по юридическим вопросам
│
├── routes/
│   ├── ai_accountant.py          # API endpoints для бухгалтера
│   └── ai_lawyer.py              # API endpoints для юриста
│
└── scripts/
    ├── parse_tax_code.py         # Парсинг Налогового кодекса
    ├── parse_kaspi_rules.py      # Парсинг правил Kaspi
    └── update_knowledge_base.py  # Обновление базы знаний
```

---

### Схема работы

```
Пользователь → API Endpoint → AI Service → Knowledge Base → LLM → Ответ
                ↓                ↓              ↓
            Валидация      Поиск релевантных  Генерация
                          документов (RAG)    ответа
```

---

## 💻 Примеры реализации

### AI-бухгалтер

```python
# unified-backend/services/ai_accountant.py

"""
@file: ai_accountant.py
@description: AI-бухгалтер для консультаций по налогам в РК
@dependencies: openai, langchain, supabase
@created: 2025-12-09
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from supabase import create_client

from config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class AIAccountant:
    """AI-бухгалтер для консультаций по налогам в Казахстане"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
    async def answer_tax_question(
        self, 
        question: str, 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ответ на вопрос по налогам с учетом контекста Kaspi
        
        Args:
            question: Вопрос пользователя
            user_context: Контекст пользователя (тип деятельности, доходы, режим налогообложения)
            
        Returns:
            dict: Ответ с анализом, рекомендациями и источниками
        """
        try:
            # Поиск релевантных документов
            relevant_docs = await self._search_knowledge_base(question)
            
            # Формирование промпта
            prompt = self._build_prompt(question, user_context, relevant_docs)
            
            # Генерация ответа через OpenAI
            response = await self._generate_response(prompt)
            
            return {
                "answer": response["content"],
                "sources": relevant_docs[:3],  # Топ-3 источника
                "confidence": self._calculate_confidence(relevant_docs),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка в answer_tax_question: {e}", exc_info=True)
            raise
    
    async def calculate_tax(
        self, 
        revenue: float, 
        expenses: float,
        tax_regime: str,
        business_type: str = "ИП"
    ) -> Dict[str, Any]:
        """
        Расчет налогов для продавца Kaspi
        
        Args:
            revenue: Доходы
            expenses: Расходы
            tax_regime: Режим налогообложения (УСН, ОСНО, ПНС)
            business_type: Тип бизнеса (ИП, ТОО)
            
        Returns:
            dict: Расчет налогов с пояснениями
        """
        try:
            # Получение правил для режима налогообложения
            tax_rules = await self._get_tax_rules(tax_regime, business_type)
            
            # Расчет налогов
            calculation = self._perform_calculation(
                revenue, expenses, tax_regime, tax_rules
            )
            
            # Генерация пояснений через AI
            explanation = await self._explain_calculation(calculation, tax_rules)
            
            return {
                "calculation": calculation,
                "explanation": explanation,
                "tax_regime": tax_regime,
                "business_type": business_type
            }
            
        except Exception as e:
            logger.error(f"Ошибка в calculate_tax: {e}", exc_info=True)
            raise
    
    async def _search_knowledge_base(self, query: str, top_k: int = 5) -> List[Dict]:
        """Поиск релевантных документов в базе знаний"""
        try:
            # Создание эмбеддинга запроса
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Поиск в Supabase Vector
            results = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.7,
                    "match_count": top_k,
                    "filter": {"category": "accountant"}
                }
            ).execute()
            
            return [
                {
                    "text": doc["text"],
                    "source": doc["metadata"].get("source", "unknown"),
                    "relevance": doc.get("similarity", 0)
                }
                for doc in results.data
            ]
            
        except Exception as e:
            logger.error(f"Ошибка поиска в базе знаний: {e}")
            return []
    
    def _build_prompt(
        self, 
        question: str, 
        user_context: Optional[Dict],
        relevant_docs: List[Dict]
    ) -> str:
        """Формирование промпта для AI"""
        context_str = ""
        if user_context:
            context_str = f"""
Контекст пользователя:
- Тип деятельности: {user_context.get('business_type', 'не указано')}
- Доходы: {user_context.get('revenue', 'не указано')}
- Режим налогообложения: {user_context.get('tax_regime', 'не указано')}
"""
        
        docs_str = "\n".join([
            f"Источник: {doc['source']}\n{doc['text'][:500]}"
            for doc in relevant_docs
        ])
        
        return f"""
Ты - AI-бухгалтер, специализирующийся на налогообложении в Казахстане
и работе с маркетплейсом Kaspi.kz.

{context_str}

Релевантные документы:
{docs_str}

Вопрос: {question}

Инструкции:
1. Ответь на вопрос, ссылаясь на конкретные статьи Налогового кодекса РК
2. Если вопрос касается Kaspi, учти специфику работы с маркетплейсом
3. Предоставь практические рекомендации
4. Укажи источники информации
5. Пиши на русском языке

Ответ:
"""
    
    async def _generate_response(self, prompt: str) -> Dict[str, str]:
        """Генерация ответа через OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Ты профессиональный бухгалтер в Казахстане, специализирующийся на налогообложении электронной коммерции и работе с маркетплейсами."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Низкая температура для точности
            max_tokens=1500
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": response.usage.dict()
        }
    
    def _calculate_confidence(self, relevant_docs: List[Dict]) -> float:
        """Расчет уверенности в ответе на основе релевантности документов"""
        if not relevant_docs:
            return 0.3
        
        avg_relevance = sum(doc.get("relevance", 0) for doc in relevant_docs) / len(relevant_docs)
        return min(avg_relevance, 1.0)
    
    async def _get_tax_rules(self, tax_regime: str, business_type: str) -> Dict:
        """Получение правил налогообложения для режима"""
        # Загрузка из базы знаний
        # ...
        pass
    
    def _perform_calculation(
        self, 
        revenue: float, 
        expenses: float,
        tax_regime: str,
        tax_rules: Dict
    ) -> Dict[str, float]:
        """Выполнение расчета налогов"""
        # Логика расчета в зависимости от режима
        # ...
        pass
    
    async def _explain_calculation(self, calculation: Dict, tax_rules: Dict) -> str:
        """Генерация пояснений к расчету через AI"""
        # ...
        pass
```

---

### AI-юрист

```python
# unified-backend/services/ai_lawyer.py

"""
@file: ai_lawyer.py
@description: AI-юрист для решения спорных ситуаций и защиты прав продавцов
@dependencies: openai, langchain, supabase
@created: 2025-12-09
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

import openai
from langchain.embeddings import OpenAIEmbeddings
from supabase import create_client

from config import settings
from core.logger import get_logger

logger = get_logger(__name__)


class AILawyer:
    """AI-юрист для защиты прав продавцов на Kaspi"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
    async def resolve_dispute(
        self,
        dispute_type: str,
        situation: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Решение спорной ситуации с покупателем или Kaspi
        
        Args:
            dispute_type: Тип спора (return, exchange, complaint, kaspi_violation)
            situation: Описание ситуации
            user_context: Контекст пользователя
            
        Returns:
            dict: Анализ, рекомендации и правовая база
        """
        try:
            # Поиск релевантных законов и правил
            relevant_laws = await self._search_legal_base(dispute_type, situation)
            
            # Формирование промпта
            prompt = self._build_legal_prompt(dispute_type, situation, relevant_laws, user_context)
            
            # Генерация ответа
            response = await self._generate_legal_response(prompt)
            
            # Извлечение рекомендаций
            recommendations = self._extract_recommendations(response["content"])
            
            return {
                "analysis": response["content"],
                "recommendations": recommendations,
                "legal_basis": relevant_laws[:3],
                "dispute_type": dispute_type,
                "confidence": self._calculate_confidence(relevant_laws),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ошибка в resolve_dispute: {e}", exc_info=True)
            raise
    
    async def analyze_contract(
        self,
        contract_text: str,
        contract_type: str = "kaspi_agreement"
    ) -> Dict[str, Any]:
        """
        Анализ договора или соглашения
        
        Args:
            contract_text: Текст договора
            contract_type: Тип договора
            
        Returns:
            dict: Анализ договора с выявлением рисков
        """
        try:
            # Поиск релевантных законов
            relevant_laws = await self._search_legal_base("contract_analysis", {"type": contract_type})
            
            # Анализ через AI
            analysis = await self._analyze_contract_ai(contract_text, relevant_laws)
            
            return {
                "analysis": analysis,
                "risks": self._extract_risks(analysis),
                "recommendations": self._extract_contract_recommendations(analysis),
                "legal_basis": relevant_laws
            }
            
        except Exception as e:
            logger.error(f"Ошибка в analyze_contract: {e}", exc_info=True)
            raise
    
    async def _search_legal_base(
        self, 
        dispute_type: str, 
        situation: Dict
    ) -> List[Dict]:
        """Поиск релевантных законов в базе знаний"""
        try:
            # Формирование запроса для поиска
            query = f"{dispute_type} {situation.get('description', '')}"
            
            # Создание эмбеддинга
            query_embedding = await self.embeddings.aembed_query(query)
            
            # Поиск в Supabase Vector
            results = self.supabase.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": 0.7,
                    "match_count": 5,
                    "filter": {"category": "lawyer", "type": dispute_type}
                }
            ).execute()
            
            return [
                {
                    "text": doc["text"],
                    "source": doc["metadata"].get("source", "unknown"),
                    "article": doc["metadata"].get("article", ""),
                    "relevance": doc.get("similarity", 0)
                }
                for doc in results.data
            ]
            
        except Exception as e:
            logger.error(f"Ошибка поиска в юридической базе: {e}")
            return []
    
    def _build_legal_prompt(
        self,
        dispute_type: str,
        situation: Dict,
        relevant_laws: List[Dict],
        user_context: Optional[Dict]
    ) -> str:
        """Формирование юридического промпта"""
        context_str = ""
        if user_context:
            context_str = f"""
Контекст продавца:
- Тип бизнеса: {user_context.get('business_type', 'не указано')}
- Статус на Kaspi: {user_context.get('kaspi_status', 'не указано')}
"""
        
        laws_str = "\n".join([
            f"Статья: {law.get('article', 'N/A')}\nИсточник: {law['source']}\n{law['text'][:500]}"
            for law in relevant_laws
        ])
        
        return f"""
Ты - AI-юрист, специализирующийся на защите прав продавцов
на маркетплейсе Kaspi.kz в Казахстане.

Тип спора: {dispute_type}
Ситуация: {situation.get('description', '')}

{context_str}

Релевантные законы и правила:
{laws_str}

Предоставь:
1. Анализ ситуации с точки зрения законодательства РК
2. Рекомендации по защите прав продавца
3. Пошаговые действия для решения спора
4. Ссылки на конкретные статьи законов и правила Kaspi
5. Возможные риски и как их избежать

Пиши на русском языке, будь конкретным и практичным.

Ответ:
"""
    
    async def _generate_legal_response(self, prompt: str) -> Dict[str, str]:
        """Генерация юридического ответа через OpenAI"""
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system",
                    "content": "Ты профессиональный юрист в Казахстане, специализирующийся на защите прав продавцов на маркетплейсах и электронной коммерции."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,  # Очень низкая для юридической точности
            max_tokens=2000
        )
        
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": response.usage.dict()
        }
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Извлечение рекомендаций из анализа"""
        # Простой парсинг или использование структурированного вывода
        # ...
        return []
    
    def _calculate_confidence(self, relevant_laws: List[Dict]) -> float:
        """Расчет уверенности на основе релевантности законов"""
        if not relevant_laws:
            return 0.3
        
        avg_relevance = sum(law.get("relevance", 0) for law in relevant_laws) / len(relevant_laws)
        return min(avg_relevance, 1.0)
    
    async def _analyze_contract_ai(self, contract_text: str, relevant_laws: List[Dict]) -> str:
        """Анализ договора через AI"""
        # ...
        pass
    
    def _extract_risks(self, analysis: str) -> List[str]:
        """Извлечение рисков из анализа"""
        # ...
        return []
    
    def _extract_contract_recommendations(self, analysis: str) -> List[str]:
        """Извлечение рекомендаций по договору"""
        # ...
        return []
```

---

## 🔌 API Endpoints

### AI-бухгалтер

```python
# unified-backend/routes/ai_accountant.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.ai_accountant import AIAccountant

router = APIRouter(prefix="/api/v1/ai-accountant", tags=["AI Accountant"])

class TaxQuestionRequest(BaseModel):
    question: str
    user_context: Optional[Dict[str, Any]] = None

class TaxCalculationRequest(BaseModel):
    revenue: float
    expenses: float
    tax_regime: str
    business_type: str = "ИП"

@router.post("/ask")
async def ask_tax_question(request: TaxQuestionRequest):
    """Задать вопрос по налогам"""
    accountant = AIAccountant()
    try:
        result = await accountant.answer_tax_question(
            question=request.question,
            user_context=request.user_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
async def calculate_tax(request: TaxCalculationRequest):
    """Рассчитать налоги"""
    accountant = AIAccountant()
    try:
        result = await accountant.calculate_tax(
            revenue=request.revenue,
            expenses=request.expenses,
            tax_regime=request.tax_regime,
            business_type=request.business_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### AI-юрист

```python
# unified-backend/routes/ai_lawyer.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from services.ai_lawyer import AILawyer

router = APIRouter(prefix="/api/v1/ai-lawyer", tags=["AI Lawyer"])

class DisputeRequest(BaseModel):
    dispute_type: str
    situation: Dict[str, Any]
    user_context: Optional[Dict[str, Any]] = None

class ContractAnalysisRequest(BaseModel):
    contract_text: str
    contract_type: str = "kaspi_agreement"

@router.post("/resolve-dispute")
async def resolve_dispute(request: DisputeRequest):
    """Решить спорную ситуацию"""
    lawyer = AILawyer()
    try:
        result = await lawyer.resolve_dispute(
            dispute_type=request.dispute_type,
            situation=request.situation,
            user_context=request.user_context
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-contract")
async def analyze_contract(request: ContractAnalysisRequest):
    """Проанализировать договор"""
    lawyer = AILawyer()
    try:
        result = await lawyer.analyze_contract(
            contract_text=request.contract_text,
            contract_type=request.contract_type
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 База данных

### Таблица для хранения знаний

```sql
-- Миграция для создания таблицы knowledge_base

CREATE TABLE IF NOT EXISTS knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    text TEXT NOT NULL,
    category TEXT NOT NULL, -- 'accountant' или 'lawyer'
    subcategory TEXT, -- 'tax_code', 'kaspi_rules', etc.
    source TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(1536), -- OpenAI embedding размерность
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индекс для векторного поиска
CREATE INDEX IF NOT EXISTS knowledge_base_embedding_idx 
ON knowledge_base 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Индекс по категории
CREATE INDEX IF NOT EXISTS knowledge_base_category_idx 
ON knowledge_base(category, subcategory);

-- Функция для поиска похожих документов
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
    match_threshold float,
    match_count int,
    filter jsonb DEFAULT '{}'
)
RETURNS TABLE (
    id uuid,
    text text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        knowledge_base.id,
        knowledge_base.text,
        knowledge_base.metadata,
        1 - (knowledge_base.embedding <=> query_embedding) as similarity
    FROM knowledge_base
    WHERE 
        1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
        AND (filter = '{}' OR knowledge_base.metadata @> filter)
    ORDER BY knowledge_base.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
```

---

## 🚀 План внедрения

### Этап 1: Подготовка баз знаний (1-2 недели)

1. **Парсинг Налогового кодекса РК**
   - Создать скрипт `scripts/parse_tax_code.py`
   - Парсинг с сайта Adilet
   - Структурирование по статьям
   - Загрузка в векторную БД

2. **Парсинг правил Kaspi**
   - Создать скрипт `scripts/parse_kaspi_rules.py`
   - Парсинг официальных документов Kaspi
   - Структурирование правил
   - Загрузка в векторную БД

3. **Создание FAQ**
   - Сбор типичных вопросов
   - Создание структурированных ответов
   - Загрузка в базу знаний

4. **Настройка Supabase Vector**
   - Создание таблицы `knowledge_base`
   - Настройка индексов
   - Тестирование поиска

### Этап 2: Разработка AI-модулей (2-3 недели)

1. **Создание `ai_accountant.py`**
   - Реализация основного класса
   - Интеграция с OpenAI
   - Интеграция с базой знаний
   - Тестирование на реальных вопросах

2. **Создание `ai_lawyer.py`**
   - Реализация основного класса
   - Интеграция с OpenAI
   - Интеграция с базой знаний
   - Тестирование на реальных ситуациях

3. **Создание `knowledge_base.py`**
   - Управление базой знаний
   - Функции поиска и обновления
   - Мониторинг качества

### Этап 3: Интеграция в платформу (1 неделя)

1. **API endpoints**
   - Создание роутов для бухгалтера
   - Создание роутов для юриста
   - Интеграция в `main.py`

2. **UI компоненты**
   - Создание страниц для AI-ассистентов
   - Интеграция с существующим фронтендом
   - Тестирование UX

3. **Документация API**
   - Swagger документация
   - Примеры использования

### Этап 4: Тестирование и улучшение (1-2 недели)

1. **Тестирование с реальными пользователями**
   - Сбор вопросов от продавцов
   - Тестирование ответов
   - Сбор feedback

2. **Улучшение промптов**
   - Оптимизация на основе feedback
   - A/B тестирование промптов
   - Улучшение качества ответов

3. **Мониторинг и аналитика**
   - Отслеживание использования
   - Анализ популярных вопросов
   - Метрики качества ответов

---

## 💰 Стоимость и ресурсы

### Примерные затраты:

- **OpenAI API**: ~$50-200/месяц (зависит от использования)
  - GPT-4 Turbo: $0.01-0.03 за 1K токенов
  - Embeddings: $0.0001 за 1K токенов
  
- **Supabase**: Уже есть (бесплатный тариф достаточен)
  - Хранение векторов: бесплатно до 500MB
  - Запросы: бесплатно до 50K/месяц

- **Парсинг данных**: Бесплатно (собственные скрипты)

- **Разработка**: 4-6 недель работы разработчика

### Оптимизация затрат:

1. Кэширование частых вопросов
2. Использование более дешевых моделей для простых вопросов
3. Batch обработка запросов
4. Мониторинг использования токенов

---

## 📈 Метрики успеха

### Для AI-бухгалтера:

- **Точность ответов**: >85% правильных ответов
- **Время ответа**: <5 секунд
- **Удовлетворенность пользователей**: >4.5/5
- **Использование**: >50% активных пользователей

### Для AI-юриста:

- **Точность рекомендаций**: >80% полезных рекомендаций
- **Время ответа**: <7 секунд
- **Удовлетворенность пользователей**: >4.5/5
- **Использование**: >40% активных пользователей

---

## 🔒 Безопасность и ограничения

### Ограничения:

1. **Не является заменой профессионального бухгалтера/юриста**
   - AI предоставляет консультации, но не заменяет специалистов
   - Для сложных случаев рекомендуется обращаться к профессионалам

2. **Актуальность информации**
   - Законы могут изменяться
   - Необходимо регулярное обновление базы знаний

3. **Конфиденциальность**
   - Данные пользователей не передаются третьим лицам
   - Используется только для генерации ответов

### Безопасность:

1. **Валидация входных данных**
2. **Rate limiting** для предотвращения злоупотреблений
3. **Логирование** всех запросов
4. **Мониторинг** использования API

---

## 📝 Чеклист реализации

### Подготовка:
- [ ] Настроить OpenAI API ключ
- [ ] Настроить Supabase Vector
- [ ] Создать структуру папок
- [ ] Установить зависимости

### База знаний:
- [ ] Парсинг Налогового кодекса РК
- [ ] Парсинг правил Kaspi
- [ ] Создание FAQ
- [ ] Загрузка в векторную БД

### Разработка:
- [ ] Реализация `ai_accountant.py`
- [ ] Реализация `ai_lawyer.py`
- [ ] Создание API endpoints
- [ ] Интеграция в `main.py`

### Тестирование:
- [ ] Unit тесты
- [ ] Интеграционные тесты
- [ ] Тестирование с реальными вопросами
- [ ] Сбор feedback

### Деплой:
- [ ] Деплой на production
- [ ] Мониторинг
- [ ] Документация для пользователей

---

**Дата создания**: 2025-12-09  
**Версия**: 1.0  
**Статус**: Планирование


