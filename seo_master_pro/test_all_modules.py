#!/usr/bin/env python3
"""
Тестовый скрипт для проверки всех модулей SEO Master PRO
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

def create_test_html():
    """Создает тестовую HTML страницу для проверки"""
    test_html = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Купить кроссовки в Молдове | Sportlandia</title>
    <meta name="description" content="Лучшие кроссовки для бега и спорта. Широкий выбор брендов: Adidas, Nike, Puma. Доставка по Кишиневу и всей Молдове.">
    <link rel="canonical" href="https://sportlandia.md/krossovki/">
    
    <!-- Schema.org Product -->
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": "Кроссовки Adidas Ultraboost",
        "brand": "Adidas",
        "offers": {
            "@type": "Offer",
            "price": "2499",
            "priceCurrency": "MDL",
            "availability": "https://schema.org/InStock"
        }
    }
    </script>
    
    <!-- Open Graph -->
    <meta property="og:title" content="Кроссовки Adidas - Sportlandia">
    <meta property="og:description" content="Премиум кроссовки для бега">
    <meta property="og:image" content="https://sportlandia.md/images/adidas-ultraboost.jpg">
    <meta property="og:type" content="product">
</head>
<body>
    <header>
        <nav>
            <a href="/">Главная</a>
            <a href="/krossovki/">Кроссовки</a>
            <a href="/odezhda/">Одежда</a>
            <a href="/kontakty/">Контакты</a>
        </nav>
    </header>
    
    <main>
        <h1>Кроссовки для бега в Молдове</h1>
        
        <div class="breadcrumbs">
            <a href="/">Главная</a> / <span>Кроссовки</span>
        </div>
        
        <section class="product-card">
            <img src="/images/adidas-1.jpg" alt="Кроссовки Adidas Ultraboost белые" width="400" height="300">
            <h2>Adidas Ultraboost 22</h2>
            <p class="price">2499 MDL</p>
            <p class="availability">В наличии</p>
            <button class="buy-button">Купить</button>
            <button class="cart-button">В корзину</button>
            
            <div class="product-details">
                <h3>Характеристики</h3>
                <ul>
                    <li>Бренд: Adidas</li>
                    <li>Тип: Беговые</li>
                    <li>Пол: Мужские</li>
                    <li>Цвет: Белый</li>
                </ul>
            </div>
            
            <div class="delivery-info">
                <h3>Доставка и оплата</h3>
                <p>Бесплатная доставка при заказе от 1000 MDL</p>
                <p>Оплата наличными или картой</p>
                <p>Возврат в течение 14 дней</p>
            </div>
        </section>
        
        <section class="seo-text">
            <h2>Как выбрать кроссовки для бега?</h2>
            <p>При выборе беговых кроссовок важно учитывать тип пронации, покрытие и дистанцию...</p>
            
            <h3>Популярные бренды</h3>
            <p>В нашем магазине представлены Adidas, Nike, Puma, Reebok и другие известные бренды.</p>
        </section>
        
        <section class="faq">
            <h2>Частые вопросы</h2>
            <div class="faq-item">
                <h4>Есть ли гарантия на кроссовки?</h4>
                <p>Да, мы предоставляем гарантию 30 дней на производственные дефекты.</p>
            </div>
            <div class="faq-item">
                <h4>Как определить размер?</h4>
                <p>Используйте нашу таблицу размеров или проконсультируйтесь с менеджером.</p>
            </div>
        </section>
    </main>
    
    <footer>
        <div class="contacts">
            <h3>Контакты</h3>
            <p>Адрес: г. Кишинев, ул. Штефан чел Маре 100</p>
            <p>Телефон: +373 22 123 456</p>
            <p>Email: info@sportlandia.md</p>
            <p>График работы: Пн-Вс 9:00-21:00</p>
        </div>
        <div class="company-info">
            <p>ООО "Sportlandia Moldova"</p>
            <p>IDNO: 123456789</p>
        </div>
    </footer>
    
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Страница загружена');
        });
    </script>
</body>
</html>'''
    
    os.makedirs('test_site', exist_ok=True)
    with open('test_site/test_page.html', 'w', encoding='utf-8') as f:
        f.write(test_html)
    
    return 'test_site/test_page.html'


def test_meta_auditor():
    """Тестирует модуль аудита мета-тегов"""
    print("\n" + "="*60)
    print("🔵 ТЕСТ 1: Meta Auditor (Мета-теги и сниппеты)")
    print("="*60)
    
    try:
        from modules.meta_auditor import MetaTagsAuditor
        
        # Читаем HTML файл
        with open('test_site/test_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        auditor = MetaTagsAuditor()
        results = auditor.analyze_page(
            url='https://sportlandia.md/krossovki/',
            html=html_content,
            page_type='category'
        )
        
        print(f"\n✅ Title: {results.get('title', {}).get('content', 'N/A')[:60]}...")
        print(f"✅ Description: {results.get('description', {}).get('content', 'N/A')[:60]}...")
        print(f"✅ H1: {results.get('headings', {}).get('h1', ['N/A'])[0]}")
        print(f"✅ Canonical: {results.get('canonical', 'N/A')}")
        
        # Показываем превью сниппета
        snippet = auditor.generate_snippet_preview(
            results.get('title', {}).get('content', ''),
            results.get('description', {}).get('content', ''),
            'https://sportlandia.md/krossovki/'
        )
        print(f"\n📄 ПРЕВЬЮ СНИППЕТА GOOGLE:")
        print(snippet)
        
        print("\n✅ Meta Auditor работает корректно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка Meta Auditor: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_commercial_auditor():
    """Тестирует модуль коммерческих факторов"""
    print("\n" + "="*60)
    print("🔵 ТЕСТ 2: Commercial Auditor (Коммерческие факторы)")
    print("="*60)
    
    try:
        from modules.commercial_auditor import CommercialFactorsAuditor
        
        # Читаем HTML файл
        with open('test_site/test_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        auditor = CommercialFactorsAuditor()
        results = auditor.analyze_page(
            url='https://sportlandia.md/krossovki/',
            html=html_content,
            page_type='category'
        )
        
        score = results.get('overall_score', 0)
        factors = results.get('factors', {})
        
        print(f"\n📊 ОБЩАЯ ОЦЕНКА: {score}/100")
        print(f"\nПроверенные факторы:")
        for factor_id, data in factors.items():
            status = "✅" if data.get('present') else "❌"
            print(f"  {status} {data.get('name', factor_id)}: {'Найдено' if data.get('present') else 'Не найдено'}")
        
        print("\n✅ Commercial Auditor работает корректно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка Commercial Auditor: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_js_renderer():
    """Тестирует модуль JS рендеринга"""
    print("\n" + "="*60)
    print("🔵 ТЕСТ 3: JS Renderer Analyzer (JavaScript рендеринг)")
    print("="*60)
    
    try:
        from modules.js_renderer_analyzer import JavaScriptSEOAnalyzer
        
        # Читаем HTML файл (используем как "до" и "после" рендера для теста)
        with open('test_site/test_page.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        analyzer = JavaScriptSEOAnalyzer()
        
        # Для простого теста используем одинаковый HTML до и после
        results = analyzer.analyze_rendering(
            url='https://sportlandia.md/krossovki/',
            html_before=html_content,
            html_after=html_content,
            wait_time=1.0
        )
        
        print(f"\n📊 JS Совместимость: {results.get('js_compatibility_score', 0)}/100")
        print(f"✅ Найдено скриптов: {len(results.get('scripts', []))}")
        print(f"✅ Проблемы рендеринга: {len(results.get('rendering_issues', []))}")
        
        if results.get('googlebot_compatibility'):
            print("\n✅ Страница совместима с Googlebot!")
        else:
            print("\n⚠️ Возможны проблемы с индексацией JS-контента")
        
        print("\n✅ JS Renderer Analyzer работает корректно!")
        return True
    except Exception as e:
        print(f"❌ Ошибка JS Renderer Analyzer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_report_builder():
    """Тестирует конструктор отчетов"""
    print("\n" + "="*60)
    print("🔵 ТЕСТ 4: Report Builder (Конструктор отчетов)")
    print("="*60)
    
    try:
        from modules.report_builder import ReportBuilder
        
        builder = ReportBuilder()
        
        # Показываем доступные шаблоны
        templates = builder.list_templates()
        print(f"\n✅ Доступные шаблоны: {[t['name'] for t in templates]}")
        
        # Создаем тестовые данные в правильном формате
        audit_data = {
            'url': 'https://sportlandia.md/krossovki/',
            'audit_date': '2024-01-15',
            'scores': {
                'meta_score': 85,
                'commercial_score': 77,
                'trust_score': 90,
                'js_score': 100,
                'overall_score': 88,
            },
            'issues': [
                {'priority': 'High', 'category': 'Meta', 'description': 'Title слишком короткий'},
                {'priority': 'Medium', 'category': 'Commercial', 'description': 'Отсутствует блок отзывов'},
            ],
            'recommendations': [
                'Увеличить длину Title до 50-60 символов',
                'Добавить блок с отзывами покупателей',
                'Добавить FAQPage разметку',
            ]
        }
        
        # Брендирование
        branding = {
            'brand_name': 'Sportlandia SEO',
            'brand_color': '#2563eb'
        }
        
        # Генерируем отчет используя правильный метод и параметры
        result = builder.generate_report(
            template_id='full_report',  # Используем существующий шаблон
            audit_data=audit_data,
            branding=branding
        )
        
        # Экспортируем в HTML (метод возвращает HTML строку)
        html_content = builder.export_to_html(result)
        
        # Сохраняем в файл
        report_filename = f"reports/test_report_{result.get('report_id', 'unknown')}.html"
        os.makedirs('reports', exist_ok=True)
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ Отчет создан: {report_filename}")
        print(f"✅ Шаблон: full_report")
        print(f"✅ Формат: HTML")
        
        # Проверяем существование файла
        if os.path.exists(report_filename):
            file_size = os.path.getsize(report_filename)
            print(f"✅ Размер файла: {file_size:,} байт")
            print("\n✅ Report Builder работает корректно!")
            return True
        else:
            print("❌ Файл отчета не создан")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка Report Builder: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Запускает все тесты"""
    print("\n" + "🚀"*30)
    print("🚀 SEO MASTER PRO - ТЕСТИРОВАНИЕ ВСЕХ МОДУЛЕЙ")
    print("🚀"*30)
    
    # Создаем тестовую страницу
    print("\n📄 Создание тестовой страницы...")
    test_file = create_test_html()
    print(f"✅ Тестовая страница создана: {test_file}")
    
    # Запускаем тесты
    results = {
        'Meta Auditor': test_meta_auditor(),
        'Commercial Auditor': test_commercial_auditor(),
        'JS Renderer': test_js_renderer(),
        'Report Builder': test_report_builder(),
    }
    
    # Итоговый отчет
    print("\n" + "="*60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ ПО ТЕСТИРОВАНИЮ")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for module, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {module}")
    
    print(f"\n🎯 Пройдено тестов: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ВСЕ МОДУЛИ РАБОТАЮТ КОРРЕКТНО!")
        print("\n💡 Как использовать:")
        print("   python seo_master_pro.py https://example.com")
        print("\n📁 Отчеты сохраняются в папку: reports/")
    else:
        print("\n⚠️ Некоторые модули требуют внимания")
        sys.exit(1)


if __name__ == '__main__':
    main()
