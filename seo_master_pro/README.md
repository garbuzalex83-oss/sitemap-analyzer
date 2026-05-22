# SEO Master PRO

Профессиональная система SEO-аудита уровня Enterprise для комплексного анализа сайтов.

## 🚀 Возможности

### Ядро системы (core_crawler.py)
- **SiteCrawler** - Профессиональный краулер сайтов
  - Сканирование всех URL с проверкой статус-кодов
  - Сбор Title, Description, H1-H6
  - Извлечение canonical, meta robots, hreflang
  - Анализ внутренней и внешней перелинковки
  - Проверка изображений (alt, width, height, lazy loading)
  - Извлечение Schema.org разметки
  - Определение типа страницы
  - Выявление технических проблем с приоритетами

- **SitemapAnalyzer** - Анализатор sitemap.xml
  - Автоматический поиск sitemap.xml
  - Парсинг индексных и обычных sitemap
  - Рекурсивная обработка вложенных sitemap
  - Проверка на битые URL
  - Выявление старых страниц

- **RobotsTxtAnalyzer** - Анализатор robots.txt
  - Проверка наличия и доступности
  - Парсинг всех правил
  - Выявление закрытия важных путей
  - Обнаружение конфликтных правил
  - Симулятор доступа к URL

### Модули аудита

#### Meta Tags Auditor (`modules/meta_auditor.py`)
- ✅ Проверка Title (длина, дубли, переспам)
- ✅ Проверка Description (длина, уникальность)
- ✅ Анализ заголовков H1-H6
- ✅ Оценка структуры заголовков (0-100)
- ✅ Генерация превью сниппета Google
- ✅ Рекомендации по исправлению

#### Commercial Factors Auditor (`modules/commercial_auditor.py`)
- ✅ Анализ 16 коммерческих факторов:
  - Цена, кнопка "Купить", корзина
  - Контакты, доставка, оплата
  - Гарантия, возврат, отзывы
  - Trust badges, наличие, SKU
  - Бренд, характеристики, CTA
- ✅ Коммерческая оценка (0-100)
- ✅ Оценка доверия (0-100)
- ✅ Готовность к конверсии
- ✅ Сравнение с конкурентами

#### JavaScript SEO Analyzer (`modules/js_renderer_analyzer.py`)
- ✅ Сравнение контента до/после рендеринга
- ✅ Проверка изменений Title, H1, Description
- ✅ Анализ JS-ссылок и контента
- ✅ Оценка совместимости с Googlebot
- ✅ Рекомендации по SSR

#### Report Builder (`modules/report_builder.py`)
- ✅ Drag-and-Drop конструктор отчетов
- ✅ 5 готовых шаблонов:
  - Технический аудит
  - On-Page SEO
  - E-commerce
  - JavaScript SEO
  - Полный отчет
- ✅ Создание пользовательских шаблонов
- ✅ White-label брендирование
- ✅ Экспорт в HTML и JSON

## 📦 Установка

```bash
cd /workspace/seo_master_pro
```

Зависимости не требуются (только стандартная библиотека Python).

## 💻 Использование

### Консольный запуск

```bash
# Анализ product страницы
python seo_master_pro.py https://example.com/product/nike product

# Анализ category страницы
python seo_master_pro.py https://example.com/category/sneakers category

# Анализ homepage
python seo_master_pro.py https://example.com homepage
```

### Программное использование

```python
from modules.meta_auditor import MetaTagsAuditor
from modules.commercial_auditor import CommercialFactorsAuditor
from modules.js_renderer_analyzer import JavaScriptSEOAnalyzer
from modules.report_builder import ReportBuilder

# Анализ мета-тегов
auditor = MetaTagsAuditor()
result = auditor.analyze_page(url, html, page_type='product')

# Анализ коммерческих факторов
commercial = CommercialFactorsAuditor()
comm_result = commercial.analyze_page(url, html, page_type='product')

# Анализ JS рендеринга
js_analyzer = JavaScriptSEOAnalyzer()
js_result = js_analyzer.analyze_rendering(url, html_before, html_after)

# Генерация отчета
builder = ReportBuilder()
report = builder.generate_report(
    template_id='full_report',
    audit_data={
        'meta_tags': result,
        'commercial': comm_result,
        'javascript': js_result
    },
    branding={'company_name': 'My Agency'}
)

# Экспорт
html = builder.export_to_html(report)
json = builder.export_to_json(report)
```

## 📊 Система оценок

### Общая оценка SEO (0-100)
- **90-100**: Отлично 🟢
- **75-89**: Хорошо 🔵
- **50-74**: Требует улучшений 🟡
- **0-49**: Критическое состояние 🔴

### Веса категорий
- Мета-теги: 25%
- Коммерческие факторы: 25%
- JavaScript рендеринг: 20%
- Crawl данные: 30%

### Приоритеты проблем
- **Critical**: Требует немедленного исправления
- **High**: Важно исправить в ближайшее время
- **Medium**: Рекомендуется исправить
- **Low**: Желательно исправить

## 📁 Структура проекта

```
/workspace/seo_master_pro/
├── core/
│   └── core_crawler.py      # Ядро: Crawler, Sitemap, Robots
├── modules/
│   ├── meta_auditor.py       # Анализ мета-тегов
│   ├── commercial_auditor.py # Коммерческие факторы
│   ├── js_renderer_analyzer.py # JS рендеринг
│   └── report_builder.py     # Конструктор отчетов
├── templates/                # HTML шаблоны
├── static/                   # CSS/JS
├── reports/                  # Сгенерированные отчеты
└── seo_master_pro.py         # Главный скрипт
```

## 🎯 Примеры отчетов

Отчеты сохраняются в папку `reports/`:
- `seo_report_YYYYMMDD_HHMMSS.html` - HTML версия
- `seo_report_YYYYMMDD_HHMMSS.json` - JSON версия

## 🔥 Уникальные возможности

1. **Типизация страниц** - Разные требования для product/category/article
2. **Коммерческие факторы** - Специализированный анализ для e-commerce
3. **JS рендеринг** - Проверка видимости контента для Googlebot
4. **Drag-and-Drop отчеты** - Гибкий конструктор без аналогов
5. **White-label** - Полное брендирование под вашу компанию
6. **Actionable recommendations** - Конкретные шаги для исправления

## 📈 Roadmap

### Этап 1 (реализовано) ✅
- [x] Ядро краулера
- [x] Анализ мета-тегов
- [x] Коммерческие факторы
- [x] JS рендеринг
- [x] Конструктор отчетов

### Этап 2 (в разработке)
- [ ] Интеграция с Playwright для реального рендеринга
- [ ] Анализ дублей контента
- [ ] Поиск thin content
- [ ] Анализ изображений
- [ ] Проверка hreflang

### Этап 3 (планируется)
- [ ] Лог-файл анализатор
- [ ] Сравнение с конкурентами
- [ ] Мониторинг изменений
- [ ] AI-рекомендации
- [ ] Веб-интерфейс

## 📝 Лицензия

SEO Master PRO - профессиональный инструмент для SEO-аудита.

---

**Создано для профессионального SEO аудита сайтов любого масштаба.**
