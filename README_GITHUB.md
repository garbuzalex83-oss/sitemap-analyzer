# 🔍 Sitemap Analyzer - Professional SEO Tool

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Комплексный инструмент для анализа и аудита sitemap.xml с SEO проверками**

[Особенности](#-особенности) •
[Установка](#-установка) •
[Использование](#-использование) •
[Примеры](#-примеры) •
[Документация](#-документация)

![Demo](https://via.placeholder.com/800x400/667eea/ffffff?text=Sitemap+Analyzer+Demo)

</div>

---

## 📋 Содержание

- [О проекте](#-о-проекте)
- [Особенности](#-особенности)
- [Требования](#-требования)
- [Установка](#-установка)
- [Использование](#-использование)
- [Варианты запуска](#-варианты-запуска)
- [Что проверяется](#-что-проверяется)
- [Примеры](#-примеры)
- [Документация](#-документация)
- [Автор](#-автор)
- [Лицензия](#-лицензия)

---

## 🎯 О проекте

**Sitemap Analyzer** - это профессиональный инструмент для SEO специалистов и веб-разработчиков, который позволяет проводить комплексный анализ sitemap.xml файлов с выявлением всех критических ошибок, проблем и возможностей для оптимизации.

### 💡 Зачем это нужно?

- ✅ Автоматическая проверка всех URL в sitemap
- ✅ Выявление технических ошибок (404, 500, редиректы)
- ✅ Поиск дубликатов и неправильных URL
- ✅ Валидация XML структуры и атрибутов
- ✅ SEO аудит контента страниц
- ✅ Экономия времени на ручной проверке

---

## ✨ Особенности

### 🔧 Базовая версия (Console)
- 📊 Парсинг XML sitemap и Sitemap Index
- 🔍 Валидация формата URL
- 🔗 Проверка HTTP статусов (200, 301, 404, 500+)
- 📅 Валидация атрибутов (lastmod, changefreq, priority)
- 🔄 Поиск дубликатов URL
- 🌐 Проверка внешних доменов
- 📝 Детальные отчеты в консоли и файл

### 🌐 Веб-интерфейс (Flask)
- 🎨 Красивый UI с градиентами
- 📊 Визуальная статистика с карточками
- 🎯 Оценка качества sitemap (0-100 баллов)
- 📋 Интерактивные отчеты
- 💡 Группировка проблем по типам
- 📱 Адаптивный дизайн

### 🚀 Pro версия (Advanced SEO)
- 🔬 Глубокая проверка контента страниц
- 📝 Анализ Title и Meta Description
- 🏷️ Проверка заголовков H1
- 🔗 Canonical и Robots meta теги
- 🖼️ Изображения без ALT атрибутов
- 🔄 Поиск дублированного контента
- ⚡ Анализ скорости загрузки
- 📊 Комплексные SEO метрики

---

## 📦 Требования

- **Python:** 3.7 или выше
- **Библиотеки:**
  - `requests` - HTTP запросы
  - `beautifulsoup4` - парсинг HTML (для Pro версии)
  - `flask` - веб-интерфейс (опционально)

---

## 🚀 Установка

### Шаг 1: Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/sitemap-analyzer.git
cd sitemap-analyzer
```

### Шаг 2: Установите зависимости

**Автоматическая установка:**
```bash
pip install -r requirements.txt
```

**Или вручную:**
```bash
pip install requests beautifulsoup4 flask
```

**Для Windows с Python 3.11+:**
```cmd
pip install requests beautifulsoup4 flask --break-system-packages
```

---

## 💻 Использование

### Вариант 1: Консольная версия (Рекомендуется)

```bash
python sitemap_analyzer.py
```

Интерактивный режим:
1. Введите URL sitemap: `https://example.com/sitemap.xml`
2. Проверять HTTP статусы? `[y/N]`
3. Сохранить детальный отчет? `[y/N]`

**С параметром командной строки:**
```bash
python sitemap_analyzer.py https://example.com/sitemap.xml
```

### Вариант 2: Веб-интерфейс

```bash
python sitemap_analyzer_web.py
```

Откройте браузер: `http://localhost:5000`

### Вариант 3: Pro версия с SEO анализом

```bash
python sitemap_analyzer_pro.py
```

---

## 🎨 Варианты запуска

| Версия | Команда | Скорость | Детальность | Для кого |
|--------|---------|----------|-------------|----------|
| **Console** | `python sitemap_analyzer.py` | ⚡⚡⚡ Быстро | ⭐⭐ Средняя | Ежедневная проверка |
| **Web UI** | `python sitemap_analyzer_web.py` | ⚡⚡ Средне | ⭐⭐ Средняя | Презентации клиентам |
| **Pro** | `python sitemap_analyzer_pro.py` | ⚡ Медленно | ⭐⭐⭐ Максимальная | Глубокий SEO аудит |

---

## 🔍 Что проверяется

### ✅ XML Структура
- Валидность XML синтаксиса
- Корректность namespace
- Наличие обязательных тегов
- Размер файла (лимит 50 MB)
- Количество URL (лимит 50,000)

### 🔗 URL Анализ
- Формат URL (протокол, длина)
- Дубликаты URL
- Внешние домены
- Запрещенные символы
- Незакодированная кириллица
- Пробелы в URL

### 📅 Атрибуты
- **lastmod**: формат даты (ISO 8601)
- **changefreq**: валидные значения (always, hourly, daily, weekly, monthly, yearly, never)
- **priority**: диапазон 0.0 - 1.0

### 🌐 HTTP Статусы
- ✅ 200 - страница доступна
- ⚠️ 301/302 - редиректы (не должны быть в sitemap)
- ❌ 404/410 - страница не найдена
- ❌ 500+ - серверные ошибки

### 🎯 SEO Метрики (Pro версия)
- Title: длина, дубликаты, отсутствие
- Meta Description: длина, качество
- H1 заголовки: количество, содержание
- Canonical URL: соответствие
- Robots meta: проверка noindex
- ALT атрибуты изображений
- Скорость загрузки страниц

---

## 📊 Примеры

### Пример 1: Быстрая проверка

```bash
python sitemap_analyzer.py https://example.com/sitemap.xml
```

**Результат:**
```
╔═══════════════════════════════════════════════════════════════╗
║              📊 ОТЧЕТ ПО АНАЛИЗУ SITEMAP                    ║
╚═══════════════════════════════════════════════════════════════╝

📈 ОСНОВНАЯ СТАТИСТИКА:
  • Всего URL в sitemap: 1234
  • URL своего домена: 1234
  • Дубликатов: 5
  • Проблем с протоколом: 2

💡 РЕКОМЕНДАЦИИ:
  ⚠️ Удалите 5 дубликатов URL
  ⚠️ Исправьте 2 несоответствия протокола

✅ ОТЛИЧНО! Sitemap в хорошем состоянии
```

### Пример 2: С проверкой HTTP

```python
from sitemap_analyzer import SitemapAnalyzer

analyzer = SitemapAnalyzer('https://example.com/sitemap.xml')
analyzer.run(check_status=True, save_report=True)
```

### Пример 3: Сравнение двух версий sitemap

```python
from sitemap_analyzer import SitemapAnalyzer

# Анализ старой версии
old = SitemapAnalyzer('https://example.com/old-sitemap.xml')
old.run()

# Анализ новой версии
new = SitemapAnalyzer('https://example.com/sitemap.xml')
new.run()

# Сравнение
print(f"Изменение URL: {new.statistics['total_urls'] - old.statistics['total_urls']}")
```

---

## 📚 Документация

### Основные файлы

| Файл | Описание |
|------|----------|
| `sitemap_analyzer.py` | Базовый консольный анализатор |
| `sitemap_analyzer_web.py` | Веб-интерфейс на Flask |
| `sitemap_analyzer_pro.py` | Расширенная версия с SEO проверками |
| `examples.py` | 8 практических примеров использования |
| `test_demo.py` | Демонстрационный тест без реального sitemap |

### Дополнительная документация

- 📖 [STEP_BY_STEP.txt](STEP_BY_STEP.txt) - Пошаговая инструкция
- 📋 [CHEATSHEET.txt](CHEATSHEET.txt) - Шпаргалка с командами
- 🚀 [QUICKSTART.txt](QUICKSTART.txt) - Быстрый старт
- 📚 [INDEX.txt](INDEX.txt) - Обзор пакета

---

## 🎓 SEO Best Practices

### ✅ Что делать:
- Обновляйте sitemap при добавлении нового контента
- Указывайте реальные даты в `lastmod`
- Используйте правильный `priority` для важных страниц
- Удаляйте старые и неактуальные URL
- Используйте gzip сжатие (sitemap.xml.gz)
- Указывайте путь к sitemap в `robots.txt`
- Отправляйте sitemap в Google Search Console

### ❌ Чего избегать:
- Не включайте URL с кодами 404/410
- Не добавляйте URL с редиректами 301/302
- Не используйте внешние домены
- Не превышайте лимит 50,000 URL в одном файле
- Не добавляйте страницы с `noindex`
- Не забывайте про единый протокол (https)

---

## ⚡ Производительность

| Тип анализа | 100 URL | 1,000 URL | 10,000 URL |
|-------------|---------|-----------|------------|
| Базовый | ~10 сек | ~1 мин | ~10 мин |
| + HTTP проверка | ~2 мин | ~20 мин | ~3 часа |
| Pro (с контентом) | ~5 мин | ~50 мин | несколько часов |

**Рекомендации:**
- Для больших sitemap (10,000+ URL) используйте базовую версию без HTTP проверки
- Pro версию используйте только для критически важных разделов
- Запускайте полный анализ в нерабочее время

---

## 🛠️ Разработка

### Структура проекта

```
sitemap-analyzer/
├── sitemap_analyzer.py          # Базовый анализатор
├── sitemap_analyzer_web.py      # Веб-интерфейс
├── sitemap_analyzer_pro.py      # Pro версия
├── requirements.txt             # Зависимости
├── examples.py                  # Примеры использования
├── test_demo.py                 # Тесты
├── README.md                    # Документация
├── STEP_BY_STEP.txt            # Инструкция
├── CHEATSHEET.txt              # Шпаргалка
├── QUICKSTART.txt              # Быстрый старт
└── INDEX.txt                   # Обзор пакета
```

### Запуск тестов

```bash
python test_demo.py
```

### Примеры кода

```bash
python examples.py
```

---

## 🤝 Вклад в проект

Приветствуются любые вклады! Если вы хотите улучшить проект:

1. Форкните репозиторий
2. Создайте ветку для новой функции (`git checkout -b feature/AmazingFeature`)
3. Закоммитьте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте в ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

---

## 🐛 Сообщить о проблеме

Если вы нашли баг или у вас есть предложение:

1. Откройте [Issue](https://github.com/yourusername/sitemap-analyzer/issues)
2. Опишите проблему детально
3. Приложите скриншоты (если возможно)
4. Укажите версию Python и ОС

---

## 📞 Контакты и поддержка

- 🌐 **Website:** [garbuz.online](https://garbuz.online)
- 📧 **Email:** support@garbuz.online
- 💼 **LinkedIn:** [Alexander Garbuz](https://linkedin.com/in/your-profile)
- 🐦 **Twitter:** [@yourusername](https://twitter.com/yourusername)

---

## 👨‍💻 Автор

**Alexander Garbuz**
- SEO Specialist & Web Developer
- Brand: GARBUZ.ONLINE
- Специализация: SEO оптимизация, веб-разработка, Python инструменты

---

## ⭐ Поддержите проект

Если этот инструмент был вам полезен:

- ⭐ Поставьте звезду на GitHub
- 🔄 Поделитесь с коллегами
- 💬 Оставьте отзыв
- 🐛 Сообщите о багах
- 💡 Предложите улучшения

---

## 📄 Лицензия

Этот проект распространяется под лицензией MIT - см. файл [LICENSE](LICENSE) для деталей.

```
MIT License

Copyright (c) 2025 Alexander Garbuz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

---

## 🙏 Благодарности

- Python Software Foundation за отличный язык программирования
- Сообществу SEO специалистов за обратную связь
- Всем контрибьюторам проекта

---

<div align="center">

**Сделано с ❤️ для SEO сообщества**

[⬆ Вернуться к началу](#-sitemap-analyzer---professional-seo-tool)

</div>
