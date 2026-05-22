#!/usr/bin/env python3
"""
SEO Master PRO - Профессиональная система SEO аудита уровня Enterprise
Запуск всех модулей и генерация комплексного отчета
"""

import sys
import json
from datetime import datetime
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent))

from modules.meta_auditor import MetaTagsAuditor
from modules.commercial_auditor import CommercialFactorsAuditor
from modules.js_renderer_analyzer import JavaScriptSEOAnalyzer
from modules.report_builder import ReportBuilder


def analyze_url(url: str, html_content: str, page_type: str = 'product') -> dict:
    """
    Проводит полный SEO анализ страницы
    
    Args:
        url: URL страницы
        html_content: HTML контент
        page_type: Тип страницы (product, category, homepage, article)
    
    Returns:
        Dict с результатами всех аудитов
    """
    print("=" * 80)
    print(f"SEO MASTER PRO - АНАЛИЗ СТРАНИЦЫ")
    print("=" * 80)
    print(f"URL: {url}")
    print(f"Тип: {page_type}")
    print(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    print("=" * 80)
    
    results = {
        'url': url,
        'page_type': page_type,
        'analyzed_at': datetime.now().isoformat()
    }
    
    # 1. Анализ мета-тегов
    print("\n[1/4] АНАЛИЗ МЕТА-ТЕГОВ...")
    meta_auditor = MetaTagsAuditor()
    meta_results = meta_auditor.analyze_page(url, html_content, page_type)
    results['meta_tags'] = meta_results
    
    snippet = meta_auditor.generate_snippet_preview(
        meta_results['title']['value'],
        meta_results['description']['value'],
        url
    )
    results['snippet'] = snippet
    
    print(f"  ✓ Title: {meta_results['title']['length']} символов ({meta_results['title']['status']})")
    print(f"  ✓ Description: {meta_results['description']['length']} символов ({meta_results['description']['status']})")
    print(f"  ✓ H1: {len(meta_results['headings'].get('h1', []))} найдено")
    print(f"  ✓ Оценка структуры: {meta_results['structure_score']}/100")
    print(f"  ✓ Проблем: {meta_results['total_issues']} (Critical: {meta_results['critical_count']})")
    
    # 2. Анализ коммерческих факторов
    print("\n[2/4] АНАЛИЗ КОММЕРЧЕСКИХ ФАКТОРОВ...")
    commercial_auditor = CommercialFactorsAuditor()
    commercial_results = commercial_auditor.analyze_page(url, html_content, page_type)
    results['commercial'] = commercial_results
    
    print(f"  ✓ Коммерческая оценка: {commercial_results['commercial_score']}/100")
    print(f"  ✓ Оценка доверия: {commercial_results['trust_score']}/100")
    print(f"  ✓ Найдено элементов: {commercial_results['total_elements']}")
    print(f"  ✓ Готовность к конверсии: {commercial_results['conversion_readiness']}")
    print(f"  ✓ Проблем: {commercial_results['critical_issues']} критических")
    
    # 3. Анализ JavaScript рендеринга (симуляция)
    print("\n[3/4] АНАЛИЗ JAVASCRIPT РЕНДЕРИНГА...")
    js_analyzer = JavaScriptSEOAnalyzer()
    
    # Для демонстрации используем тот же HTML как "после рендеринга"
    # В реальности здесь нужно использовать Playwright/Selenium
    js_results = js_analyzer.analyze_rendering(
        url=url,
        html_before=html_content,  # В реальности - исходный HTML сервера
        html_after=html_content,   # В реальности - HTML после выполнения JS
        wait_time=3.0
    )
    results['javascript'] = js_results
    
    print(f"  ✓ SEO оценка рендеринга: {js_results['render_seo_score']}/100")
    print(f"  ✓ Совместимость с Googlebot: {js_results['googlebot_compatibility']['level']}")
    print(f"  ✓ Проблем: {len(js_results['issues'])}")
    
    # 4. Генерация отчета
    print("\n[4/4] ГЕНЕРАЦИЯ ОТЧЕТА...")
    report_builder = ReportBuilder()
    
    # Добавляем данные crawl (заглушка для примера)
    results['crawl'] = {
        'seo_score': 75,
        'total_pages': 1,
        'indexed_pages': 1,
        'issues': [],
        'total_issues': 0,
        'critical_count': 0
    }
    
    # Генерируем полный отчет
    report = report_builder.generate_report(
        template_id='full_report',
        audit_data=results,
        branding={
            'company_name': 'SEO Master PRO',
            'contact_info': 'professional SEO audit tool',
            'logo': ''
        }
    )
    
    print(f"  ✓ Отчет сгенерирован: {report['report_id']}")
    print(f"  ✓ Секций: {len(report['sections'])}")
    print(f"  ✓ Общая оценка: {report['overall_score']}/100")
    print(f"  ✓ Статус: {report['summary']['status_text']}")
    
    # Сохраняем отчеты
    reports_dir = Path(__file__).parent / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # HTML отчет
    html_report = report_builder.export_to_html(report)
    html_path = reports_dir / f'seo_report_{timestamp}.html'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_report)
    print(f"\n  📄 HTML отчет сохранен: {html_path}")
    
    # JSON отчет
    json_report = report_builder.export_to_json(report)
    json_path = reports_dir / f'seo_report_{timestamp}.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_report)
    print(f"  📊 JSON отчет сохранен: {json_path}")
    
    # Вывод резюме
    print("\n" + "=" * 80)
    print("РЕЗЮМЕ АУДИТА")
    print("=" * 80)
    
    overall_score = report['overall_score']
    if overall_score >= 80:
        grade = 'ОТЛИЧНО'
        color = '🟢'
    elif overall_score >= 60:
        grade = 'ХОРОШО'
        color = '🔵'
    elif overall_score >= 40:
        grade = 'ТРЕБУЕТ УЛУЧШЕНИЙ'
        color = '🟡'
    else:
        grade = 'КРИТИЧЕСКОЕ СОСТОЯНИЕ'
        color = '🔴'
    
    print(f"\n{color} ОБЩАЯ ОЦЕНКА: {overall_score}/100 - {grade}")
    
    print(f"\n📊 Оценки по категориям:")
    print(f"  • Мета-теги: {results['meta_tags']['structure_score']}/100")
    print(f"  • Коммерческие факторы: {results['commercial']['commercial_score']}/100")
    print(f"  • Доверие: {results['commercial']['trust_score']}/100")
    print(f"  • JS Рендеринг: {results['javascript']['render_seo_score']}/100")
    
    total_issues = (
        results['meta_tags']['total_issues'] +
        results['commercial'].get('total_issues', 0) +
        results['javascript'].get('total_issues', 0)
    )
    
    critical_issues = (
        results['meta_tags']['critical_count'] +
        results['commercial'].get('critical_count', 0) +
        len([i for i in results['javascript']['issues'] if i.get('severity') == 'critical'])
    )
    
    print(f"\n⚠️ Всего проблем: {total_issues}")
    print(f"  🔴 Критических: {critical_issues}")
    
    if critical_issues > 0:
        print(f"\n❗ ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ!")
    
    print("\n" + "=" * 80)
    print("Аудит завершен успешно!")
    print("=" * 80)
    
    return results


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("SEO Master PRO - Профессиональный SEO аудит")
        print("\nИспользование:")
        print("  python seo_master_pro.py <URL> [page_type]")
        print("\nПримеры:")
        print("  python seo_master_pro.py https://example.com/product product")
        print("  python seo_master_pro.py https://example.com/category category")
        print("  python seo_master_pro.py https://example.com homepage")
        print("\nТипы страниц: product, category, homepage, article, brand, tag")
        sys.exit(1)
    
    url = sys.argv[1]
    page_type = sys.argv[2] if len(sys.argv) > 2 else 'product'
    
    # Для демонстрации используем тестовый HTML
    # В реальности здесь будет загрузка страницы через requests/Playwright
    test_html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Купить кроссовки Nike Air Max в Москве - лучшие цены | SportStore</title>
        <meta name="description" content="Широкий выбор кроссовок Nike Air Max в Москве. Оригинальная продукция, гарантия качества, быстрая доставка. Закажите онлайн!">
        <link rel="canonical" href="https://example.com/product/nike-air-max">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Nike Air Max",
            "image": "https://example.com/nike.jpg",
            "offers": {
                "@type": "Offer",
                "price": "12990",
                "priceCurrency": "RUB",
                "availability": "https://schema.org/InStock"
            }
        }
        </script>
    </head>
    <body>
        <header>
            <a href="tel:+74951234567">+7 (495) 123-45-67</a>
            <nav>
                <a href="/cart">Корзина <span class="cart-count">(3)</span></a>
            </nav>
        </header>
        
        <main>
            <h1>Кроссовки Nike Air Max</h1>
            
            <div class="product-info">
                <span class="price">12 990 ₽</span>
                <span class="availability" data-availability="in-stock">В наличии</span>
                <span class="sku">Артикул: NK-AM-001</span>
                <span data-brand="Nike">Nike</span>
            </div>
            
            <button class="btn-buy" data-action="buy">Купить</button>
            <button class="btn-cart" data-action="add-to-cart">В корзину</button>
            
            <section class="description">
                <h2>Описание</h2>
                <p>Легендарные кроссовки Nike Air Max сочетают в себе стиль и комфорт...</p>
            </section>
            
            <section class="specifications">
                <h2>Характеристики</h2>
                <table>
                    <tr><th>Материал</th><td>Текстиль</td></tr>
                    <tr><th>Цвет</th><td>Белый/Черный</td></tr>
                    <tr><th>Размер</th><td>38-46</td></tr>
                </table>
            </section>
            
            <section class="delivery-info">
                <h2>Доставка</h2>
                <p>Бесплатная доставка при заказе от 5000 ₽</p>
                <p>Доставка по Москве 1-2 дня</p>
            </section>
            
            <section class="payment-methods">
                <h2>Оплата</h2>
                <p>Наличные, картой, Visa, Mastercard</p>
            </section>
            
            <section class="reviews">
                <h2>Отзывы</h2>
                <span class="rating" data-rating="4.5">★★★★☆</span>
                <p>Отзывы (127)</p>
            </section>
            
            <section class="trust-badges">
                <span>🔒 Безопасная оплата</span>
                <span>✓ Гарантия качества</span>
                <span>↩ Возврат 30 дней</span>
            </section>
        </main>
        
        <footer>
            <p>© 2024 SportStore. Все права защищены.</p>
        </footer>
    </body>
    </html>
    """
    
    try:
        results = analyze_url(url, test_html, page_type)
        return 0
    except Exception as e:
        print(f"\n❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
