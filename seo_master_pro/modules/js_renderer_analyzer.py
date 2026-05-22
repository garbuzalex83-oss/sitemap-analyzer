"""
SEO Master PRO - Модуль JavaScript рендеринга и сравнения контента
Проверяет, как поисковые роботы видят интерактивный контент
Сравнивает HTML до и после рендеринга JavaScript
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class RenderIssueType(Enum):
    """Типы проблем с рендерингом"""
    CONTENT_MISSING = "content_missing"
    TITLE_CHANGED = "title_changed"
    DESCRIPTION_CHANGED = "description_changed"
    H1_CHANGED = "h1_changed"
    LINKS_MISSING = "links_missing"
    SCHEMA_MISSING = "schema_missing"
    CANONICAL_CHANGED = "canonical_changed"
    LAZY_CONTENT = "lazy_content"
    INFINITE_SCROLL = "infinite_scroll"
    SPA_ROUTING = "spa_routing"


@dataclass
class RenderIssue:
    """Проблема с рендерингом"""
    issue_type: RenderIssueType
    severity: str  # critical, high, medium, low
    message: str
    before_value: Optional[str]
    after_value: Optional[str]
    recommendation: str
    affected_elements: int = 0


@dataclass
class ContentDifference:
    """Разница в контенте"""
    element_type: str
    before: Optional[str]
    after: Optional[str]
    changed: bool
    added_content: List[str] = field(default_factory=list)
    removed_content: List[str] = field(default_factory=list)


class JavaScriptSEOAnalyzer:
    """
    Анализатор JavaScript рендеринга
    Сравнивает контент до и после выполнения JS
    """
    
    def __init__(self):
        self.issues: List[RenderIssue] = []
    
    def analyze_rendering(self, 
                         url: str,
                         html_before: str,
                         html_after: str,
                         wait_time: float = 3.0) -> Dict:
        """
        Анализирует различия между HTML до и после рендеринга
        
        Args:
            url: URL страницы
            html_before: Исходный HTML (до выполнения JS)
            html_after: HTML после рендеринга JavaScript
            wait_time: Время ожидания рендеринга (секунды)
            
        Returns:
            Dict с результатами анализа
        """
        self.issues = []
        
        # Извлечение элементов из обоих версий
        before_data = self._extract_content(html_before)
        after_data = self._extract_content(html_after)
        
        # Сравнение ключевых элементов
        differences = self._compare_content(before_data, after_data)
        
        # Проверка проблем рендеринга
        self._check_render_issues(url, before_data, after_data, differences)
        
        # Анализ количества контента
        content_analysis = self._analyze_content_volume(html_before, html_after)
        
        # Расчет SEO score для рендеринга
        render_score = self._calculate_render_score(differences, content_analysis)
        
        result = {
            'url': url,
            'wait_time': wait_time,
            'before_render': before_data,
            'after_render': after_data,
            'differences': [d.__dict__ for d in differences],
            'content_analysis': content_analysis,
            'issues': [i.__dict__ for i in self.issues],
            'render_seo_score': render_score,
            'googlebot_compatibility': self._assess_googlebot_compatibility(),
            'recommendations': self._generate_js_recommendations(),
        }
        
        return result
    
    def _extract_content(self, html: str) -> Dict:
        """Извлекает важный контент из HTML"""
        return {
            'title': self._extract_title(html),
            'description': self._extract_meta_description(html),
            'h1': self._extract_h1(html),
            'headings': self._extract_all_headings(html),
            'text_content': self._extract_text_content(html),
            'links': self._extract_links(html),
            'images': self._extract_images(html),
            'schema': self._extract_schema(html),
            'canonical': self._extract_canonical(html),
            'word_count': self._count_words(html),
            'html_size': len(html),
        }
    
    def _extract_title(self, html: str) -> Optional[str]:
        match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        return re.sub(r'\s+', ' ', match.group(1).strip()) if match else None
    
    def _extract_meta_description(self, html: str) -> Optional[str]:
        match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if not match:
            match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def _extract_h1(self, html: str) -> Optional[str]:
        match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
        return re.sub(r'\s+', ' ', match.group(1).strip()) if match else None
    
    def _extract_all_headings(self, html: str) -> Dict[str, List[str]]:
        headings = {f'h{i}': [] for i in range(1, 7)}
        for i in range(1, 7):
            pattern = f'<h{i}[^>]*>(.*?)</h{i}>'
            matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
            headings[f'h{i}'] = [re.sub(r'\s+', ' ', m.strip()) for m in matches]
        return headings
    
    def _extract_text_content(self, html: str) -> str:
        """Извлекает видимый текст из HTML"""
        # Удаляем скрипты и стили
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        # Удаляем HTML теги
        text = re.sub(r'<[^>]+>', ' ', text)
        # Очищаем пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000]  # Ограничиваем длину
    
    def _extract_links(self, html: str) -> List[Dict]:
        """Извлекает ссылки из HTML"""
        links = []
        pattern = r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>'
        matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
        
        for href, text in matches[:50]:  # Ограничиваем количество
            links.append({
                'href': href,
                'text': re.sub(r'\s+', ' ', text.strip())[:100],
                'is_internal': href.startswith('/') or 'http' not in href
            })
        
        return links
    
    def _extract_images(self, html: str) -> List[Dict]:
        """Извлекает изображения из HTML"""
        images = []
        pattern = r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for src in matches[:30]:
            images.append({
                'src': src,
                'has_alt': 'alt=' in html[html.find(src)-100:html.find(src)+len(src)+100],
            })
        
        return images
    
    def _extract_schema(self, html: str) -> List[str]:
        """Извлекает Schema.org разметку"""
        schemas = []
        
        # JSON-LD
        jsonld_pattern = r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>'
        matches = re.findall(jsonld_pattern, html, re.DOTALL)
        schemas.extend([f'JSON-LD: {m[:100]}...' for m in matches[:5]])
        
        # Microdata
        microdata_pattern = r'itemscope[^>]*itemtype=["\']([^"\']+)["\']'
        matches = re.findall(microdata_pattern, html, re.IGNORECASE)
        schemas.extend([f'Microdata: {m}' for m in matches[:5]])
        
        return schemas
    
    def _extract_canonical(self, html: str) -> Optional[str]:
        match = re.search(r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not match:
            match = re.search(r'<link[^>]*href=["\']([^"\']+)["\'][^>]*rel=["\']canonical["\']', html, re.IGNORECASE)
        return match.group(1) if match else None
    
    def _count_words(self, html: str) -> int:
        text = self._extract_text_content(html)
        return len(text.split())
    
    def _compare_content(self, before: Dict, after: Dict) -> List[ContentDifference]:
        """Сравнивает контент до и после рендеринга"""
        differences = []
        
        # Title
        title_changed = before['title'] != after['title']
        differences.append(ContentDifference(
            element_type='title',
            before=before['title'],
            after=after['title'],
            changed=title_changed
        ))
        
        # Description
        desc_changed = before['description'] != after['description']
        differences.append(ContentDifference(
            element_type='description',
            before=before['description'],
            after=after['description'],
            changed=desc_changed
        ))
        
        # H1
        h1_changed = before['h1'] != after['h1']
        differences.append(ContentDifference(
            element_type='h1',
            before=before['h1'],
            after=after['h1'],
            changed=h1_changed
        ))
        
        # Links count
        before_links = len(before['links'])
        after_links = len(after['links'])
        links_changed = before_links != after_links
        diff = ContentDifference(
            element_type='links',
            before=str(before_links),
            after=str(after_links),
            changed=links_changed
        )
        if after_links > before_links:
            diff.added_content = [l['href'] for l in after['links'] if l not in before['links']][:10]
        differences.append(diff)
        
        # Word count
        word_diff = after['word_count'] - before['word_count']
        content_changed = abs(word_diff) > 50
        differences.append(ContentDifference(
            element_type='word_count',
            before=str(before['word_count']),
            after=str(after['word_count']),
            changed=content_changed,
            added_content=[f'+{word_diff} слов'] if word_diff > 0 else [f'{word_diff} слов']
        ))
        
        # Schema
        schema_changed = before['schema'] != after['schema']
        differences.append(ContentDifference(
            element_type='schema',
            before=str(len(before['schema'])) + ' схем',
            after=str(len(after['schema'])) + ' схем',
            changed=schema_changed
        ))
        
        return differences
    
    def _check_render_issues(self, url: str, before: Dict, after: Dict, differences: List[ContentDifference]):
        """Проверяет проблемы рендеринга"""
        
        for diff in differences:
            if diff.element_type == 'title' and diff.changed:
                severity = 'high' if not after['title'] else 'medium'
                self.issues.append(RenderIssue(
                    issue_type=RenderIssueType.TITLE_CHANGED,
                    severity=severity,
                    message=f"Title изменился после рендеринга JS",
                    before_value=diff.before,
                    after_value=diff.after,
                    recommendation="Убедитесь, что Title доступен в исходном HTML или быстро рендерится через JS."
                ))
            
            elif diff.element_type == 'description' and diff.changed:
                if not after['description'] and before['description']:
                    self.issues.append(RenderIssue(
                        issue_type=RenderIssueType.CONTENT_MISSING,
                        severity='high',
                        message="Description исчез после рендеринга JS",
                        before_value=diff.before,
                        after_value=diff.after,
                        recommendation="Проверьте, не удаляется ли Description при загрузке JS."
                    ))
            
            elif diff.element_type == 'h1' and diff.changed:
                if not after['h1'] and before['h1']:
                    self.issues.append(RenderIssue(
                        issue_type=RenderIssueType.H1_CHANGED,
                        severity='critical',
                        message="H1 исчез после рендеринга JS",
                        before_value=diff.before,
                        after_value=diff.after,
                        recommendation="Критическая проблема! H1 должен быть доступен сразу или быстро рендериться."
                    ))
            
            elif diff.element_type == 'links' and diff.changed:
                if len(after.get('added_content', [])) > 10:
                    self.issues.append(RenderIssue(
                        issue_type=RenderIssueType.LINKS_MISSING,
                        severity='medium',
                        message=f"Найдено {len(after.get('added_content', []))} ссылок, загружаемых через JS",
                        before_value=diff.before,
                        after_value=diff.after,
                        recommendation="Важные ссылки должны быть в HTML. Google может не индексировать JS-ссылки."
                    ))
            
            elif diff.element_type == 'word_count' and diff.changed:
                word_diff = after['word_count'] - before['word_count']
                if word_diff > 500:
                    self.issues.append(RenderIssue(
                        issue_type=RenderIssueType.LAZY_CONTENT,
                        severity='medium',
                        message=f"Большой объем контента ({word_diff} слов) загружается через JS",
                        before_value=diff.before,
                        after_value=diff.after,
                        recommendation="Основной контент должен быть в HTML. JS-контент индексируется с задержкой."
                    ))
            
            elif diff.element_type == 'schema' and diff.changed:
                if len(after['schema']) > len(before['schema']):
                    self.issues.append(RenderIssue(
                        issue_type=RenderIssueType.SCHEMA_MISSING,
                        severity='medium',
                        message=f"Schema.org разметка добавляется через JS ({len(after['schema']) - len(before['schema'])} схем)",
                        before_value=diff.before,
                        after_value=diff.after,
                        recommendation="Добавьте Schema.org разметку в серверный HTML для быстрой индексации."
                    ))
        
        # Проверка canonical
        if before['canonical'] != after['canonical']:
            self.issues.append(RenderIssue(
                issue_type=RenderIssueType.CANONICAL_CHANGED,
                severity='high',
                message="Canonical URL изменился после рендеринга JS",
                before_value=before['canonical'],
                after_value=after['canonical'],
                recommendation="Canonical должен быть в исходном HTML. JS-изменения могут игнорироваться."
            ))
    
    def _analyze_content_volume(self, html_before: str, html_after: str) -> Dict:
        """Анализирует изменения объема контента"""
        before_text = self._extract_text_content(html_before)
        after_text = self._extract_text_content(html_after)
        
        before_words = len(before_text.split())
        after_words = len(after_text.split())
        
        return {
            'html_size_before': len(html_before),
            'html_size_after': len(html_after),
            'html_size_diff': len(html_after) - len(html_before),
            'word_count_before': before_words,
            'word_count_after': after_words,
            'word_count_diff': after_words - before_words,
            'content_load_percentage': round((after_words / before_words * 100) if before_words > 0 else 0, 1),
            'js_heavy': len(html_after) > len(html_before) * 1.5,
        }
    
    def _calculate_render_score(self, differences: List[ContentDifference], content_analysis: Dict) -> int:
        """Рассчитывает оценку качества рендеринга (0-100)"""
        score = 100
        
        # Штрафы за изменения
        for diff in differences:
            if diff.element_type == 'title' and diff.changed:
                score -= 15
            elif diff.element_type == 'h1' and diff.changed:
                score -= 25
            elif diff.element_type == 'description' and diff.changed:
                score -= 10
            elif diff.element_type == 'links' and diff.changed:
                score -= 5
            elif diff.element_type == 'word_count' and diff.changed:
                word_diff = abs(content_analysis['word_count_diff'])
                if word_diff > 500:
                    score -= 15
                elif word_diff > 200:
                    score -= 10
        
        # Штраф за тяжелый JS
        if content_analysis.get('js_heavy'):
            score -= 10
        
        return max(score, 0)
    
    def _assess_googlebot_compatibility(self) -> Dict:
        """Оценивает совместимость с Googlebot"""
        critical_issues = [i for i in self.issues if i.severity == 'critical']
        high_issues = [i for i in self.issues if i.severity == 'high']
        
        if critical_issues:
            compatibility = 'poor'
            message = "Googlebot может не увидеть важный контент"
        elif high_issues:
            compatibility = 'fair'
            message = "Есть проблемы, которые могут повлиять на индексацию"
        elif self.issues:
            compatibility = 'good'
            message = "Небольшие проблемы, но в целом совместимо"
        else:
            compatibility = 'excellent'
            message = "Отличная совместимость с Googlebot"
        
        return {
            'level': compatibility,
            'message': message,
            'critical_issues_count': len(critical_issues),
            'high_issues_count': len(high_issues),
            'total_issues_count': len(self.issues)
        }
    
    def _generate_js_recommendations(self) -> List[Dict]:
        """Генерирует рекомендации по улучшению JS рендеринга"""
        recommendations = []
        
        # Общие рекомендации
        if any(i.issue_type == RenderIssueType.CONTENT_MISSING for i in self.issues):
            recommendations.append({
                'priority': 'critical',
                'title': 'Реализуйте SSR (Server-Side Rendering)',
                'description': 'Основной контент должен отдаваться сервером. Используйте Next.js, Nuxt.js или аналогичные фреймворки.',
                'impact': 'Высокое влияние на индексацию'
            })
        
        if any(i.issue_type in [RenderIssueType.TITLE_CHANGED, RenderIssueType.H1_CHANGED] for i in self.issues):
            recommendations.append({
                'priority': 'high',
                'title': 'Добавьте критический контент в HTML',
                'description': 'Title, H1 и мета-теги должны присутствовать в исходном HTML ответе сервера.',
                'impact': 'Критично для SEO'
            })
        
        if any(i.issue_type == RenderIssueType.LAZY_CONTENT for i in self.issues):
            recommendations.append({
                'priority': 'medium',
                'title': 'Оптимизируйте загрузку контента',
                'description': 'Используйте динамический импорт только для второстепенного контента. Основной текст должен быть сразу доступен.',
                'impact': 'Среднее влияние на скорость индексации'
            })
        
        if any(i.issue_type == RenderIssueType.SCHEMA_MISSING for i in self.issues):
            recommendations.append({
                'priority': 'medium',
                'title': 'Добавьте Schema.org в серверный HTML',
                'description': 'Микроразметка должна быть в исходном HTML для быстрой обработки поисковыми роботами.',
                'impact': 'Влияет на расширенные сниппеты'
            })
        
        if not recommendations:
            recommendations.append({
                'priority': 'low',
                'title': 'Продолжайте мониторинг',
                'description': 'Текущая реализация хороша. Регулярно проверяйте изменения после обновлений.',
                'impact': 'Профилактическая мера'
            })
        
        return recommendations
    
    def simulate_googlebot_view(self, html_after: str) -> Dict:
        """
        Симулирует представление страницы глазами Googlebot
        
        Returns:
            Dict с тем, что "видит" Googlebot
        """
        return {
            'title': self._extract_title(html_after),
            'description': self._extract_meta_description(html_after),
            'h1': self._extract_h1(html_after),
            'main_content_preview': self._extract_text_content(html_after)[:500] + '...',
            'links_count': len(self._extract_links(html_after)),
            'images_count': len(self._extract_images(html_after)),
            'schema_types': self._extract_schema(html_after),
            'canonical': self._extract_canonical(html_after),
            'word_count': self._count_words(html_after),
            'indexable': self._is_indexable(html_after),
        }
    
    def _is_indexable(self, html: str) -> bool:
        """Проверяет, может ли страница быть проиндексирована"""
        # Проверка на noindex
        noindex_pattern = r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'][^"\']*noindex'
        if re.search(noindex_pattern, html, re.IGNORECASE):
            return False
        
        # Проверка на X-Robots-Tag (в meta)
        xrobots_pattern = r'<meta[^>]*http-equiv=["\']x-robots-tag["\'][^>]*content=["\'][^"\']*noindex'
        if re.search(xrobots_pattern, html, re.IGNORECASE):
            return False
        
        return True


# Пример использования
if __name__ == "__main__":
    # HTML до рендеринга (серверный)
    html_before = """
    <html>
    <head>
        <title>Загрузка...</title>
        <meta name="description" content="">
    </head>
    <body>
        <div id="app">
            <div class="loading">Загрузка контента...</div>
        </div>
    </body>
    </html>
    """
    
    # HTML после рендеринга (клиентский)
    html_after = """
    <html>
    <head>
        <title>Купить кроссовки Nike Air Max - лучшие цены | SportStore</title>
        <meta name="description" content="Широкий выбор кроссовок Nike Air Max. Оригинальная продукция, гарантия качества, быстрая доставка.">
        <script type="application/ld+json">
        {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": "Nike Air Max",
            "offers": {"price": "12990", "currency": "RUB"}
        }
        </script>
    </head>
    <body>
        <div id="app">
            <h1>Кроссовки Nike Air Max</h1>
            <p>Легендарные кроссовки Nike Air Max сочетают в себе стиль и комфорт...</p>
            <h2>Характеристики</h2>
            <p>Материал: текстиль, подошва: резина...</p>
            <h2>Отзывы</h2>
            <div class="reviews">
                <p>Отличный товар! (127 отзывов)</p>
            </div>
            <a href="/catalog/nike">Все товары Nike</a>
            <a href="/delivery">Доставка</a>
            <a href="/payment">Оплата</a>
        </div>
    </body>
    </html>
    """
    
    analyzer = JavaScriptSEOAnalyzer()
    result = analyzer.analyze_rendering(
        url="https://example.com/product/nike-air-max",
        html_before=html_before,
        html_after=html_after,
        wait_time=3.0
    )
    
    print("=" * 80)
    print("АНАЛИЗ JAVASCRIPT РЕНДЕРИНГА")
    print("=" * 80)
    print(f"URL: {result['url']}")
    print(f"Время ожидания: {result['wait_time']} сек")
    print(f"\nSEO оценка рендеринга: {result['render_seo_score']}/100")
    
    print(f"\nСовместимость с Googlebot: {result['googlebot_compatibility']['level']}")
    print(f"  Сообщение: {result['googlebot_compatibility']['message']}")
    print(f"  Критических проблем: {result['googlebot_compatibility']['critical_issues_count']}")
    print(f"  Серьезных проблем: {result['googlebot_compatibility']['high_issues_count']}")
    
    print("\n" + "=" * 80)
    print("РАЗЛИЧИЯ ДО/ПОСЛЕ РЕНДЕРИНГА:")
    print("=" * 80)
    for diff in result['differences']:
        status = "⚠️ ИЗМЕНЕНО" if diff['changed'] else "✓ Без изменений"
        print(f"\n{status} {diff['element_type'].upper()}")
        print(f"  До: {diff['before']}")
        print(f"  После: {diff['after']}")
        if diff.get('added_content'):
            print(f"  Добавлено: {diff['added_content'][:3]}")
    
    print("\n" + "=" * 80)
    print("АНАЛИЗ КОНТЕНТА:")
    print("=" * 80)
    ca = result['content_analysis']
    print(f"Размер HTML: {ca['html_size_before']} → {ca['html_size_after']} байт ({ca['html_size_diff']:+})")
    print(f"Количество слов: {ca['word_count_before']} → {ca['word_count_after']} ({ca['word_count_diff']:+})")
    print(f"Загружено через JS: {ca['content_load_percentage']}%")
    print(f"Тяжелый JS: {'Да ⚠️' if ca['js_heavy'] else 'Нет'}")
    
    if result['issues']:
        print("\n" + "=" * 80)
        print("ПРОБЛЕМЫ РЕНДЕРИНГА:")
        print("=" * 80)
        for issue in result['issues']:
            print(f"\n[{issue['severity'].upper()}] {issue['issue_type'].value}")
            print(f"  Проблема: {issue['message']}")
            print(f"  До: {issue['before_value']}")
            print(f"  После: {issue['after_value']}")
            print(f"  Решение: {issue['recommendation']}")
    
    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    for rec in result['recommendations']:
        print(f"\n[{rec['priority'].upper()}] {rec['title']}")
        print(f"  {rec['description']}")
        print(f"  Влияние: {rec['impact']}")
    
    # Симуляция вида Googlebot
    print("\n" + "=" * 80)
    print("КАК ВИДИТ СТРАНИЦУ GOOGLEBOT:")
    print("=" * 80)
    bot_view = analyzer.simulate_googlebot_view(html_after)
    print(f"Title: {bot_view['title']}")
    print(f"Description: {bot_view['description']}")
    print(f"H1: {bot_view['h1']}")
    print(f"Слов: {bot_view['word_count']}")
    print(f"Ссылок: {bot_view['links_count']}")
    print(f"Изображений: {bot_view['images_count']}")
    print(f"Schema: {bot_view['schema_types']}")
    print(f"Может индексироваться: {'Да ✓' if bot_view['indexable'] else 'Нет ✗'}")
