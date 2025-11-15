#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Примеры использования анализаторов sitemap
Тестовые сценарии и демонстрация возможностей
"""

# ============================================================================
# ПРИМЕР 1: Быстрый базовый анализ
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║                    ПРИМЕР 1: Базовый анализ                  ║
╚═══════════════════════════════════════════════════════════════╝
""")

from sitemap_analyzer import SitemapAnalyzer

# Простой анализ без проверки HTTP статусов
analyzer = SitemapAnalyzer('https://example.com/sitemap.xml')
analyzer.run(check_status=False, save_report=False)

print("\n✅ Базовый анализ завершен\n")


# ============================================================================
# ПРИМЕР 2: Полный анализ с HTTP проверкой
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║          ПРИМЕР 2: Полный анализ с HTTP статусами            ║
╚═══════════════════════════════════════════════════════════════╝
""")

# Анализ с проверкой доступности каждого URL
analyzer2 = SitemapAnalyzer('https://example.com/sitemap.xml')
analyzer2.run(check_status=True, save_report=True)

print("\n✅ Полный анализ завершен, отчет сохранен в sitemap_report.txt\n")


# ============================================================================
# ПРИМЕР 3: Расширенный SEO анализ с проверкой контента
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║       ПРИМЕР 3: Расширенный SEO анализ (Pro версия)          ║
╚═══════════════════════════════════════════════════════════════╝
""")

from sitemap_analyzer_pro import AdvancedSitemapAnalyzer

# Глубокая проверка с анализом контента страниц
analyzer3 = AdvancedSitemapAnalyzer('https://example.com/sitemap.xml', deep_check=True)
analyzer3.run()

print("\n✅ Расширенный SEO анализ завершен\n")


# ============================================================================
# ПРИМЕР 4: Анализ нескольких sitemap
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║            ПРИМЕР 4: Анализ нескольких sitemap                ║
╚═══════════════════════════════════════════════════════════════╝
""")

sitemaps = [
    'https://example.com/sitemap.xml',
    'https://example.com/sitemap-posts.xml',
    'https://example.com/sitemap-pages.xml',
]

results = {}

for sitemap_url in sitemaps:
    print(f"\n📍 Анализ: {sitemap_url}")
    analyzer = SitemapAnalyzer(sitemap_url)
    analyzer.run(check_status=False)
    
    results[sitemap_url] = {
        'total_urls': analyzer.statistics['total_urls'],
        'errors': len(analyzer.errors),
        'warnings': len(analyzer.warnings)
    }

# Сводный отчет
print("\n" + "="*70)
print("СВОДНЫЙ ОТЧЕТ ПО ВСЕМ SITEMAP")
print("="*70)

for sitemap_url, stats in results.items():
    print(f"\n{sitemap_url}:")
    print(f"  • URL: {stats['total_urls']}")
    print(f"  • Ошибок: {stats['errors']}")
    print(f"  • Предупреждений: {stats['warnings']}")

print("\n")


# ============================================================================
# ПРИМЕР 5: Кастомная обработка результатов
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║         ПРИМЕР 5: Кастомная обработка результатов            ║
╚═══════════════════════════════════════════════════════════════╝
""")

analyzer5 = SitemapAnalyzer('https://example.com/sitemap.xml')
content = analyzer5.fetch_sitemap(analyzer5.sitemap_url)

if content:
    urls = analyzer5.parse_sitemap(content, analyzer5.sitemap_url)
    
    print(f"\nНайдено {len(urls)} URL")
    
    # Фильтрация только URL с определенным путем
    blog_urls = [u for u in urls if '/blog/' in u['loc']]
    print(f"URL блога: {len(blog_urls)}")
    
    # URL с priority > 0.8
    high_priority = [u for u in urls if u.get('priority') and float(u['priority']) > 0.8]
    print(f"Высокоприоритетных URL: {len(high_priority)}")
    
    # URL обновленные за последний месяц
    recent_urls = []
    for u in urls:
        if u.get('lastmod'):
            try:
                from datetime import datetime, timedelta
                lastmod = datetime.fromisoformat(u['lastmod'].replace('Z', '+00:00'))
                if lastmod > datetime.now(lastmod.tzinfo) - timedelta(days=30):
                    recent_urls.append(u)
            except:
                pass
    
    print(f"Обновленных за месяц: {len(recent_urls)}")
    
    # Экспорт в CSV
    import csv
    
    with open('sitemap_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['URL', 'Last Modified', 'Change Frequency', 'Priority'])
        
        for u in urls[:100]:  # Первые 100
            writer.writerow([
                u['loc'],
                u.get('lastmod', ''),
                u.get('changefreq', ''),
                u.get('priority', '')
            ])
    
    print("\n✅ Данные экспортированы в sitemap_export.csv")


# ============================================================================
# ПРИМЕР 6: Сравнение двух версий sitemap
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║            ПРИМЕР 6: Сравнение версий sitemap                 ║
╚═══════════════════════════════════════════════════════════════╝
""")

def compare_sitemaps(old_url: str, new_url: str):
    """Сравнение двух sitemap"""
    
    # Анализ старого
    old_analyzer = SitemapAnalyzer(old_url)
    old_content = old_analyzer.fetch_sitemap(old_url)
    old_urls = set(u['loc'] for u in old_analyzer.parse_sitemap(old_content, old_url))
    
    # Анализ нового
    new_analyzer = SitemapAnalyzer(new_url)
    new_content = new_analyzer.fetch_sitemap(new_url)
    new_urls = set(u['loc'] for u in new_analyzer.parse_sitemap(new_content, new_url))
    
    # Сравнение
    added = new_urls - old_urls
    removed = old_urls - new_urls
    unchanged = old_urls & new_urls
    
    print(f"\n📊 СРАВНЕНИЕ SITEMAP:")
    print(f"  • Старая версия: {len(old_urls)} URL")
    print(f"  • Новая версия: {len(new_urls)} URL")
    print(f"  • Добавлено: {len(added)} URL")
    print(f"  • Удалено: {len(removed)} URL")
    print(f"  • Без изменений: {len(unchanged)} URL")
    
    if added:
        print(f"\n➕ ДОБАВЛЕННЫЕ URL (первые 10):")
        for url in list(added)[:10]:
            print(f"    {url}")
    
    if removed:
        print(f"\n➖ УДАЛЕННЫЕ URL (первые 10):")
        for url in list(removed)[:10]:
            print(f"    {url}")
    
    return {
        'added': list(added),
        'removed': list(removed),
        'unchanged': list(unchanged)
    }

# Пример использования
# compare_sitemaps('https://example.com/old-sitemap.xml', 'https://example.com/new-sitemap.xml')


# ============================================================================
# ПРИМЕР 7: Мониторинг sitemap (запуск по расписанию)
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║         ПРИМЕР 7: Мониторинг sitemap (крон задача)           ║
╚═══════════════════════════════════════════════════════════════╝
""")

def monitor_sitemap(sitemap_url: str, alert_threshold: int = 10):
    """
    Мониторинг sitemap с уведомлениями
    Можно использовать в cron для ежедневной проверки
    """
    from datetime import datetime
    
    print(f"\n🔍 Мониторинг sitemap: {datetime.now()}")
    
    analyzer = SitemapAnalyzer(sitemap_url)
    analyzer.run(check_status=True)
    
    total_issues = len(analyzer.errors) + len(analyzer.warnings)
    
    # Логирование
    log_entry = f"{datetime.now()} | URL: {analyzer.statistics['total_urls']} | Issues: {total_issues}\n"
    
    with open('sitemap_monitor.log', 'a') as f:
        f.write(log_entry)
    
    # Алерт при превышении порога
    if total_issues > alert_threshold:
        alert_message = f"""
        ⚠️ АЛЕРТ: Обнаружено {total_issues} проблем в sitemap!
        
        Sitemap: {sitemap_url}
        Время: {datetime.now()}
        
        Критических ошибок: {len(analyzer.errors)}
        Предупреждений: {len(analyzer.warnings)}
        
        Требуется проверка!
        """
        
        print(alert_message)
        
        # Здесь можно добавить отправку email/telegram
        # send_alert_email(alert_message)
        # send_telegram_message(alert_message)
    else:
        print(f"✅ Проверка пройдена: {total_issues} проблем (< {alert_threshold})")
    
    return total_issues

# Пример использования
# monitor_sitemap('https://example.com/sitemap.xml', alert_threshold=10)


# ============================================================================
# ПРИМЕР 8: Генерация отчета в HTML
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║            ПРИМЕР 8: Генерация HTML отчета                    ║
╚═══════════════════════════════════════════════════════════════╝
""")

def generate_html_report(sitemap_url: str, output_file: str = 'sitemap_report.html'):
    """Генерация красивого HTML отчета"""
    
    analyzer = SitemapAnalyzer(sitemap_url)
    analyzer.run(check_status=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Sitemap Analysis Report</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                border-radius: 10px;
                margin-bottom: 20px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 20px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}
            .section {{
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .error {{ color: #e74c3c; }}
            .warning {{ color: #f39c12; }}
            .success {{ color: #27ae60; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔍 Sitemap Analysis Report</h1>
            <p>{sitemap_url}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{analyzer.statistics['total_urls']}</div>
                <div>Total URLs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{analyzer.statistics['domain_urls']}</div>
                <div>Domain URLs</div>
            </div>
            <div class="stat-card">
                <div class="stat-value error">{len(analyzer.errors)}</div>
                <div>Errors</div>
            </div>
            <div class="stat-card">
                <div class="stat-value warning">{len(analyzer.warnings)}</div>
                <div>Warnings</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Errors</h2>
            {'<br>'.join(f'<div class="error">❌ {e}</div>' for e in analyzer.errors) or '<p class="success">No errors found</p>'}
        </div>
        
        <div class="section">
            <h2>Warnings</h2>
            {'<br>'.join(f'<div class="warning">⚠️  {w}</div>' for w in analyzer.warnings[:50]) or '<p class="success">No warnings</p>'}
        </div>
    </body>
    </html>
    """
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ HTML отчет сохранен: {output_file}")

# Пример использования
# generate_html_report('https://example.com/sitemap.xml')


# ============================================================================
# ЗАКЛЮЧЕНИЕ
# ============================================================================

print("""
╔═══════════════════════════════════════════════════════════════╗
║                    ✅ ВСЕ ПРИМЕРЫ ГОТОВЫ                      ║
╚═══════════════════════════════════════════════════════════════╝

Доступные скрипты:

1. sitemap_analyzer.py - Базовый анализатор (консоль)
2. sitemap_analyzer_web.py - Веб-интерфейс (Flask)
3. sitemap_analyzer_pro.py - Расширенный SEO анализ
4. examples.py - Примеры использования (этот файл)

Для начала работы выполните:
    pip install requests flask beautifulsoup4 --break-system-packages
    python3 sitemap_analyzer.py

Документация: README.md
Автор: Alexander Garbuz (GARBUZ.ONLINE)
""")
